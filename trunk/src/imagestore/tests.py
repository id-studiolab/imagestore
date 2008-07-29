import unittest
import re

from lxml import etree
from zope.testing import doctest, cleanup
import zope.component.eventtesting

from imagestore.xml import XMLValidationError, local_file

class ValidationTests(unittest.TestCase):

    relaxng = etree.RelaxNG(file=local_file('rng', 'imagestore.rng'))
    
    def validate(self, el):
        if not self.relaxng.validate(etree.ElementTree(el)):
            raise XMLValidationError("%s failed to validate" % el.tag)
    
    def test_basic(self):
        xml = '''
        <imagestore xmlns="http://studiolab.io.tudelft.nl/ns/imagestore">
          <sessions>
          </sessions>
        </imagestore>
        '''
        self.validate(etree.XML(xml))

    def test_attributes(self):
        xml = '''
        <imagestore xmlns="http://studiolab.io.tudelft.nl/ns/imagestore">
          <sessions href="sessions">
          </sessions>
        </imagestore>
        '''
        self.validate(etree.XML(xml))
    
    def test_attributes_illegal(self):
        xml = '''
        <imagestore xmlns="http://studiolab.io.tudelft.nl/ns/imagestore">
          <sessions name="sessions">
          </sessions>
        </imagestore>
        '''
        self.assertRaises(XMLValidationError, self.validate, etree.XML(xml))

    def test_extended(self):
        xml = '''
        <imagestore xmlns="http://studiolab.io.tudelft.nl/ns/imagestore">
          <sessions>
            <session href="sessions/foo" name="foo">
              <group xmlns="http://studiolab.io.tudelft.nl/ns/imagestore" href="." name="collection">
                <source src="APP/sessions/foo/images/UNKNOWN" name="UNKNOWN"/>
                <metadata href="metadata">
                  <depth href="metadata/depth">0.0</depth>
                  <rotation href="metadata/rotation">0.0</rotation>
                  <x href="metadata/x">0.0</x>
                  <y href="metadata/y">0.0</y>
                </metadata>
                <objects href="objects">
                  <image href="objects/alpha" name="alpha">
                    <source src="APP/sessions/foo/images/a.png" name="a.png"/>
                    <metadata href="objects/alpha/metadata">
                      <depth href="objects/alpha/metadata/depth">0.0</depth>
                      <rotation href="objects/alpha/metadata/rotation">0.0</rotation>
                      <x href="objects/alpha/metadata/x">0.0</x>
                      <y href="objects/alpha/metadata/y">0.0</y>
                    </metadata>
                  </image>
                  <group href="objects/beta" name="beta">
                    <source src="APP/sessions/foo/images/a.png" name="a.png"/>
                    <metadata href="objects/beta/metadata">
                      <depth href="objects/beta/metadata/depth">0.0</depth>
                      <rotation href="objects/beta/metadata/rotation">0.0</rotation>
                      <x href="objects/beta/metadata/x">0.0</x>
                      <y href="objects/beta/metadata/y">0.0</y>
                    </metadata>
                    <objects href="objects/beta/objects"/>
                  </group>
                </objects>
              </group>
              <images>
              </images>
            </session>
          </sessions>
        </imagestore>
        '''
        self.validate(etree.XML(xml))


def setUpZope(test):
    zope.component.eventtesting.setUp(test)

def cleanUpZope(test):
    cleanup.cleanUp()

r_created = re.compile('<created>[^/]*</created>')
r_modified = re.compile('<modified>[^/]*</modified>')
      
def datetime_normalize(xml):
    result = r_created.sub('<created></created>', xml)
    result = r_modified.sub('<modified></modified', result)
    return result

def test_suite():
    optionflags = (
        doctest.ELLIPSIS
        | doctest.REPORT_NDIFF
        | doctest.NORMALIZE_WHITESPACE
        )
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'model.txt', optionflags=optionflags,
            setUp=setUpZope, tearDown=cleanUpZope,
            globs={'datetime_normalize': datetime_normalize}),
        unittest.makeSuite(ValidationTests)])
