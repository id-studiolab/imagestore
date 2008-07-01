import grok
from lxml import etree
import cgi

from zope import component
from zope.publisher.interfaces import INotFound

from imagestore.interfaces import IRest, IXml, IHTTPEmbed, IHTTPOnly200
from imagestore.xml import (export, Settings, NS,
                            XMLValidationError, XMLRecognitionError,
                            ContentNotAllowedError, CreationConflictError,
                            FactoryNotAllowedError, ReplaceNotAllowedError)

class StoreLayer(grok.IRESTLayer):
    pass

class FlashLayer(StoreLayer):
    pass

class Rest(grok.REST):
    grok.context(IRest)
    grok.layer(StoreLayer)
    
    def GET(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        app_url = grok.url(self.request, grok.getSite())
        tree = export(self.context, Settings(expand='compact',
                                             app_url=app_url))
        self.response.setStatus(200)
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

    def POST(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        # fake PUT or DELETE if necessary
        msg = fakePutOrDelete(self.context, self.request)
        if msg is not None:
            return msg
        # normal POST behavior
        # set status in case what follows is successful. this
        # may overridden in the helper
        self.response.setStatus(201, 'Created')
        obj, tree = self._put_post_helper(
            lambda element: IXml(self.context).factory(element))
        # if we created a new object, or if there's an object already
        # there in conflict with ours, set the Location header with it
        if obj is not None:
            self.response.setHeader('Location', grok.url(self.request, obj))
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')
    
    def PUT(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        self.response.setStatus(200, 'Ok')
        obj, tree = self._put_post_helper(
            lambda element: IXml(self.context).replace(element))
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

    def _put_post_helper(self, func):
        try:
            element = etree.XML(self.body)
             # remove any http element that got in during roundtrip
            remove_http(element)
        except etree.XMLSyntaxError:
            self.response.setStatus(400, 'Bad Request')
            return None, error_message(
                "The submitted data was not well-formed XML.")
        try:
            return func(element), success_message()
        except FactoryNotAllowedError:
            self.response.setStatus(405, 'Method not allowed')
            return None, error_message(
                "Creation of content with POST is not allowed at this location.")
        except ReplaceNotAllowedError:
            self.response.setStatus(405, 'Method not allowed')
            return None, error_message(
                "Replacing of content with PUT is not allowed at this location.")
        except XMLRecognitionError:
            self.response.setStatus(400, 'Bad Request')
            return None, error_message(
                "The submitted XML could not be recognized.")
        except XMLValidationError:
            self.response.setStatus(400, 'Bad Request')
            return None, error_message("The submitted XML was invalid.")
        except ContentNotAllowedError:
            self.response.setStatus(400, 'Bad Request')
            return None, error_message(
                "The submitted content could not be added in this location.")
        except CreationConflictError, e:
            self.response.setStatus(409, 'Conflict')
            return (e.conflicting_object,
                    error_message("There is already a resource with this name "
                                  "in this location."))
        # shouldn't ever reach here
        assert False, "Failure in PUT or POST processing"

    def DELETE(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
 
        if IXml(self.context).is_deletable:
            self.response.setStatus(200, 'Ok')
            del self.context.__parent__[self.context.__name__]
            tree = success_message()
        else:
            self.response.setStatus(405, 'Method not allowed')
            tree = error_message(
                "This location may not be DELETEed")            
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

class StoreProtocol(grok.RESTProtocol):
    grok.layer(StoreLayer)
    grok.name('store')

class FlashProtocol(StoreProtocol):
    grok.layer(FlashLayer)
    grok.name('flash')

def fakePutOrDelete(context, request):
    """Check whether to do fake PUT or DELETE.

    If fake needs to be performed, return message of fake request.
    If no faking is requested, return None.
    """
    qs = request.environment['QUERY_STRING']
    # this is an optimization so we don't have to do parse_qs all the time
    if not '_method=' in qs:
        return None
    d = cgi.parse_qs(qs)
    method = d.get('_method', None)
    # there actually was no _method parameter after all
    if method is None:
        return None
    method = method[0]
    method = method.lower()
    if method == 'put':
        view = component.getMultiAdapter((context, request),
                                         name='PUT')
        return view()
    elif method == 'delete':
        view = component.getMultiAdapter((context, request),
                                         name='DELETE')
        return view()
    # unknown fake HTTP method, ignore
    return None

class HTTPEmbed(grok.GlobalUtility):
    grok.provides(IHTTPEmbed)
    
    def __call__(self, request):
        return FlashLayer.providedBy(request)

class HTTPOnly200(grok.GlobalUtility):
    grok.provides(IHTTPOnly200)
    
    def __call__(self, request):
        return FlashLayer.providedBy(request)

def embed_http(request, response, tree):
    """Given an XML tree, embed HTTP response information in it.

    Also set actual response code to 200 if this turns out to be required
    by very broken clients.
    """
    is_http_embedded = component.getUtility(IHTTPEmbed)
    if not is_http_embedded(request):
        return
    http_el = etree.Element('{%s}http' % NS)
    root = tree.getroot()
    # move any text to after the HTTP element
    text = root.text
    # insert HTTP element
    root.insert(0, http_el)
    # make the text now the tail of HTTP
    http_el.tail = text
    # no more text
    root.text = None
    
    status_el = etree.SubElement(http_el, '{%s}status' % NS)
    status_el.attrib['code'] = str(response.getStatus())
    status_message = response.getStatusString()
    i = status_message.find(' ')
    status_message = status_message[i+1:]
    status_el.text = status_message
    for name, value in sorted(response.getHeaders()):
        if name == 'X-Powered-By':
            continue
        header_el = etree.SubElement(http_el, '{%s}header' % NS)
        header_el.attrib['name'] = name
        header_el.text = value

    # in very broken clients, only 200 response messages allow the
    # client to inspect the body. We force the response message back to
    # 200 at the last moment (after which we already exported the true
    # status message in the XML)
    response_only_200 = component.getUtility(IHTTPOnly200)
    if response_only_200(request):
        response.setStatus(200, 'Ok')

def remove_http(root):
    """Given root element, remove http element if it's there.
    """
    try:
        el = root[0]
    except IndexError:
        return
    if el.tag.endswith('}http'):
        del root[0]

def success_message():
    """Return XML success message.
    """
    success_el = etree.Element('{%s}success' % NS, nsmap={None:NS})
    tree = etree.ElementTree(element=success_el)
    return tree

def error_message(msg):
    """Return XML error message.
    """
    error_el = etree.Element('{%s}error' % NS,  nsmap={None:NS})
    message_el = etree.SubElement(error_el, '{%s}message' % NS)
    message_el.text = msg
    tree = etree.ElementTree(element=error_el)
    return tree

class NotFoundView(grok.View):
    grok.context(INotFound)
    grok.layer(StoreLayer)
    grok.name('index.html')

    def render(self):
        self.response.setHeader('Content-Type',
                                'application/xml; charset=UTF-8')
        self.response.setStatus(404)
        tree = error_message('Not found: %s' % self.request.getURL())
        embed_http(self.request, self.response, tree)
        return etree.tostring(tree, encoding='UTF-8')

