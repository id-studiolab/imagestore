from StringIO import StringIO
from lxml import etree
import os
import grok
from zope import component

from imagestore.interfaces import IXml, IXmlFactory, ISession

NS = u'http://studiolab.io.tudelft.nl/ns/imagestore'
NS_MAP = {'ids': NS}

class XMLValidationError(Exception):
    pass

class XMLRecognitionError(XMLValidationError):
    pass

class ContentNotAllowedError(ValueError):
    pass

class CreationConflictError(ValueError):
    def __init__(self, message, conflicting_object):
        ValueError.__init__(self, message)
        self.conflicting_object = conflicting_object

class FactoryNotAllowedError(ValueError):
    pass

class ReplaceNotAllowedError(ValueError):
    pass

def xml_el(element, element_name, settings, **kw):
    if not settings.hyperlinks:
        try:
            del kw['href']
        except KeyError:
            pass
    el = etree.SubElement(
        element,
        '{%s}%s' % (NS, element_name),
        nsmap={None:NS},
        **kw)
    return el

def xml_href(url, name):
    # if no URL is passed in, we don't generate one. This is
    # used when hyperlinks=False
    if url is None:
        return None
    if url == '.':
        return name
    else:
        return url + '/' + name

def xml_replace(element, object):
    factory = component.getUtility(IXmlFactory, name=element.tag)
    factory.replace(element, object)

def xml_factory(element):
    return component.queryUtility(IXmlFactory,
                                  name=element.tag, default=None)


def image_url(obj, settings, name):
    while obj is not None:
        if ISession.providedBy(obj):
            return '%s/sessions/%s/images/%s' % (
                settings.app_url, obj.__name__, name)
        obj = obj.__parent__
    assert False, "images container could not be found"

class Settings(object):
    def __init__(self, root_url='.', expand='all', hyperlinks=True,
                 app_url=None):
        self.root_url = '.'
        self.expand = expand
        self.hyperlinks = hyperlinks
        if app_url is None:
            app_url = 'APP'
        self.app_url = app_url

def export(obj, settings):
    el = etree.Element('export')
    tree = etree.ElementTree(el)
    r = IXml(obj)
    r.serialize(el, settings, url='.')
    return etree.ElementTree(el[0])

def import_(xml):
    dummy_context = {}
    el = etree.parse(StringIO(xml)).getroot()
    factory = xml_factory(el)
    factory.create(dummy_context, el, lambda item: True, overwrite=True)
    assert len(dummy_context.keys()) == 1
    return dummy_context[dummy_context.keys()[0]]

class XmlBase(grok.Adapter):
    grok.provides(IXml)
    grok.baseclass()

    is_factory = True
    is_deletable = True
    is_replacable = True
    
    def serialize(self, element, settings, url):
        raise NotImplementedError

    def serialize_compact(self, element, settings, url):
        return self.serialize(element, settings, url)

    def factory(self, element):
        factory = component.queryUtility(IXmlFactory, name=element.tag,
                                         default=None)
        if factory is None:
            if not self.is_factory:
                raise FactoryNotAllowedError()
            raise XMLRecognitionError(
                "XML element %s was not recognized." % element.tag)
        return factory.create(self.context, element, self.is_allowed,
                              overwrite=False)

    def is_allowed(self, obj):
        return False

    def replace(self, element):
        factory = component.queryUtility(IXmlFactory, name=element.tag,
                                         default=None)
        if factory is None:
            if not self.is_replacable:
                raise ReplaceNotAllowedError()
            raise XMLRecognitionError(
                "XML element %s was not recognized." % element.tag)
        factory.replace(element, self.context)

class XmlContainerBase(XmlBase):
    grok.provides(IXml)
    grok.baseclass()
    
    tag = None
    export_name = False

    sort_priority = {}
    
    def serialize(self, element, settings, url):
        if self.export_name:
            el_result = xml_el(element, self.tag, settings,
                               name=self.context.__name__,
                               href=url)
        else:
            el_result = xml_el(element, self.tag, settings,
                               href=url)

        def priority_key(n):
            return (self.sort_priority.get(n, 1000), n)

        names = sorted(self.context.keys(), key=priority_key)
        for name in names:
            obj = self.context[name]
            IXml(obj).serialize(el_result, settings,
                                url=xml_href(url, name))
        return el_result

# a validator cache
validators = {}

def local_file(*names):
    return os.path.join(os.path.dirname(__file__), *names)

class XmlFactoryBase(grok.GlobalUtility):
    grok.implements(IXmlFactory)
    grok.baseclass()
    
    set_name = False

    def factory(self):
        raise NotImplementedError
    
    def create(self, context, element, is_allowed, overwrite):
        result = self.factory()
        if self.set_name:
            name = element.get('name')
            result.__name__ = unicode(name)
        if not is_allowed(result):
            raise ContentNotAllowedError(
                "Not allowed to add in this location: %s" % element.tag)
        if result.__name__ in context:
            if overwrite:
                del context[result.__name__]
            else:
                raise CreationConflictError(
                    "Object with name '%s' already exists" % name,
                    context[result.__name__])
        self.validate(element)
        context[result.__name__] = result
        self.replace(element, result)
        return result
    
    def replace(self, element, result):
        raise NotImplementedError
    
    def validate(self, element):
        # XXX a bit of inside knowledge about grok here...
        grok_name = grok.name.bind().get(self)
        dummy, tag_name = grok_name.split('}')
        validator = validators.get(tag_name)
        if validator is None:
            validator =  etree.RelaxNG(
                file=local_file('rng', '%s.rng' % tag_name))
            validators[tag_name] = validator
        if not validator.validate(etree.ElementTree(element)):
            raise XMLValidationError("%s failed to validate" % element.tag)

class XmlContainerFactoryBase(XmlFactoryBase):
    grok.baseclass()
    
    def replace(self, element, result):
        # XXX this is a duplication if we call this from create
        self.validate(element)
        # everything is allowed while replacing; schema validation will
        # make sure nothing weird slips in already.
        is_allowed = lambda item: True
        for el in element:
            factory = xml_factory(el)
            # don't create anything unrecognized
            if factory is None:
                continue
            factory.create(result, el, is_allowed, overwrite=True)
