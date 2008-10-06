import sys, os
from StringIO import StringIO
from lxml import etree
import urllib2

import pygame
from pygame.locals import *

from frontend.rest import Rest, NS_MAP
from frontend.button import Button, Buttons
from frontend.util import scale_h
from frontend.font import get_display_font

class Collection(object):
    def __init__(self, rest):
        self.rest = rest
        self.groups = {}

    def reload(self):
        self.groups = {}
        load_collection_helper(self.rest, self)
        
    def add_group(self, name, group):
        self.groups[name] = group
    
    def render(self, screen):
        names = self.groups.keys()
        names.sort()
        x = 20
        y = 40
        max_height = 32
        padding = 5
        for name in names:
            group = self.groups[name]
            group.render_row(screen, x, y, max_height)
            y += max_height
            y += padding

class Group(object):
    def __init__(self, name):
        self.name = name
        self._objects = []
        
    def add_object(self, object):
        self._objects.append(object)
        
    def render(self, screen):
        for object in self._objects:
            object.render(screen)

    def render_row(self, screen, x, y, max_height):      
        padding = 10
        font = get_display_font()
        surface = font.render(
            self.name, True, (0, 0, 0), (255, 255, 255))
        screen.blit(surface, (x, y))
        x += 150 + padding
        for object in self._objects:
            image = object.thumb
            if image.get_height() > max_height:
                image = scale_h(image, max_height)
            screen.blit(image, (x, y))
            x += image.get_width() + padding
        
    def clear_selection(self):
        for obj in self._objects:
            obj.selected = False

    def get_selected_objects(self):
        result = []
        for obj in self._objects:
            if obj.selected:
                result.append(obj)
        return result
    
    def get_objects_at_pos(self, x, y):
        """Get the objects at coordinate x, y.
        """
        result = []
        for object in self._objects:
            if object.at_pos(x, y):
                result.append(object)
        return result

    def get_objects_in_box(self, box):
        x1 = box.x1
        y1 = box.y1
        x2 = box.x2
        y2 = box.y2
        
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        result = []
        for object in self._objects:
            if object.in_box(x1, y1, x2, y2):
                result.append(object)
        return result
        
class Object(object):
    def __init__(self, name, image_name, metadata_rest, image, thumb, x, y):
        self.name = name
        self.image_name = image_name
        self.metadata_rest = metadata_rest
        self.image = image
        self.thumb = thumb
        self.x = x
        self.y = y
        self.selected = False
        
    def save(self):
        xml = '''
        <metadata xmlns="http://studiolab.io.tudelft.nl/ns/imagestore">
         <depth>0.0</depth>
         <rotation>0.0</rotation>
         <x>%s</x>
         <y>%s</y>
        </metadata>
        ''' % (self.x, self.y)
        self.metadata_rest.put(xml)
        
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))
        if self.selected:
            pygame.draw.rect(screen, (200, 0, 0),
                             Rect(self.x - 2, self.y - 2,
                                  self.image.get_width()  + 2,
                                  self.image.get_height() + 2), 
                             2)


    def at_pos(self, x, y):
        return (x > self.x and y > self.y and
                x < self.x + self.image.get_width() and
                y < self.y + self.image.get_height())

    def in_box(self, x1, y1, x2, y2):
        if self.x + self.image.get_width() < x1:
            return False
        if self.x > x2:
            return False
        if self.y + self.image.get_height() < y1:
            return False
        if self.y > y2:
            return False
        return True
            
    def relative_pos(self, x, y):
        """Get coordinates relative to object.
        """
        xrel = x - self.x
        yrel = y - self.y
        if xrel < 0:
            xrel = 0
        if yrel < 0:
            yrel = 0
        if xrel >= self.image.get_width():
            xrel = self.image.get_width() - 1
        if yrel >= self.image.get_height():
            yrel = self.image.get_height() - 1
        return xrel, yrel

def load_group(name, group_rest):
    group = Group(name)
    
    xml = group_rest.get().read()
    el = etree.XML(xml)
    object_elements = el.xpath('ids:objects/*', namespaces=NS_MAP)
    for object_el in object_elements:
        name = object_el.xpath('./@name')[0]
        image_url = object_el.xpath('ids:source/@src', namespaces=NS_MAP)[0]
        image_name = object_el.xpath('ids:source/@name', namespaces=NS_MAP)[0]
        x = int(float(object_el.xpath('ids:metadata/ids:x/text()', namespaces=NS_MAP)[0]))
        y = int(float(object_el.xpath('ids:metadata/ids:y/text()', namespaces=NS_MAP)[0]))
        
        dummy, namehint = os.path.split(image_url)

        image_f = urllib2.urlopen(image_url)
        image = pygame.image.load(StringIO(image_f.read()), namehint)
        image_f.close()
        
        image.convert()

        # calculate thumbnail
        w, h = image.get_size()
        if w >= h:
            s = w
        else:
            s = h
        scaling_factor = 32. / s
        thumb = pygame.transform.scale(
            image,
            (int(w * scaling_factor), int(h * scaling_factor)))

        metadata_rest = Rest(group_rest.url + '/' +
                             object_el.xpath('ids:metadata/@href', namespaces=NS_MAP)[0])
        group.add_object(Object(name, image_name, metadata_rest, image, thumb, x, y))
    return group

def load_collection(collection_rest):
    collection = Collection(collection_rest)
    load_collection_helper(collection_rest, collection)
    return collection

def load_collection_helper(collection_rest, collection):
    root_rest = collection_rest
    xml = root_rest.get().read()
    el = etree.XML(xml)

    object_els = el.xpath('ids:objects/ids:group', namespaces=NS_MAP)

    for object_el in object_els:
        name = object_el.xpath('./@name', namespaces=NS_MAP)[0]
        group_rest = Rest(
            root_rest.url + '/' +
            object_el.xpath('./@href', namespaces=NS_MAP)[0])
        group = load_group(name, group_rest)
        collection.add_group(name, group)
