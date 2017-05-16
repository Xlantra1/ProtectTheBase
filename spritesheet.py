"""
Sprite Sheet Class

This class handles sprite sheets
This was taken from www.scriptefun.com/transcript-2-using
sprite-sheets-and-drawing-the-background
I've added some code to fail if the file wasn't found..
Note: When calling images_at the rect is the format:
(x, y, x + offset, y + offset)
"""


# region Imports
import pygame
# endregion


# region Sprite Sheet Class
class Spritesheet(object):
    def __init__(self, filename, is_alpha=None):
        try:
            if is_alpha is None:
                self.sheet = pygame.image.load(filename).convert()
            else:
                self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit(message)
    # Load a specific image from a specific rectangle

    # noinspection PyArgumentList
    def image_at(self, rectangle, colorkey=None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        # noinspection PyArgumentList
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list

    def images_at(self, rects, colorkey=None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images

    def load_strip(self, rect, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list"""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
# endregion
