"""
Library for RGB / CIE1931 "x, y" conversion.
Based on Philips implementation guidance:
http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
Copyright (c) 2016 Benjamin Knight / MIT License.
"""
import math
import random
from collections import namedtuple


# Represents a CIE 1931 XY coordinate pair.
XYPoint = namedtuple('XYPoint', ['x', 'y'])

# LivingColors Iris, Bloom, Aura, LightStrips
GamutA = (
    XYPoint(0.704, 0.296),
    XYPoint(0.2151, 0.7106),
    XYPoint(0.138, 0.08),
)

# Hue A19 bulbs
GamutB = (
    XYPoint(0.675, 0.322),
    XYPoint(0.4091, 0.518),
    XYPoint(0.167, 0.04),
)

# Hue BR30, A19 (Gen 3), Hue Go, LightStrips plus
GamutC = (
    XYPoint(0.692, 0.308),
    XYPoint(0.17, 0.7),
    XYPoint(0.153, 0.048),
)


def get_light_gamut(model_id):
    """Gets the correct color gamut for the provided model id.
    Docs: http://www.developers.meethue.com/documentation/supported-lights
    """
    if model_id in (
        'LST001',
        'LLC010',
        'LLC011',
        'LLC012',
        'LLC006',
        'LLC007',
            'LLC013'):
        return GamutA
    elif model_id in ('LCT001', 'LCT007', 'LCT002', 'LCT003', 'LLM001'):
        return GamutB
    elif model_id in ('LCT010', 'LCT014', 'LCT011', 'LLC020', 'LST002'):
        return GamutC
    else:
        raise ValueError


class ColorHelper:

    def __init__(self, gamut=GamutB):
        self.Red = gamut[0]
        self.Lime = gamut[1]
        self.Blue = gamut[2]

    @staticmethod
    def hex_to_red(hex_color):
        """Parses a valid hex color string and returns the Red RGB integer value."""
        return int(hex_color[0:2], 16)

    @staticmethod
    def hex_to_green(hex_color):
        """Parses a valid hex color string and returns the Green RGB integer value."""
        return int(hex_color[2:4], 16)

    @staticmethod
    def hex_to_blue(hex_color):
        """Parses a valid hex color string and returns the Blue RGB integer value."""
        return int(hex_color[4:6], 16)

    def hex_to_rgb(self, h):
        """Converts a valid hex color string to an RGB array."""
        rgb = (self.hex_to_red(h), self.hex_to_green(h), self.hex_to_blue(h))
        return rgb

    @staticmethod
    def rgb_to_hex(r, g, b):
        """Converts RGB to hex."""
        return '%02x%02x%02x' % (r, g, b)

    @staticmethod
    def random_rgb_value():
        """Return a random Integer in the range of 0 to 255, representing an RGB color value."""
        return random.randrange(0, 256)

    @staticmethod
    def cross_product(p1, p2):
        """Returns the cross product of two XYPoints."""
        return p1.x * p2.y - p1.y * p2.x

    def check_point_in_lamps_reach(self, p):
        """Check if the provided XYPoint can be recreated by a Hue lamp."""
        v1 = XYPoint(self.Lime.x - self.Red.x, self.Lime.y - self.Red.y)
        v2 = XYPoint(self.Blue.x - self.Red.x, self.Blue.y - self.Red.y)

        q = XYPoint(p.x - self.Red.x, p.y - self.Red.y)
        s = self.cross_product(q, v2) / self.cross_product(v1, v2)
        t = self.cross_product(v1, q) / self.cross_product(v1, v2)

        return (s >= 0.0) and (t >= 0.0) and (s + t <= 1.0)

    @staticmethod
    def get_closest_point_to_line(a, b, p):
        """Find the closest point on a line. This point will be reproducible by a Hue lamp."""
        ap = XYPoint(p.x - a.x, p.y - a.y)
        ab = XYPoint(b.x - a.x, b.y - a.y)
        ab2 = ab.x * ab.x + ab.y * ab.y
        ap_ab = ap.x * ab.x + ap.y * ab.y
        t = ap_ab / ab2

        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0

        return XYPoint(a.x + ab.x * t, a.y + ab.y * t)

    def get_closest_point_to_point(self, xy_point):
        # Color is unreproducible, find the closest point on each line in the
        # CIE 1931 'triangle'.
        pab = self.get_closest_point_to_line(self.Red, self.Lime, xy_point)
        pac = self.get_closest_point_to_line(self.Blue, self.Red, xy_point)
        pbc = self.get_closest_point_to_line(self.Lime, self.Blue, xy_point)

        # Get the distances per point and see which point is closer to our
        # Point.
        dab = self.get_distance_between_two_points(xy_point, pab)
        dac = self.get_distance_between_two_points(xy_point, pac)
        dbc = self.get_distance_between_two_points(xy_point, pbc)

        lowest = dab
        closest_point = pab

        if dac < lowest:
            lowest = dac
            closest_point = pac

        if dbc < lowest:
            # lowest = dbc
            closest_point = pbc

        # Change the xy value to a value which is within the reach of the lamp.
        cx = closest_point.x
        cy = closest_point.y

        return XYPoint(cx, cy)

    @staticmethod
    def get_distance_between_two_points(one, two):
        """Returns the distance between two XYPoints."""
        dx = one.x - two.x
        dy = one.y - two.y
        return math.sqrt(dx * dx + dy * dy)

    def get_xy_point_from_rgb(self, red, green, blue):
        """Returns an XYPoint object containing the closest available CIE 1931 x, y coordinates
        based on the RGB input values."""

        r = ((red + 0.055) / (1.0 + 0.055)
             )**2.4 if (red > 0.04045) else (red / 12.92)
        g = ((green + 0.055) / (1.0 + 0.055)
             )**2.4 if (green > 0.04045) else (green / 12.92)
        b = ((blue + 0.055) / (1.0 + 0.055)
             )**2.4 if (blue > 0.04045) else (blue / 12.92)

        x = r * 0.664511 + g * 0.154324 + b * 0.162028
        y = r * 0.283881 + g * 0.668433 + b * 0.047685
        z = r * 0.000088 + g * 0.072310 + b * 0.986039

        cx = x / (x + y + z)
        cy = y / (x + y + z)

        # Check if the given XY value is within the color reach of our lamps.
        xy_point = XYPoint(cx, cy)
        in_reach = self.check_point_in_lamps_reach(xy_point)

        if not in_reach:
            xy_point = self.get_closest_point_to_point(xy_point)

        return xy_point

    def get_rgb_from_xy_and_brightness(self, x, y, bri=1):
        """Inverse of `get_xy_point_from_rgb`. Returns (r, g, b) for given x, y values.
        Implementation of the instructions found on the Philips Hue iOS SDK docs: http://goo.gl/kWKXKl
        """
        # The xy to color conversion is almost the same, but in reverse order.
        # Check if the xy value is within the color gamut of the lamp.
        # If not continue with step 2, otherwise step 3.
        # We do this to calculate the most accurate color the given light can
        # actually do.
        xy_point = XYPoint(x, y)

        if not self.check_point_in_lamps_reach(xy_point):
            # Calculate the closest point on the color gamut triangle
            # and use that as xy value See step 6 of color to xy.
            xy_point = self.get_closest_point_to_point(xy_point)

        # Calculate XYZ values Convert using the following formulas:
        y = bri
        x = (y / xy_point.y) * xy_point.x
        z = (y / xy_point.y) * (1 - xy_point.x - xy_point.y)

        # Convert to RGB using Wide RGB D65 conversion
        r = x * 1.656492 - y * 0.354851 - z * 0.255038
        g = -x * 0.707196 + y * 1.655397 + z * 0.036152
        b = x * 0.051713 - y * 0.121364 + z * 1.011530

        # Apply reverse gamma correction
        r, g, b = map(lambda gamma_x: (12.92 * gamma_x) if (gamma_x <= 0.0031308)
                      else ((1.0 + 0.055) * pow(gamma_x, (1.0 / 2.4)) - 0.055), [r, g, b])

        # Bring all negative components to zero
        r, g, b = map(lambda negative_components_x: max(0, negative_components_x), [r, g, b])

        # If one component is greater than 1, weight components by that value.
        max_component = max(r, g, b)
        if max_component > 1:
            r, g, b = map(lambda weight_components_x: weight_components_x / max_component, [r, g, b])

        r, g, b = map(lambda max_component_final_x: int(max_component_final_x * 255), [r, g, b])

        # Convert the RGB values to your color object The rgb values from the
        # above formulas are between 0.0 and 1.0.
        return r, g, b


class Converter:

    def __init__(self, gamut=GamutB):
        self.color = ColorHelper(gamut)

    def hex_to_xy(self, h):
        """Converts hexadecimal colors represented as a String to approximate CIE
        1931 x and y coordinates.
        """
        rgb = self.color.hex_to_rgb(h)
        return self.rgb_to_xy(rgb[0], rgb[1], rgb[2])

    def rgb_to_xy(self, red, green, blue):
        """Converts red, green and blue integer values to approximate CIE 1931
        x and y coordinates.
        """
        point = self.color.get_xy_point_from_rgb(red, green, blue)
        return point.x, point.y

    def xy_to_hex(self, x, y, bri=1):
        """Converts CIE 1931 x and y coordinates and brightness value from 0 to 1
        to a CSS hex color."""
        r, g, b = self.color.get_rgb_from_xy_and_brightness(x, y, bri)
        return self.color.rgb_to_hex(r, g, b)

    def xy_to_rgb(self, x, y, bri=1):
        """Converts CIE 1931 x and y coordinates and brightness value from 0 to 1
        to a CSS hex color."""
        r, g, b = self.color.get_rgb_from_xy_and_brightness(x, y, bri)
        return r, g, b

    def get_random_xy_color(self):
        """Returns the approximate CIE 1931 x,y coordinates represented by the
        supplied hexColor parameter, or of a random color if the parameter
        is not passed."""
        r = self.color.random_rgb_value()
        g = self.color.random_rgb_value()
        b = self.color.random_rgb_value()
        return self.rgb_to_xy(r, g, b)
