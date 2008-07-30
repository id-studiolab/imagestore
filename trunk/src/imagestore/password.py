import grok

from imagestore.interfaces import IRest
from imagestore.xml import xml_el, XmlBase, XmlFactoryBase, NS

class Password(grok.Model):
    grok.implements(IRest)

    def __init__(self):
        pass

class PasswordXml(XmlBase):
    tag = 'password'

    is_factory = False
    is_deletable = False
    
    def serialize(self, element, settings, url):
        return xml_el(element, 'password', settings)

class PasswordXmlFactory(XmlFactoryBase):
    grok.name('{%s}password' % NS)
    
    def factory(self):
        result = Password()
        result.__name__ = 'password'
        return result
    
    def replace(self, element, result):
        pass

        
