import pygame
from pygame.locals import *

from frontend.font import get_display_font

class Buttons(object):
    def __init__(self, buttons=None):
        if buttons is None:
            buttons = []
        self._buttons = buttons

    def add_button(self, button):
        self._buttons.append(button)

    def click(self, x, y, *args, **kw):
        for button in self._buttons:
            if button.on_button(x, y):
                return button.click(*args, **kw)
        return False
    
    def render(self, screen):
        for button in self._buttons:
            button.render(screen)    

class Button(object):
    def __init__(self, label, x, y, w, h, color, label_color):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.label_color = label_color
        self.font = get_display_font()
        
    def on_button(self, x, y):
        xs = self.x
        ys = self.y
        xe = self.x + self.w
        ye = self.y + self.h
        return (xs <= x <= xe and
                ys <= y <= ye)

    def click(self, *args, **kw):
        if global_timeout.active():
            return False
        result = self.clicked(*args, **kw)
        global_timeout.start()
        return result
    
    def clicked(self, *args, **kw):
        raise NotImplementedError

    def render(self, screen):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y, self.w, self.h))
        surface = self.font.render(
            self.label, True, self.label_color, self.color)
        w = surface.get_width()
        h = surface.get_height()
        w_padding = (self.w - w) / 2
        h_padding = (self.h - h) / 2
        screen.blit(surface, (self.x + w_padding, self.y + h_padding))

class Timeout(object):
    def __init__(self, amount):
        self.amount = amount
        self._end = 0
        
    def start(self):
        self._end = pygame.time.get_ticks() + self.amount

    def active(self):
        return pygame.time.get_ticks() < self._end 

global_timeout = Timeout(500)
