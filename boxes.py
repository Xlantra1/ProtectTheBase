"""
Box manager that handles the movement, rotation, and resizing of both the boxes and the home base

Xlantra1
Copyright (c) 2017
MIT License
"""

# region Imports
from collections import namedtuple
from random import randint

import pygame

# endregion

# region Named Tuples
BoxData = namedtuple('BoxData', 'img rotation location color padding')
# endregion


# region Box Class
class Box(object):
    # region Initialization
    def __init__(self, screen):
        self.maxBoxes = 1

        self.screen = screen

        self.boxes = []
        self.numberOfBoxes = 0

        self.angle = 0

        self.home_padding = 15
        self.padding = 10
        self.box_speed = 60.0

        self.home = []

    # endregion

    # region Rotation
    @staticmethod
    def rotate_box(image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)

        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()

        return rot_image

    @staticmethod
    def rotate_home(image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)

        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center

        rot_image = rot_image.subsurface(rot_rect).copy()

        return rot_image

    # endregion

    @staticmethod
    def colorize(image, new_color):
        """
        Applies the supplied color to the image

        :param image:      The image that the color should be applied to
        :param new_color:  The color that the image should have
        :return:           The new image with the color applied
        """
        image = image.copy()

        image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        image.fill(new_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

        return image

    @staticmethod
    def create_new_color():
        """
        Creates a new random color, to spice up the look of the boxes
        """
        random_color_red = randint(0, 255)
        random_color_green = randint(0, 255)
        random_color_blue = randint(0, 255)

        return random_color_red, random_color_green, random_color_blue

    @staticmethod
    def resize_image(image, scale):
        """
        Takes an image and resize it based on the scale parameter

        :param image: The image that should be resized
        :param scale: The scale of which the image should be resized by (e.g. 1.0 is no resize, 0.5 is half scale)
                            - If an image is 100 pixels wide, and scale is set to 0.5, then the final image will have a
                              scale of 50 pixels wide
                            - Both the width and height are scaled
        :return:      The new image with the rotation applied
        """
        image_size = image.get_size()
        new_image = pygame.transform.scale(
            image, (int(image_size[0] * scale), int(image_size[1] * scale)))

        return new_image

    def move_towards_point(self, box_location, point):
        """
        Calculates how much an object needs to move, based on it's current location and the destination location

        :param box_location: The current location of the box (as a tuple)
        :param point:        The destination (as a tuple)
        :return:             How much the box needs to move (can be positive or negative)
        """
        dx, dy = (point[0] - box_location[0], box_location[1] - point[1])
        step_x, step_y = (dx / self.box_speed, dy / self.box_speed)

        return step_x, step_y

    def box_manager(self):
        """
        The manager for all the boxes. Handles the rotation, resizing, and movement of each box

        :return: None
        """
        screen_width, screen_height = self.screen.get_size()

        """
        Creates a new box, at a random location near the top, a random color, and adds it a the 'boxes' array.

        This 'boxes' array is there to ensure that with each loop, the boxes are drawn, but not re-created.
        Boxes are only re-created if there are less than the 'maxBoxes'.
        """
        if len(self.boxes) < self.maxBoxes:
            starting_angle = 0

            random_width = randint(10, 50)
            random_y = randint(0 - self.padding, (screen_width - random_width))
            random_x = randint(0 - self.padding, 50 + self.padding)

            box_image = pygame.image.load('square.png').convert_alpha()
            new_box_image = box_image.copy()
            box_color = self.create_new_color()
            new_box_image = self.colorize(new_box_image, box_color)

            box_data = BoxData(
                new_box_image,
                starting_angle,
                (random_y,
                 random_x),
                box_color,
                self.padding * 2)
            self.boxes.append(box_data)

        """
        Creates the 'home' base near the bottom. This image doesn't move, but does rotate.
        Once created, it is added to the 'home' array.

        This 'home' array is there to ensure that with each loop, the home is drawn, but not re-created.
        If the 'home' has already been created, it simply re-calculates the rotation of the sprite.
        """
        if len(self.home) == 0:
            starting_angle = 0

            home_image = pygame.image.load('home.png').convert_alpha()
            home_image = self.resize_image(home_image, 3.0)
            home_image = self.rotate_box(home_image, 0)

            home_image_size = home_image.get_rect().size

            home_start_x = (screen_width / 2) - self.home_padding
            home_start_y = ((screen_height / 2) +
                            (home_image_size[1] / 2)) - self.home_padding

            home_data = BoxData(
                home_image,
                starting_angle,
                (home_start_x,
                 home_start_y),
                (255,
                 255,
                 255),
                self.home_padding)
            self.home.append(home_data)
        else:
            for index, home in enumerate(self.home):
                home_image = pygame.image.load('home.png').convert_alpha()
                home_image = self.resize_image(home_image, 3.0)

                new_rotation = (home.rotation + 1) % 360

                home_image = self.rotate_home(home_image, new_rotation)

                home_data = BoxData(
                    home_image,
                    new_rotation,
                    home.location,
                    home.color,
                    home.padding)
                self.home[index] = home_data

        """ Loop through each box and re-calculates the rotation and location (as it moves toward the 'home' base). """
        for index, box in enumerate(self.boxes):
            box_image = pygame.image.load('square.png').convert_alpha()
            box_image = self.colorize(box_image, box.color)

            # box_image = self.ResizeImage(box_image, 0.90)

            new_rotation = (box.rotation + 1) % 360

            # TODO: Fix the hardcoded point
            points_to_move = self.move_towards_point(box.location, (250, 420))
            new_location = (
                box.location[0] +
                points_to_move[0],
                box.location[1] -
                points_to_move[1])

            new_location_x = new_location[0]
            new_location_y = new_location[1]

            if new_location_x < 0:
                new_location_x = 0

            if new_location_y < 0:
                new_location_y = 0

            final_location = (new_location_x, new_location_y)

            new_box_image = self.rotate_box(box_image, new_rotation)
            box_data = BoxData(
                new_box_image,
                new_rotation,
                final_location,
                box.color,
                box.padding)
            self.boxes[index] = box_data
# endregion
