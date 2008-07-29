import httplib
from urlparse import urlparse
from lxml import etree

NS = 'http://studiolab.io.tudelft.nl/ns/imagestore'
NS_MAP = {'ids': NS}

class Rest(object):
    def __init__(self, url):
        self.url = url
        scheme, netloc, path = urlparse(url)[:3]
        self.netloc = netloc
        self.path = path

    def get(self):
        conn = httplib.HTTPConnection(self.netloc)
        conn.request('GET', self.path)
        return conn.getresponse()

    def post(self, data, **headers):
        conn = httplib.HTTPConnection(self.netloc)
        conn.request('POST', self.path, data, headers)    
        return conn.getresponse()
    
    def put(self, data, **headers):
        conn = httplib.HTTPConnection(self.netloc)
        conn.request('PUT', self.path, data, headers)
        return conn.getresponse()
        
    def delete(self):
        conn = httplib.HTTPConnection(self.netloc)
        conn.request('DELETE', self.path)
        return conn.getresponse()

    def click_to(self, path):
        url = self.url_to(path)
        assert url is not None, "Cannot find url for xpath: %s" % path
        return Rest(url)
    
    def url_to(self, path):
        rel_urls = self.xpath(path)
        if not rel_urls:
            return None
        rel_url = rel_urls[0]
        return self.url + '/' + rel_url

    def xpath(self, path):
        return self.element().xpath(path, namespaces=NS_MAP)

    def element(self):
        response = self.get()
        data = response.read()
        return etree.XML(data)
    
        
