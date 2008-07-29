import sys, os
from datetime import datetime
from lxml import etree

import pygame
from pygame.locals import *

from frontend.rest import Rest, NS
from frontend.button import Button, Buttons
from frontend.model import load_collection, load_group

def main():
    pygame.init()
    try:
        url = sys.argv[1]
    except IndexError:
        print "frontend <url to session>"
        return
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Front end")
    
    backend_rest = Rest(url)
    collection_rest = backend_rest.click_to('ids:group[@name="collection"]/@href')   
    collection = load_collection(collection_rest)

    mainloop['screen'] = screen
    mainloop['collection'] = collection
    mainloop.run(collectionloop)

class MainLoop(object):
    def __init__(self):
        self.next = None
        self._d = {}
        
    def __setitem__(self, name, value):
        self._d[name] = value

    def __getitem__(self, name):
        return self._d[name]

    def __get__(self, name, default=None):
        return self._d.get(name, default)

    def __delitem__(self, name):
        del self._d[name]
    
    def run(self, loop):
        while True:
            loop()
            if self.next is None:
                break
            loop = self.next
            self.next = None

    def switch(self, loop):
        self.next = loop

mainloop = MainLoop()

def grouploop(group):
    screen = mainloop['screen']
    
    drag_obj = None
    drag_x = None
    drag_y = None

    box_obj = None

    buttons = Buttons([MakeGroupButton(
        'make group', 0, screen.get_height() - 40, 80, 40,
        (0, 0, 200), (255, 255, 255)),
                       CollectionScreenButton(
        'select group',
        screen.get_width() - 80, screen.get_height() - 40, 80, 40,
        (0, 0, 200), (255, 255, 255))])
                      
    while True:
        if quit_pressed():
            break
    
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            switch = buttons.click(x, y, group)
            if switch:
                break
            if drag_obj is None and box_obj is None:
                objects = group.get_objects_at_pos(x, y)
                if objects:
                    drag_obj = objects[0]
                    drag_x, drag_y = drag_obj.relative_pos(x, y)
                else:
                    box_obj = Box(x, y)
        else:
            if drag_obj is not None:
                drag_obj.save()
                drag_obj = None
            if box_obj is not None:
                group.clear_selection()
                for obj in group.get_objects_in_box(box_obj):
                    obj.selected = True
                box_obj = None
                
        if drag_obj:
            x, y = pygame.mouse.get_pos()
            drag_obj.x = x - drag_x
            drag_obj.y = y - drag_y
        if box_obj:
            x, y = pygame.mouse.get_pos()
            box_obj.x2 = x
            box_obj.y2 = y
            
        screen.fill((255, 255, 255))
        group.render(screen)
        buttons.render(screen)
        if box_obj is not None:
            box_obj.render(screen)
        pygame.display.flip()

def collectionloop():
    screen = mainloop['screen']
    collection = mainloop['collection']
    
    buttons = collection_buttons(collection)
    real_buttons = Buttons([ReloadButton(
        'refresh', 0, 560, 80, 40,
        (0, 0, 200), (255, 255, 255))])
    
    while True:
        if quit_pressed():
            break
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            switch = real_buttons.click(x, y, screen)
            if switch:
                break
            switch = buttons.click(x, y, screen)
            if switch:
                break

        screen.fill((255, 255, 255))        
        collection.render(screen)
        real_buttons.render(screen)
        pygame.display.flip()

class CollectionScreenButton(Button):
    def clicked(self, screen):
        mainloop.switch(collectionloop)
        return True

class MakeGroupButton(Button):
    def clicked(self, group):
        collection = mainloop['collection']
        objects = group.get_selected_objects()
        collection_rest = collection.rest
        new_name = datetime.now().isoformat().replace(':', '-')
        root_rest = collection_rest
        objects_rest = root_rest.click_to('ids:objects/@href')

        el = etree.Element('{%s}group' % NS, name=new_name, nsmap={None: NS})
        etree.SubElement(el, '{%s}source' % NS, name='UNKNOWN')
        el_metadata = etree.SubElement(el, '{%s}metadata' % NS)

        el_x = etree.SubElement(el_metadata, '{%s}x' % NS)
        el_x.text = '0'
        el_y = etree.SubElement(el_metadata, '{%s}y' % NS)
        el_y.text = '0'
        el_depth = etree.SubElement(el_metadata, '{%s}depth' % NS)
        el_depth.text = '0'
        el_rotation = etree.SubElement(el_metadata, '{%s}rotation' % NS)
        el_rotation.text = '0'
        
        el_objects = etree.SubElement(el, '{%s}objects' % NS)

        for obj in objects:
            el_image = etree.SubElement(el_objects, '{%s}image' % NS,
                                        name=obj.name)
            etree.SubElement(el_image, '{%s}source' % NS, name=obj.image_name)
            el_image_metadata = etree.SubElement(el_image, '{%s}metadata' % NS)
            el_x = etree.SubElement(el_image_metadata, '{%s}x' % NS)
            el_x.text = str(obj.x)
            el_y = etree.SubElement(el_image_metadata, '{%s}y' % NS)
            el_y.text = str(obj.y)
            el_depth = etree.SubElement(el_image_metadata, '{%s}depth' % NS)
            el_depth.text = '0'
            el_rotation = etree.SubElement(el_image_metadata, '{%s}rotation' % NS)
            el_rotation.text = '0'
        
        xml = etree.tostring(el, encoding='UTF-8')
        objects_rest.post(xml)

        new_group = load_group(
            new_name,
            root_rest.click_to('ids:objects/ids:group[@name="%s"]/@href' % new_name))
        collection.add_group(new_name, new_group)
        
class SwitchGroupButton(Button):
    def __init__(self, x, y, w, h, group):
        # doesn't have a label or colors as it's not rendered
        super(SwitchGroupButton, self).__init__(None, x, y, w, h, None, None)
        self.group = group
        
    def clicked(self, screen):
        mainloop.switch(lambda: grouploop(self.group))
        return True

class ReloadButton(Button):
    def clicked(self, screen):
        mainloop['collection'].reload()
        mainloop.switch(collectionloop)
        return True

def collection_buttons(collection):
    result = []
    x = 0
    y = 40
    row_height = 32
    padding = 5
    for name, group in sorted(collection.groups.items()):
        # XXX entire horizontal area of screen won't work with dimensions
        # greater than 2000..
        result.append(
            SwitchGroupButton(0, y, 2000, row_height, group))
        y += row_height
        y += padding
    return Buttons(result)
    
class Box(object):
    def __init__(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = None
        self.y2 = None

    def render(self, screen):
        w = self.x2 - self.x1
        h = self.y2 - self.y1
        pygame.draw.rect(screen, (0, 0, 0),
                         Rect(self.x1, self.y1, w, h), 
                         2)
        
    def __repr__(self):
        return '(%s, %s) (%s, %s)' % (self.x1, self.y1, self.x2, self.y2)

def quit_pressed():
    events = pygame.event.get()
    for e in events:
        if e.type == QUIT:
            sys.exit()
            return True
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return True
    return False
