import os, sys

import pygame
from pygame.locals import *

def main_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)

def get_display_font():
    return pygame.font.Font(
        main_path('ttf-bitstream-vera', 'Vera.ttf'),
        10)
