import grok

from zope.securitypolicy.interfaces import IPrincipalRoleManager

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase, xml_el

class Permission(grok.Container):
    grok.implements(IRest)

    def __init__(self, permission):
        super(Permission, self).__init__()
        self.permission = permission

@grok.subscribe(Permission, grok.IObjectAddedEvent)
def permission_added(obj, event):
    if obj.permission not in ('read', 'write'):
        return
    try:
        role_manager(obj).assignRoleToPrincipal(
            perm2role(obj.permission), name2principalid(obj.__name__))
    except TypeError:
        # XXX if we don't have IPrincipalRoleManager set up...
        pass

@grok.subscribe(Permission, grok.IObjectRemovedEvent)
def permission_removed(obj, event):
    if obj.permission not in ('read', 'write'):
        return
    try:
        role_manager(obj).removeRoleFromPrincipal(
            perm2role(obj.permission), name2principalid(obj.__name__))
    except TypeError:
        # XXX if we don't have IPrincipalRoleManager set up...
        pass
        
#@grok.subscribe(Permission, grok.IObjectModifiedEvent):
#def permission_modified(obj, event):
#    role_manager(obj).removeRoleFromPrincipal(
#        perm2internal(obj.permission), obj.__name__)
#    role_manager(obj).assignRoleToPrincipal(
#        perm2internal(obj.permission), obj.__name__)
    
def role_manager(permission):
    """role manager for session (given permission).
    """
    return IPrincipalRoleManager(permission.__parent__.__parent__)

def perm2role(permission):
    if permission == 'read':
        return 'imagestore.Reader'
    elif permission == 'write':
        return 'imagestore.Writer'
    else:
        assert False, "Unknown permission: %s" % permission

def name2principalid(name):
    if name == 'default':
        return 'zope.anybody'
    return name

class PermissionXml(XmlContainerBase):
    tag = 'permission'
    export_name = True
    is_factory = False

    def serialize(self, element, settings, url):
        el_permission = xml_el(element, 'permission', settings,
                               name=self.context.__name__,
                               permission=self.context.permission,
                               href=url)
        return el_permission

class PermissionFactory(XmlContainerFactoryBase):
    grok.name('{%s}permission' % NS)

    set_name = True

    def factory(self):
        return Permission('none')

    def replace(self, element, result):
        result.permission = element.get('permission', 'none')
