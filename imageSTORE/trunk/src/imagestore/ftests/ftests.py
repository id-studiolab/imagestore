import os
import unittest

from lxml import etree

import zope.testbrowser.browser
import zope.testbrowser.testing
from zope.app.testing.functional import FunctionalDocFileSuite, HTTPCaller
                                         
from imagestore.testing import http_get, http_post, http_put, http_delete
from imagestore.testing import FunctionalLayer

from z3c.blobfile.testing import FunctionalBlobDocFileSuite

NS = 'http://studiolab.io.tudelft.nl/ns/imagestore'
NS_MAP = {'ids': NS}

def image_data(name):
    filename = os.path.join(os.path.dirname(__file__), name)
    f = open(filename, 'rb')
    data = f.read()
    f.close()
    return data
 
def pretty(response):
    el = etree.XML(response.getBody())
    print etree.tostring(el, pretty_print=True)
    return el

def xpath(el, path):
    return el.xpath(path, namespaces=NS_MAP)[0]

def rel(path, rel_path):
    if rel_path.startswith('http://'):
        return rel_path
    return path + '/' + rel_path

def url_to(url, element, path):
    return rel(url, xpath(element, path))
  
def test_suite():
    globs = {}
    globs['Browser'] = zope.testbrowser.testing.Browser

    globs['http_get'] = http_get
    globs['http_post'] = http_post
    globs['http_put'] = http_put
    globs['http_delete'] = http_delete
    globs['image_data'] = image_data
    globs['http'] = HTTPCaller()

    search_globs = {}
    search_globs.update(globs)
    # these extra functions are defined inside of the rest.txt test.
    # XXX perhaps we should use these too, though the act of definition
    # in the document actually adds to it.
    search_globs['pretty'] = pretty
    search_globs['xpath'] = xpath
    search_globs['rel'] = rel
    search_globs['url_to'] = url_to
    
    rest = FunctionalBlobDocFileSuite(
        '../rest.txt',
        globs = globs,
        )
    rest.layer = FunctionalLayer
    search = FunctionalBlobDocFileSuite(
        '../search.txt',
        globs = search_globs,
        )
    search.layer = FunctionalLayer
    fake = FunctionalBlobDocFileSuite(
        '../fake.txt',
        globs = search_globs,
        )
    fake.layer = FunctionalLayer
    comprehensive = FunctionalBlobDocFileSuite(
        '../comprehensive.txt',
        globs = search_globs,
        )
    comprehensive.layer = FunctionalLayer
    tests = [rest, search, fake, comprehensive]
    return unittest.TestSuite(tests)
