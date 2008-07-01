import pygame
from pygame.locals import *

def scale_w(image, target_width):
    w = image.get_width()
    h = image.get_height()
    scale_factor = target_width / float(w)
    w = int(scale_factor * w)
    h = int(scale_factor * h)
    return pygame.transform.scale(image, (w, h))

def scale_h(image, target_height):
    w = image.get_width()
    h = image.get_height()
    scale_factor = target_height / float(h)
    w = int(scale_factor * w)
    h = int(scale_factor * h)
    return pygame.transform.scale(image, (w, h))
