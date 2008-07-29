import grok

from imagestore.obj import Object
from imagestore.interfaces import IRest
from imagestore.xml import NS, XmlContainerBase, XmlContainerFactoryBase
 
class ImageObject(Object):
    grok.implements(IRest)

class ImageObjectXml(XmlContainerBase):
    tag = 'image'
    export_name = True
    sort_priority = {'source': 0}

    is_factory = False
    
class ImageObjectFactory(XmlContainerFactoryBase):
    grok.name('{%s}image' % NS)

    set_name = True

    def factory(self):
        return ImageObject(None)

