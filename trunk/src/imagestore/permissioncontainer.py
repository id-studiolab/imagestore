import grok

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase
from imagestore.permission import Permission

class PermissionContainer(grok.Container):
    grok.implements(IRest)

@grok.subscribe(PermissionContainer, grok.IObjectAddedEvent)
def session_added(obj, event):
    obj['default'] = Permission('write')

class PermissionContainerXml(XmlContainerBase):
    tag = 'permissions'
    is_deletable = False

    def is_allowed(self, obj):
        if obj.__name__ not in get_accounts():
            return False
        return isinstance(obj, Permission)

def get_accounts():
    return grok.getSite()['accounts']
    
class PermissionContainerFactory(XmlContainerFactoryBase):
    grok.name('{%s}permissions' % NS)

    def factory(self):
        result = PermissionContainer()
        result.__name__ = 'permissions'
        return result
