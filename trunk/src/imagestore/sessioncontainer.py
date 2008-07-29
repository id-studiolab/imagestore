import grok

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase
from imagestore.session import Session

class SessionContainer(grok.Container):
    grok.implements(IRest)

class SessionContainerXml(XmlContainerBase):
    tag = 'sessions'
    is_deletable = False

    def is_allowed(self, obj):
        return isinstance(obj, Session)

class SessionContainerFactory(XmlContainerFactoryBase):
    grok.name('{%s}sessions' % NS)

    def factory(self):
        result = SessionContainer()
        result.__name__ = 'sessions'
        return result

