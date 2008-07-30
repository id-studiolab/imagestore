import grok

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase
from imagestore.account import Account

class AccountContainer(grok.Container):
    grok.implements(IRest)

class AccountContainerXml(XmlContainerBase):
    tag = 'accounts'
    is_deletable = False

    def is_allowed(self, obj):
        return isinstance(obj, Account)

class AccountContainerFactory(XmlContainerFactoryBase):
    grok.name('{%s}accounts' % NS)

    def factory(self):
        result = AccountContainer()
        result.__name__ = 'accounts'
        return result
