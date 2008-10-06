import grok

from zope import component

from zope.app.authentication.interfaces import IPasswordManager

from imagestore.interfaces import IRest
from imagestore.xml import xml_el, XmlBase, XmlFactoryBase, NS

class Password(grok.Model):
    grok.implements(IRest)

    def setPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        self.password = passwordmanager.encodePassword(password)

    def checkPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        return passwordmanager.checkPassword(self.password, password)

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
        result.setPassword(element.text)

