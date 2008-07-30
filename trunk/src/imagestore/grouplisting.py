import grok

from imagestore.interfaces import IXml, IRest

from imagestore.group import Group
from imagestore.xml import xml_el, NS, XmlBase, XmlFactoryBase
from imagestore.util import get_request

class GroupListing(grok.Model):
    grok.implements(IRest)

    def groups(self):
        """Depth-first listing of groups.
        """
        group = self.__parent__['collection']
        result = [group]
        _groups_helper(group, result)
        return result

def _groups_helper(group, groups):
    items = sorted(group['objects'].items())
    for name, obj in items:
        if isinstance(obj, Group):
            groups.append(obj)
            _groups_helper(obj, groups)

class GroupListingXml(XmlBase):                                       
    is_factory = False
    is_replacable = False
    is_deletable = False
    
    def serialize(self, element, settings, url):
        el_groups = xml_el(element, 'groups', settings,
                           href=url)
        if settings.hyperlinks:
            request = get_request() # XXX ugh
        else:
            request = None
        for group in self.context.groups():
            if settings.hyperlinks:
                url = grok.url(request, group)
            else:
                url = None
            IXml(group).serialize(el_groups, settings,
                                  url=url)
        return el_groups
    
class GroupListingFactory(XmlFactoryBase):
    grok.name('{%s}groups' % NS)

    def factory(self):
        result = GroupListing()
        result.__name__ = 'groups'
        return result

    def replace(self, element, result):
        pass
