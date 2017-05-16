"""
Helper that allows a user to configure the color ranges for whatever object they want to track.
Used for the main game.

Xlantra1
Copyright (c) 2017
MIT License
"""

import os.path

import cv2

# region Global Variables
# TODO: Remove global variables
v1_min = v2_min = v3_min = v1_max = v2_max = v3_max = None
# endregion

# region Trackbars


# noinspection PyUnusedLocal
def callback(value):
    """ Trackbar 'onChange' callback. Nothing is needed, so we simply pass through """
    pass


def setup_trackbars(range_filter):
    """
    Sets up the trackbar window and trackbars for the minimum and maximum values of the supplied filter

    Reference => http://docs.opencv.org/2.4/modules/highgui/doc/user_interface.html

    :param range_filter: The name of the color filter
    :return:             None
    """
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_trackbar_values(range_filter):
    """
    Retrieves the values for

    :param range_filter: The name of the color filter
    :return:             An array of the color filter trackbar values
    """
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values
# endregion

# region Settings


def load_settings():
    """
    Loads the settings for each trackbar from the 'settings.txt' file and sets the trackbar to the value it retrieved.

    :return: None
    """
    global v1_min, v2_min, v3_min, v1_max, v2_max, v3_max

    settings_file = open("settings.txt", "r")
    all_lines = settings_file.readlines()
    for setting_value in all_lines:
        if setting_value.startswith("v1_min => "):
            v1_min = setting_value.replace("v1_min => ", "").replace("\n", "")
            cv2.setTrackbarPos("H_MIN", "Trackbars", int(v1_min))

        if setting_value.startswith("v2_min => "):
            v2_min = setting_value.replace("v2_min => ", "").replace("\n", "")
            cv2.setTrackbarPos("S_MIN", "Trackbars", int(v2_min))

        if setting_value.startswith("v3_min => "):
            v3_min = setting_value.replace("v3_min => ", "").replace("\n", "")
            cv2.setTrackbarPos("V_MIN", "Trackbars", int(v3_min))

        if setting_value.startswith("v1_max => "):
            v1_max = setting_value.replace("v1_max => ", "").replace("\n", "")
            cv2.setTrackbarPos("H_MAX", "Trackbars", int(v1_max))

        if setting_value.startswith("v2_max => "):
            v2_max = setting_value.replace("v2_max => ", "").replace("\n", "")
            cv2.setTrackbarPos("S_MAX", "Trackbars", int(v2_max))

        if setting_value.startswith("v3_max => "):
            v3_max = setting_value.replace("v3_max => ", "").replace("\n", "")
            cv2.setTrackbarPos("V_MAX", "Trackbars", int(v3_max))


def save_settings(range_filter):
    """
    Saves each trackbar value to the 'settings.txt' file. Once done, saves and exits the file.

    :param range_filter: The trackbar values
    :return:
    """
    global v1_min, v2_min, v3_min, v1_max, v2_max, v3_max

    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(
        range_filter)

    settings_file = open("settings.txt", "w+")

    settings_file.write(
        "v1_min => %s\n"
        "v2_min => %s\n"
        "v3_min => %s\n"
        "v1_max => %s\n"
        "v2_max => %s\n"
        "v3_max => %s\n" %
        (v1_min, v2_min, v3_min, v1_max, v2_max, v3_max))

    settings_file.close()
# endregion

# region Main


def main():
    """
    Sets the color filter to 'HSV' (as this is what OpenCV typically uses for object tracking).

    Then we open a new window from a local camera in order to be able to adjust the settings for tracking.
    The goal is to have only the object you want to track be in white, with everything else in black (e.g. background)

    When a user hits 'S', the current trackbar values are saved and the program will exit.
    If a user hits 'Q', the program will exit without saving.

    :return:
    """
    global v1_min, v2_min, v3_min, v1_max, v2_max, v3_max

    range_filter = 'HSV'

    camera = cv2.VideoCapture(0)

    setup_trackbars(range_filter)

    if os.path.exists("settings.txt"):
        load_settings()

    running = True
    while running is True:
        ret, image = camera.read()

        if not ret:
            print "No video source found"
            break

        if range_filter == 'RGB':
            frame_to_thresh = image.copy()
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(
            range_filter)

        thresh = cv2.inRange(
            frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break
        elif cv2.waitKey(1) & 0xFF is ord('s'):
            save_settings(range_filter)
            break


if __name__ == '__main__':
    main()
# endregion
