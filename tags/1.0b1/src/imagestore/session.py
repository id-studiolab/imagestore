import grok

from imagestore.imagecontainer import ImageContainer
from imagestore.grouplisting import GroupListing
from imagestore.group import Group
from imagestore.interfaces import IRest, ISession
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase

class Session(grok.Container):
    grok.implements(ISession, IRest)

@grok.subscribe(Session, grok.IObjectAddedEvent)
def session_added(obj, event):
    obj['images'] = ImageContainer()
    obj['collection'] = Group('UNKNOWN')
    obj['groups'] = GroupListing()
    
class SessionXml(XmlContainerBase):
    tag = 'session'
    export_name = True
    is_factory = False
    
class SessionFactory(XmlContainerFactoryBase):
    grok.name('{%s}session' % NS)

    set_name = True

    def factory(self):
        return Session()

class DashboardEdit(grok.View):
    grok.name('dashboard_edit')
    grok.template('dashboard_edit')

class DashboardDelete(grok.View):
    grok.name('dashboard_delete')
    grok.template('dashboard_delete')

    def update(self):
        if ('cancel' not in self.request.form and
            'delete' not in self.request.form):
            return
        app_url = self.application_url('dashboard')
        if 'delete' in self.request.form:
            del self.context.__parent__[self.context.__name__]
        self.redirect(app_url)
