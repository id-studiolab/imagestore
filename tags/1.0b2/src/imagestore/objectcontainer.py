import grok
from lxml import etree

from zope import component
from zope.app.catalog.interfaces import ICatalog
from zope.traversing.interfaces import IPhysicallyLocatable

from imagestore.interfaces import IXml, IRest
from imagestore.obj import Object
from imagestore.xml import (export, Settings, xml_el, xml_href, NS,
                         XmlBase, XmlContainerFactoryBase)
from imagestore.util import get_request
from imagestore.rest import StoreLayer
from imagestore.util import liberal_parse_iso_to_datetime
from imagestore.rest import Read

class ObjectContainer(grok.Container):
    grok.implements(IRest)

class ObjectsXml(XmlBase):
    is_deletable = False
    
    def search(self, element, settings, url, query):
        el_objects = xml_el(element, 'objects', settings,
                            href=url)
        catalog = component.getUtility(ICatalog)
        # look up the path of the parent of the objects obj, i.e. the group
        path = IPhysicallyLocatable(self.context.__parent__).getPath()

        q = {}
        q['paths'] = {'any_of': [path]}
        if query['tags']:
            q['tags'] = {'any_of': query['tags']}
        if query['created_after'] or query['created_before']:
            q['created'] = (query['created_after'], query['created_before'])
        if query['modified_after'] or query['modified_before']:
            q['modified'] = (query['modified_after'], query['modified_before'])
        objects = catalog.searchResults(**q)
        
        # sort result for stability of results
        objects = list(objects)
        objects.sort(key=lambda obj: obj.__name__)
        # now export as XML
        request = get_request() # XXX ugh
        deep = query['deep']
        for obj in objects:
            # if we do not want deep search, we skip anything we find
            # that doesn't have the context as the parent
            if not deep and obj.__parent__ is not self.context:
                continue
            IXml(obj).serialize_compact(el_objects, settings,
                                        url=grok.url(request, obj))
        return el_objects

    def serialize(self, element, settings, url):
        el_objects = xml_el(element, 'objects', settings,
                            href=url)
        object_names = sorted(self.context.keys())
        for object_name in object_names:
            object = self.context[object_name]
            IXml(object).serialize(el_objects, settings,
                                   url=xml_href(url, object_name))
        return el_objects

    def serialize_compact(self, element, settings, url):
        el_objects = xml_el(element, 'objects', settings,
                            href=url)
        object_names = sorted(self.context.keys())
        for object_name in object_names:
            object = self.context[object_name]
            IXml(object).serialize_compact(el_objects, settings,
                                           url=xml_href(url, object_name))
        return el_objects

    def is_allowed(self, obj):
        return isinstance(obj, Object)
    
class ObjectsFactory(XmlContainerFactoryBase):
    grok.name('{%s}objects' % NS)

    def factory(self):
        result = ObjectContainer()
        result.__name__ = 'objects'
        return result

class Rest(grok.REST):
    grok.layer(StoreLayer)

    @grok.require(Read)
    def GET(self):
        self.response.setHeader('Content-Type',
                                'text/xml; charset=UTF-8')
        app_url = grok.url(self.request, grok.getSite())
        if not self.request.form:
            tree = export(self.context, Settings(expand='compact',
                                                 app_url=app_url))
            return etree.tostring(tree, encoding='UTF-8')

        query = {
            'tags': self.getTags(),
            'created_after': self.getDatestamp('created_after'),
            'created_before': self.getDatestamp('created_before'),
            'modified_after': self.getDatestamp('modified_after'),
            'modified_before': self.getDatestamp('modified_before'),
            'deep': self.getDeep(),
            }
        el = etree.Element('export')
        tree = etree.ElementTree(el)
        IXml(self.context).search(el,
                                  Settings(expand='compact',
                                           app_url=app_url),
                                  url='.', query=query)
        tree = etree.ElementTree(el[0])
        return etree.tostring(tree, encoding='UTF-8')

    def getTags(self):
        tags = self.request.form.get('tag')
        if tags is None:
            tags = []
        if isinstance(tags, basestring):
            tags = [tags]
        return tags

    def getDeep(self):
        deep = self.request.form.get('deep', True)
        if deep == 'False':
            deep = False
        return deep

    def getDatestamp(self, name):
        stamp = self.request.form.get(name)
        if stamp is None:
            return None
        return liberal_parse_iso_to_datetime(stamp)
