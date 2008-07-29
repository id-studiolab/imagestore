import grok

from imagestore.objectcontainer import ObjectContainer
from imagestore.obj import Object
from imagestore.interfaces import IXml, IXmlFactory, IRest
from imagestore.xml import xml_el, xml_href, NS, XmlBase, XmlContainerFactoryBase

class Group(Object):
    grok.implements(IRest)
    
@grok.subscribe(Group, grok.IObjectAddedEvent)
def group_added(obj, event):
    obj['objects'] = ObjectContainer()
    
class GroupXml(XmlBase):
    is_factory = False

    @property
    def is_deletable(self):
        # if we're not in an object container we're the root group
        if not isinstance(self.context.__parent__, ObjectContainer):
            return False
        return True
    
    def _serialize_helper(self, element, settings, url):
        el_group = xml_el(element, 'group', settings,
                          name=self.context.__name__,
                          href=url)
        IXml(self.context['source']).serialize(
            el_group, settings,
            url=xml_href(url, 'source'))
        IXml(self.context['metadata']).serialize(
            el_group, settings,
            url=xml_href(url, 'metadata'))
        return el_group

    def serialize(self, element, settings, url):
        el_group = self._serialize_helper(element, settings, url)
        if settings.expand == 'all':
            IXml(self.context['objects']).serialize(
                el_group, settings,
                url=xml_href(url, 'objects'))
        else:
            IXml(self.context['objects']).serialize_compact(
                el_group, settings,
                url=xml_href(url, 'objects'))
        return el_group

    def serialize_compact(self, element, settings, url):
        el_group = self._serialize_helper(element, settings, url)
        el_objects = xml_el(el_group, 'objects', settings,
                            href=xml_href(url, 'objects'))
        return el_group

class GroupFactory(XmlContainerFactoryBase):
    grok.implements(IXmlFactory)
    grok.name('{%s}group' % NS)

    set_name = True

    def factory(self):
        return Group(None)
    
class UI(grok.View):
    pass
