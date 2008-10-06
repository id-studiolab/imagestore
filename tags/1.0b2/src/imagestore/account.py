import grok

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase
from imagestore.password import Password

class Account(grok.Container):
    grok.implements(IRest)

    @property
    def name(self):
        return self.__name__

    def checkPassword(self, password):
        return self['password'].checkPassword(password)
    
@grok.subscribe(Account, grok.IObjectAddedEvent)
def account_added(obj, event):
    obj['password'] = Password()
    
class AccountXml(XmlContainerBase):
    tag = 'account'
    export_name = True
    is_factory = False
    
class AccountFactory(XmlContainerFactoryBase):
    grok.name('{%s}account' % NS)

    set_name = True

    def factory(self):
        return Account()
