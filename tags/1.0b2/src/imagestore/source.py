import grok

from imagestore.interfaces import IRest
from imagestore.xml import image_url, xml_el, XmlBase, XmlFactoryBase, NS, NS_MAP

class Source(grok.Model):
    grok.implements(IRest)

    def __init__(self, image_name):
        self.image_name = image_name
        
class SourceXml(XmlBase):
    tag = 'source'

    is_factory = False
    is_deletable = False
    
    def serialize(self, element, settings, url):
        el_source = xml_el(element, 'source', settings,
                           name=self.context.image_name,
                           src=image_url(self.context, settings,
                                         self.context.image_name),
                           href=url)
        return el_source

class SourceXmlFactory(XmlFactoryBase):
    grok.name('{%s}source' % NS)
    
    def factory(self):
        result = Source(None)
        result.__name__ = 'source'
        return result
    
    def replace(self, element, result):
        # ugh, have to use unicode here as lxml _ElementStringResult
        # can't be pickled...
        result.image_name = unicode(
            element.xpath('@name', namespaces=NS_MAP)[0])
                                     
        
