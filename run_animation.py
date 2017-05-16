"""
Sprite strip animator demo

Requires spritesheet.spritesheet and the Explode1.bmp through Explode5.bmp
found in the sprite pack at
http://lostgarden.com/2005/03/download-complete-set-of-sweet-8-bit.html

I had to make the following addition to method spritesheet.image_at in
order to provide the means to handle sprite strip cells with borders:

            elif type(colorkey) not in (pygame.Color,tuple,list):
                colorkey = image.get_at((colorkey,colorkey))

Reference => https://pygame.org/wiki/Spritesheet
"""

# region Imports
from collections import namedtuple

import pygame

from spritesheet_animation import SpriteStripAnim
# endregion

# region Named Tuples
ExplosionData = namedtuple('ExplosionData', 'location')
# endregion


# region Explosion Class
class Explosion(object):
    def __init__(self):
        self.n = 0
        self.strips = []
        self.image = None

        self.location = (0, 0)
        self.finished = False

    def initialize(self):
        fps = 12
        frames = fps / 12
        self.strips = [
            SpriteStripAnim('images/explosion.png', (0, 0, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 92, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 184, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 276, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 368, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 460, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png', (0, 552, 92, 92), 8, 0, False, frames, True) +
            SpriteStripAnim('images/explosion.png',
                            (0, 644, 92, 92), 8, 0, False, frames, True)
        ]
        clock = pygame.time.Clock()
        self.n = 0
        self.strips[self.n].iter()
        self.image = self.strips[self.n].next()
        clock.tick(fps)

    def run(self):
        if len(self.strips) > 0:
            try:
                self.image = self.strips[self.n].next()
            except StopIteration:
                self.finished = True

        return self.image
# endregion
