import base64
import os.path
import imagestore
from zope.app.testing.functional import HTTPCaller, ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(imagestore.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

def http_get(path, **kw):
    return http_call('GET', path, **kw)
    
def http_post(path, data, **kw):
    return http_call('POST', path, data, **kw)

def http_put(path, data, **kw):
    return http_call('PUT', path, data, **kw)

def http_delete(path, **kw):
    return http_call('DELETE', path, **kw)

def http_call(method, path, data=None, basic=None, **kw):
    if path.startswith('http://localhost'):
        path = path[len('http://localhost'):]
    request_string = '%s %s HTTP/1.1\n' % (method, path)
    for key, value in kw.items():
        request_string += '%s: %s\n' % (key, value)
    if basic is not None:
        request_string += ('AUTHORIZATION: Basic %s\n' %
                           base64.encodestring(basic)) 
    if data is not None:
        request_string += '\r\n'
        request_string += data
    return HTTPCaller()(request_string, handle_errors=False)
