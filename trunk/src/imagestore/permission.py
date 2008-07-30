import grok

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase, xml_el

class Permission(grok.Container):
    grok.implements(IRest)

    def __init__(self, permission):
        super(Permission, self).__init__()
        self.permission = permission

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
