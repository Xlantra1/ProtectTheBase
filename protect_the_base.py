"""
Main game

Handles the creation of sprites, the display of the objects, collision between objects, tracking of lives, and more

Xlantra1
Copyright (c) 2017
MIT License
"""

# region Imports
import math
import os
from collections import deque
from collections import namedtuple

import cv2
import numpy as np
import pygame
from pygame.locals import *

from boxes import Box
from hue import BallGameHue
from run_animation import Explosion

# endregion

# region Global Variables
# region Hue
enable_hue = False

if enable_hue is True:
    hue = BallGameHue()

# endregion

# region Ball
show_ball = False
ball_color = (137, 193, 255)  # 0xFF

ball_x = 0
ball_y = 0
ball_radius = 0
# endregion

# region Drag Trail
drag_trail = False
drag_trail_color = (150, 255, 255)
drag_trail_thickness = 2.5
# endregion

# region Color Range
color_range_lower = None
color_range_upper = None
# endregion

# region Font
pygame.font.init()
tnr_font = pygame.font.SysFont("Times New Roman", 24)
# endregion

# region Color
screen_is_color = True
# endregion

# region Lives
lives = 10
# endregion

# region Boxes
draw_box_collision_circle = True

initializedBoxes = False
box_class = None
# endregion

# region Collision
lastFall = None
collision_check_skip = False
# endregion

# region Clock
clock = pygame.time.Clock()
# endregion

# region Camera
camera_index = 0
camera = cv2.VideoCapture(camera_index)
# endregion

# region Deques
pts = deque(maxlen=64)
# endregion

# region PyGame Screen
screen_width, screen_height = 640, 480
final_screen = pygame.display.set_mode((screen_width, screen_height))
# endregion

# region Explosion Animations
explosion = Explosion()
explosion.initialize()

explosions = []
# endregion

# region Game Loop
running = True
# endregion

# region Named Tuples
Frame = namedtuple('Frame', 'org pg')


# endregion
# endregion

# region Color Range


def load_color_range():
    if not os.path.exists("settings.txt"):
        print "MISSING COLOR RANGE FILE (settings.txt)"
        exit()

    global color_range_lower, color_range_upper

    v1_min = v2_min = v3_min = v1_max = v2_max = v3_max = None

    settings_file = open("settings.txt", "r")
    all_lines = settings_file.readlines()
    for setting_value in all_lines:
        if setting_value.startswith("v1_min => "):
            v1_min = setting_value.replace("v1_min => ", "").replace("\n", "")

        if setting_value.startswith("v2_min => "):
            v2_min = setting_value.replace("v2_min => ", "").replace("\n", "")

        if setting_value.startswith("v3_min => "):
            v3_min = setting_value.replace("v3_min => ", "").replace("\n", "")

        if setting_value.startswith("v1_max => "):
            v1_max = setting_value.replace("v1_max => ", "").replace("\n", "")

        if setting_value.startswith("v2_max => "):
            v2_max = setting_value.replace("v2_max => ", "").replace("\n", "")

        if setting_value.startswith("v3_max => "):
            v3_max = setting_value.replace("v3_max => ", "").replace("\n", "")

    color_range_lower = (int(v1_min), int(v2_min), int(v3_min))
    color_range_upper = (int(v1_max), int(v2_max), int(v3_max))


load_color_range()


# endregion

# region Camera


def get_cam_frame(is_color, video_camera):
    """
    Retrieves the camera. Will exit if no camera is found. Also will convert to black and white, depending on parameter.

    :param is_color:     Whether or not the image should be converted to black and white
                            - Supports either 'True' or 'False'
    :param video_camera: The camera (which should be opened already by OpenCV, from the global variables)
    :return f:           A named tuple for Frame, which consists of:
                            - OpenCV frame
                            - Pygame frame (it's the OpenCV converted to a Pygame surface)
    """
    return_value, camera_frame = video_camera.read()
    if return_value is not True:
        print "NO CAMERA FOUND...EXITING"
        exit()

    camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    if not is_color:
        camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
        camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_GRAY2RGB)

    f = Frame(camera_frame, pygame.surfarray.make_surface(camera_frame))

    return f


def blit_cam_frame(camera_frame, game_screen):
    """
    Transform the frame by rotating and flipping it. After this, outputs the screen to the user

    :param camera_frame: A frame that was captured by the video camera
    :param game_screen:  The Pygame screen
    :return:             The Pygame screen
    """
    surf = pygame.transform.rotate(camera_frame, -90)
    surf = pygame.transform.flip(surf, True, False)

    game_screen.blit(surf, (0, 0))
    return game_screen


# endregion

# region Main Game Loop
while running:
    """ Exit the game if the 'ESC' key is pressed """
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

    final_screen.fill(0)
    frame = get_cam_frame(screen_is_color, camera)

    ##############################

    """
    Convert the Pygame frame into a new surface in order to do object tracking.
    Then creates a object mask based on the color range.

    Object tracking is done through tracking a specific range of colors
    """
    surface_array = pygame.surfarray.array3d(frame.pg)
    hsv = cv2.cvtColor(surface_array, cv2.COLOR_RGB2HSV)

    color_mask = cv2.inRange(hsv, color_range_lower, color_range_upper)
    color_mask = cv2.erode(color_mask, None, iterations=2)
    color_mask = cv2.dilate(color_mask, None, iterations=2)

    contours = cv2.findContours(color_mask.copy(),
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    """
    Will only calculate and draw the ball object if it has found one

    Also requires the radius to total 10 or more
    """
    if len(contours) > 0:

        c = max(contours, key=cv2.contourArea)
        ((ball_x, ball_y), ball_radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if ball_radius > 10:

            if show_ball is True:
                cv2.circle(surface_array, (int(ball_x), int(ball_y)),
                           int(ball_radius), ball_color, 2)
                cv2.circle(surface_array, center, 5, ball_color, -1)

            """
            Attempts to determine whether or not the ball traveling up or not. If it is, skip collision.

            This is so that the ball doesn't remove any boxes in its' path as it travels up.
                - This prevents people from through the ball straight up in front of the camera
            """
            if lastFall is None:
                lastFall = ball_y
            else:
                if ball_y > lastFall:
                    collision_check_skip = True
                else:
                    collision_check_skip = False

                lastFall = ball_y * 1.01

    """ Handles the management of the boxes, such as creating and updating them """
    surface_array = pygame.surfarray.make_surface(surface_array)
    if initializedBoxes is False:
        box_class = Box(surface_array)
        initializedBoxes = True

    box_class.screen = surface_array

    box_class.box_manager()
    surface_array = pygame.surfarray.array3d(surface_array)

    for index, box in enumerate(box_class.boxes):
        box_size = box.img.get_size()
        box_center = (
            (box.location[0] + box_size[0] / 2),
            (box.location[1] + box_size[1] / 2))

        x1 = box_center[0]
        y1 = box_center[1]

        box_radius = (box_size[0] - box.padding) / 2

        if collision_check_skip is not True:
            x2 = ball_x
            y2 = ball_y

            dist = math.hypot(x1 - x2, y1 - y2)

            sum_radius = box_radius + ball_radius

            if dist < sum_radius:
                try:
                    box_class.boxes.pop(index)

                    ne = explosion
                    ne.location = (
                        box_center[0] - box_radius,
                        box_center[1] - box_radius)
                    ne.strips[ne.n].iter()
                    ne.finished = False

                    if enable_hue is True:
                        hue.flash_hit(1)

                    explosions.append(ne)
                except ValueError:
                    pass

        # HOME BASE #
        x2 = screen_width / 2
        y2 = screen_height + 25

        dist = math.hypot(x1 - x2, y1 - y2)

        sum_radius = box_radius + 100

        if dist < sum_radius:
            try:
                box_class.boxes.pop(index)

                if enable_hue is True:
                    hue.flash_error(1)

                lives -= 1
                if lives <= 0:
                    print "GAME OVER"
                    running = False
            except ValueError:
                pass
                # HOME BASE #

    """ Update the ball trail, if it is currently being shown """
    pts.appendleft(center)

    for i in xrange(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue

        if drag_trail is True:
            drag_trail_final_thickness = int(
                np.sqrt(64 / float(i + 1)) * drag_trail_thickness)
            cv2.line(surface_array,
                     pts[i - 1],
                     pts[i],
                     drag_trail_color,
                     drag_trail_final_thickness)

    """ Creates a new Pygame surface in order create a new OpenCV frame (which will be used for animations """
    final_surface_array = pygame.surfarray.make_surface(surface_array)
    final_screen = blit_cam_frame(final_surface_array, final_screen)

    """ Creates a new explosion animation, if there are any to create """
    for index, exp in enumerate(explosions):
        if exp.finished is False:
            final_screen.blit(exp.run(), exp.location)
        else:
            explosions.pop(index)

    """ Loop through the boxes and display them on the screen. Also displays the UI text """
    for index, boxData in enumerate(box_class.boxes):
        final_screen.blit(boxData.img, boxData.location)

        box_size = boxData.img.get_size()

        box_center = (
            (boxData.location[0] + box_size[0] / 2),
            (boxData.location[1] + box_size[1] / 2))
        box_center = (int(box_center[0]), int(box_center[1]))

        if draw_box_collision_circle is True:
            pygame.draw.circle(final_screen, (0, 255, 0), box_center,
                               (box_size[0] - boxData.padding) / 2, 3)

        lives_label = tnr_font.render("Lives: " + str(lives), 1, (255, 255, 0))
        final_screen.blit(lives_label, (25, screen_height - 35))

    """ Displays the home image """
    for index, homeData in enumerate(box_class.home):
        home_size = homeData.img.get_size()
        final_screen.blit(homeData.img, ((screen_width / 2) - (home_size[0] / 2), screen_height - (home_size[1] / 3)))

    """ Displays the two circles covering the base (for looks) """
    pygame.draw.circle(final_screen, (255, 255, 0), (screen_width / 2, screen_height + 25), 100, 5)
    pygame.draw.circle(final_screen, (255, 0, 0), (screen_width / 2, screen_height + 25), 90, 5)

    pygame.display.flip()
# endregion

# region Exit
pygame.quit()
cv2.destroyAllWindows()
# endregion
