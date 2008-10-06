import grok

from zope.securitypolicy.interfaces import IPrincipalRoleManager

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase, xml_el

class Permission(grok.Container):
    grok.implements(IRest)

    def __init__(self, permission):
        super(Permission, self).__init__()
        self.permission = permission

def add_permission(obj):
    """Add Zope permission given Permission obj.
    """
    try:
        mgr = role_manager(obj)
    except TypeError:
        # XXX if we don't have IPrincipalRoleManager set up...
        return

    id = name2principalid(obj.__name__)
    if obj.permission in ('read', 'write'):
        mgr.assignRoleToPrincipal(perm2role(obj.permission), id)
    elif obj.permission == 'none':
        mgr.removeRoleFromPrincipal(perm2role('read'), id)
        mgr.removeRoleFromPrincipal(perm2role('write'), id)

def remove_permission(obj):
    """Remove Zope permission(s) given Permission obj.
    """
    try:
        mgr = role_manager(obj)
    except TypeError:
        # XXX if we don't have IPrincipalRoleManager set up...
        return
    # unset any relevant roles for principal
    id = name2principalid(obj.__name__)
    for role, setting in mgr.getRolesForPrincipal(id):
        mgr.unsetRoleForPrincipal(role, id)
    
@grok.subscribe(Permission, grok.IObjectRemovedEvent)
def permission_removed(obj, event):
    remove_permission(obj)
    
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
        # remove any previous permissions for this role
        remove_permission(result)
        # now get new permission
        permission = element.get('permission')
        result.permission = permission
        # add permission manually
        add_permission(result)

