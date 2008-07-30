import grok
from lxml import etree

from imagestore.sessioncontainer import SessionContainer
from imagestore.session import Session
from imagestore.interfaces import IRest, IImageStore, IXml, IXmlFactory
from imagestore.xml import (XmlContainerBase, XmlContainerFactoryBase,
                            Settings, NS)
from imagestore.rest import StoreLayer
from imagestore.util import is_legal_name

from zope.app.catalog.interfaces import ICatalog
from zope import component
from zope.interface import Interface
from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.exceptions.interfaces import DuplicationError

class ImageStore(grok.Container, grok.Application):
    grok.implements(IRest, IImageStore)
    
    def __init__(self):
        super(ImageStore, self).__init__()
        self['sessions'] = SessionContainer()

    def search(self, tags):
        catalog = component.getUtility(ICatalog)
        return catalog.searchResults(tags={'any_of': tags})

@grok.subscribe(ImageStore, IBeforeTraverseEvent)
def restSkin(obj, event):
    # add store layer if it is not manually provided for
    # (such as when ++rest++flash is used)
    if not StoreLayer.providedBy(event.request):
        grok.util.applySkin(event.request,
                            StoreLayer, grok.IRESTSkinType)
    
class ImageStoreXml(XmlContainerBase):
    tag = 'imagestore'
    is_factory = False
    is_deletable = False
    
    export_name = True

class ImageStoreFactory(XmlContainerFactoryBase):
    grok.implements(IXmlFactory)
    grok.name('{%s}imagestore' % NS)

    def factory(self):
        return ImageStore()

class SearchForm(grok.View):

    def update(self, tags=None):
        if tags is None:
            self.search_result = []
            return
        tags = tags.split(' ')
        catalog = component.getUtility(ICatalog)
        self.search_result = catalog.searchResults(tags={'any_of': tags})

class DashboardMacros(grok.View):
    grok.context(Interface)
    grok.name('dashboard_macros')
    grok.template('dashboard_macros')
    
class Dashboard(grok.View):
    def session_created_datetime(self, session):
        dt = session['collection']['metadata']['created'].value
        return dt.strftime('%d/%m/%Y %H:%M')
    
class DashboardAdd(grok.View):
    grok.name('dashboard_add')
    grok.template('dashboard_add')

    error = None
    
    def update(self, name=None):
        if name is None:
            return
        if not is_legal_name(name):
            self.error = ("Name '%s' contains illegal characters. "
                          "Please only use lowercase or uppercase "
                          "letters, numbers, _, . or -." % name)
            return
        try:
            self.context['sessions'][name] = Session()
        except DuplicationError:
            self.error = ("A session with name '%s' already exists." % name)
            return
        self.redirect(self.url(self.context, 'dashboard'))

class Search(grok.View):
    def update(self, tags=None):
        if tags is not None:
            tags = tags.split(' ')
        else:
            tags = []
        self.search_result = self.context.search(tags)

    def render(self):
        el = etree.Element('{%s}%s' % (NS, 'search-result'), nsmap={None:NS})
        tree = etree.ElementTree(el)
        
        app_url = self.url(grok.getSite())
        settings = Settings('expand=all', app_url=app_url)
        
        for obj in self.search_result:
            r = IXml(obj)
            r.serialize(el, settings, url=self.url(obj))

        self.response.setHeader('Content-Type',
                                'text/xml; charset=UTF-8')
        return etree.tostring(tree, encoding='UTF-8')


# XXX factory for the entire store?
