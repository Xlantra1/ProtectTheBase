"""
Handles the color change events for both hits and misses

Reference => https://developers.meethue.com/documentation/lights-api

Xlantra1
Copyright (c) 2017
MIT License
"""

# region Imports
import logging
import threading

import phue

from ip import ip
from rgb_xy import Converter
from rgb_xy import GamutC
# endregion

# region Log
logging.basicConfig()
# endregion

# region Color
# Reference => https://developers.meethue.com/documentation/supported-lights
# Latest Hue lights have color gamut of 'C'
converter = Converter(GamutC)


def turn_light_to_color(light, rgb):
    red, green, blue = rgb

    light.on = True

    color_xy = converter.rgb_to_xy(red, green, blue)
    light.xy = color_xy


def store_original_color(light):
    return light.xy
# endregion


# region Hue Class
class BallGameHue(object):
    # region Initialization
    def __init__(self):
        # Find IP by going to https://www.meethue.com/api/nupnp
        self.b = phue.Bridge(ip)

        self.b.connect()

    def __str__(self):
        pass
    # endregion

    def turn_lights_on_off(self, light_switch):
        """
        Turns the lights either on or off, based on the parameter

        :param light_switch: Whether or not the light should be on or off
                                - Accepts either 'True' or 'False'
        :return:             None
        """
        phue.AllLights(self.b).on = light_switch

    def reset_lights(self, group, original_xy_value):
        """
        Resets the group of lights to a specified XY value

        Reference => https://developers.meethue.com/documentation/supported-lights (*requires login*)

        :param group:             The group number of the lights
                                    - By default, Hue has a pre-defined group for all lights, which is group #1
        :param original_xy_value: The XY value of what the light should be turned to (supplied in a tuple)
        :return:                  None
        """
        self.b.set_group(group, 'xy', original_xy_value)

    def flash_error(self, group):
        """
        Flashes the error lights for 1.5 seconds, after which they return to their original color

        Colors are in RGB format
            - By default the 'error' color is (128, 0, 0).

        :param group: The group number of the lights
                        - By default, Hue has a pre-defined group for all lights, which is group #1
        :return:      None
        """
        original_xy_value = self.b.get_group(group, 'xy')
        error_color_xy = converter.rgb_to_xy(128, 0, 0)

        self.b.set_group(group, 'xy', error_color_xy)

        t = threading.Timer(1.5, self.reset_lights, [group, original_xy_value])
        t.start()

    def flash_hit(self, group):
        """
        Flashes the 'hit' lights for 0.25 seconds, after which they return to their original color

        Colors are in RGB format
            - By default the 'hit' color is (0, 0, 128).

        :param group: The group number of the lights
                        - By default, Hue has a pre-defined group for all lights, which is group #1
        :return:      None
        """
        original_xy_value = self.b.get_group(group, 'xy')
        error_color_xy = converter.rgb_to_xy(0, 0, 128)

        self.b.set_group(group, 'xy', error_color_xy)

        t = threading.Timer(0.25, self.reset_lights, [group, original_xy_value])
        t.start()

# endregion
