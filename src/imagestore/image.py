import grok

from lxml import etree

from z3c.blobfile.image import Image

from imagestore.interfaces import IXml
from imagestore.xml import xml_el
from imagestore.rest import (StoreLayer, fakePutOrDelete,
                          success_message, error_message, embed_http)

class ImageXml(grok.Adapter):
    grok.context(Image)
    grok.provides(IXml)

    def serialize(self, element, settings, url):
        el_image = xml_el(element, 'source-image', settings,
                          name=self.context.__name__,
                          href=url)
        return el_image

class Formdata(grok.View):
    grok.context(Image)
    grok.layer(StoreLayer)

    tree = None
    
    def update(self, **kw):
        form = self.request.form
        # get the Filedata
        data = form.get('Filedata', None)
        if data is None:
            self.response.setStatus(400, 'Bad Request')
            self.tree = error_message("Filedata is missing from request.")
            return
        self.context.data = data.read()
        self.tree = success_message()
        self.response.setStatus(200)

    def render(self):
        embed_http(self.request, self.response, self.tree)
        return etree.tostring(self.tree, encoding='UTF-8')

# XXX a bit of hackery to make REST views work with Image, making
# grok's traverser available for Image.
class ImageTraverser(grok.Traverser):
    grok.context(Image)
    
class ImageRest(grok.REST):
    grok.layer(StoreLayer)
    grok.context(Image)

    def GET(self):
        return self.context.data

    def POST(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        msg = fakePutOrDelete(self.context, self.request)
        if msg is not None:
            return msg
        self.response.setStatus(405, 'Method not allowed')
        tree = error_message(
            "Creation of content with POST is not allowed at this location.")
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')
        
    def PUT(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        self.context.data = self.body
        self.response.setStatus(200)
        tree = success_message()
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

    def DELETE(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        del self.context.__parent__[self.context.__name__]
        self.response.setStatus(200)
        tree = success_message()
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')
