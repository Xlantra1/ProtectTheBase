# Protect The Base
An interactive game using object tracking

#### Requirements

1. [Python 2.7](https://www.python.org/downloads/)
2. [OpenCV](https://github.com/skvark/opencv-python)
3. [PyGame](http://www.pygame.org/download.shtml)
4. [NumPy](https://scipy.org/install.html)

#### Configuration

The game **requires** you to configure an object to detect, based on a specific color range.
To do this, run '*HSV_Calculator.py*'. With this open, slide each slider in order to make 
only the object you want to track be completely white. Once this is done, hit '**S**' to 
save the configuration to a the '*settings.txt*' file. This file is **required** for the 
application to run. If you have a configuration file, then it will load the file on startup
(so you can adjust the settings). If you want to quit, without saving to the settings, simply
hit '**Q**'.

#### Philips Hue

The game supports the [Philips Hue](http://www2.meethue.com/en-us/) for hits and misses. 
To enable this, a file named '*ip.py*' with a variable name '**ip**' and set to the IP address
of the Philips Hue bridge. If you are unsure what the IP address is, you can go [here](https://www.meethue.com/api/nupnp)
and it should give you the address. 

You will also need to adjust the '**enable_hue**' variable in the '*protect_the_base.py*' file 

#### Debugging

By default, there are no debugging settings enabled. These include ball detection, ball trailing, box collision. The following settings are available to change (in '*protect_the_base.py*'):

- **show_ball**: where or not the outline of the ball (that is currently being tracked) is shown
- **ball_color**: determines the color of the ball outline (to make it easier to see)
 
 - **drag_trail**: determines whether or not the ball trail should be enabled
 - **drag_trail_color**: determines the color of the trail
 - **drag_trail_thickness**: determines the thickness of the trail
 
 - **draw_box_collision_circle**: whether or not the box collision circle is shown
 
 