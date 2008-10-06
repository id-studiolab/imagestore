from datetime import datetime

from lxml import etree
import grok

from imagestore.interfaces import IXml, IRest
from imagestore.xml import XmlContainerBase
from imagestore.xml import (xml_el, xml_href, xml_replace, XmlBase,
                            NS, NS_MAP, XmlFactoryBase)
from imagestore.util import parse_iso_to_datetime

class Metadata(grok.Container):
    grok.implements(IRest)

@grok.subscribe(Metadata, grok.IObjectAddedEvent)
def metadata_added(obj, event):
    obj['x'] = FloatField(0.0)
    obj['y'] = FloatField(0.0)
    obj['rotation'] = FloatField(0.0)
    obj['depth'] = FloatField(0.0)
    obj['tags'] = SetField(set())
    obj['created'] = DatetimeField(datetime.now())
    obj['modified'] = DatetimeField(obj['created'].value)
    obj['custom'] = XmlField('')

class Field(grok.Model):
    grok.implements(IRest)

    read_only = False
    
    def __init__(self, value):
        self.value = value

class FloatField(Field):
    pass
    
class SetField(Field):
    pass

class DatetimeField(Field):
    # for now, all datetime fields are read only
    read_only = True

class XmlField(Field):
    pass

class FieldXml(XmlBase):
    grok.context(Field)
    grok.provides(IXml)

    is_factory = False
    is_deletable = False
    
    def serialize(self, element, settings, url):
        el_field = etree.SubElement(
            element, '{%s}%s' % (NS, self.context.__name__), nsmap={None: NS})
        el_field.text = self.context.value
        return el_field

    def replace(self, element):
        raise NotImplementedError

    def object_modified(self):
        grok.notify(grok.ObjectModifiedEvent(self.context.__parent__.__parent__))

class FloatFieldXml(FieldXml):
    grok.context(FloatField)

    def serialize(self, element, settings, url):
        el_field = xml_el(element, self.context.__name__, settings, href=url)
        el_field.text = str(self.context.value)
        return el_field

    def replace(self, element):
        self.context.value = float(element.text)
        self.object_modified()
        
class SetFieldXml(FieldXml):
    grok.context(SetField)
    
    def serialize(self, element, settings, url):
        el_field = xml_el(element, self.context.__name__, settings, href=url)
        for v in sorted(self.context.value):
            sub_field = xml_el(el_field, 'tag', settings)
            sub_field.text = v
        return el_field

    def replace(self, element):
        self.context.value = [unicode(v) for v in element.xpath(
            'ids:tag/text()', namespaces=NS_MAP)]
        self.object_modified()
        
class DatetimeFieldXml(FieldXml):
    grok.context(DatetimeField)

    def serialize(self, element, settings, url):
        el_field = xml_el(element, self.context.__name__, settings, href=url)
        el_field.text = self.context.value.isoformat()
        return el_field

    def replace(self, element):
        if self.context.read_only:
            return
        self.context.value = parse_iso_to_datetime(element.text)
        self.object_modified()

class XmlFieldXml(FieldXml):
    grok.context(XmlField)

    def serialize(self, element, settings, url):
        el_field = xml_el(element, self.context.__name__, settings, href=url)
        if self.context.value:
            value_el = etree.XML(self.context.value)
            el_field.append(value_el)
        return el_field

    def replace(self, element):
        if len(element):
            self.context.value = etree.tostring(element[0], encoding="UTF-8")
        else:
            self.context.value = ''
        self.object_modified()

class MetadataXml(XmlContainerBase):
    grok.context(Metadata)

    is_factory = False
    is_deletable = False
    
    tag = 'metadata'

class MetadataFactory(XmlFactoryBase):
    grok.name('{%s}metadata' % NS)

    def factory(self):
        result = Metadata()
        result.__name__ = 'metadata'
        return result
    
    def replace(self, element, result):
        self.validate(element)
        for field_el in element:
            dummy, field_name = field_el.tag.split('}')
            field = result[field_name]
            if field.read_only:
                continue
            IXml(field).replace(field_el)
        # notify parent object of changes
        grok.notify(grok.ObjectModifiedEvent(result.__parent__))
