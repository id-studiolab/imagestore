import grok

from lxml import etree

from z3c.blobfile.image import Image
from zope.exceptions.interfaces import DuplicationError

from imagestore.interfaces import IRest
from imagestore.xml import XmlContainerBase, NS, XmlContainerFactoryBase
from imagestore.rest import StoreLayer, success_message, error_message, embed_http
from imagestore.util import is_legal_name
from imagestore.rest import Read, Write

class ImageContainer(grok.Container):
    grok.implements(IRest)

class ImageContainerXml(XmlContainerBase):
    tag = 'images'

    is_deletable = False
    is_replacable = False
    
class ImageContainerFactory(XmlContainerFactoryBase):
    grok.name('{%s}images' % NS)

    def factory(self):
        result = ImageContainer()
        result.__name__ = 'images'
        return result

class Factory(grok.View):
    """This is a form-driven POST factory.

    It exists to help clients that cannot do proper REST submits with
    binary data.
    """
    grok.layer(StoreLayer)
    grok.require(Write)
    
    tree = None
    
    def update(self, **kw):
        form = self.request.form
        # get the Filedata
        data = form.get('Filedata', None)
        if data is None:
            self.response.setStatus(400, 'Bad Request')
            self.tree = error_message("Filedata is missing from request.")
            return
        # let's try to get the filename wherever we can
        slug = form.get('slug', None)
        if slug is None:
            slug = form.get('Filename', None)
        if slug is None:
            slug = data.filename
        self.tree = create_image(self.context, self.request, self.response,
                                 slug, data.read())

    def render(self):
        embed_http(self.request, self.response, self.tree)
        return etree.tostring(self.tree, encoding='UTF-8')

class Rest(grok.REST):
    grok.layer(StoreLayer)

    @grok.require(Write)
    def POST(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        slug = self.request.getHeader('Slug', None)
        tree = create_image(self.context, self.request, self.response,
                            slug, self.body)
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

def create_image(context, request, response, slug, data):
    if slug is None:
        response.setStatus(400, 'Bad Request')
        return error_message('Slug header is missing from request.')
    if not is_legal_name(slug):
        response.setStatus(400, 'Bad Request')
        return error_message(
            "Slug name '%s' contains illegal characters." % slug)
    try:
        context[slug] = image = Image()
        # XXX apparently location info isn't set up properly in Image
        image.__parent__ = context
        image.__name__ = slug
    except DuplicationError:
        response.setHeader('Location',
                           grok.url(request, context[slug]))
        response.setStatus(
            409, 'Conflict')
        return error_message(
            "There is already a resource with this name in this location.")
    image.data = data
    response.setStatus(201, 'Created')
    response.setHeader('Location', grok.url(request, image))
    return success_message()

