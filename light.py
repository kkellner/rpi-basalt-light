# Basalt project
#
# light.py - handle LED updates (NeoPixel) of basalt light
#

import logging
import time
import threading
import board
import RPi.GPIO as GPIO
import neopixel
from enum import Enum

logger = logging.getLogger('light')
motion_logger = logging.getLogger('basalt_motion')

class Color:
    RED = (255, 0, 0)
    YELLOW = (255, 200, 0)
    GREEN = (0, 255, 0)
    AQUA = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (255, 0, 255)
    BLACK = (0, 0, 0)



class Light:
    """Handle LED Light operations"""

    # Configure GPIO pins
    motion_detect_pin = 17  # G17
    pixel_pin = board.D18

    # The number of NeoPixels
    num_pixels =  56

    display_auto_off_time_seconds = 5

    def __init__(self, basalt):
        self.basalt = basalt
        self.display_off_timer = None

        # Docs: https://circuitpython.readthedocs.io/projects/neopixel/en/latest/api.html
        self.pixels = neopixel.NeoPixel(pin=Light.pixel_pin, n=Light.num_pixels,
                                        brightness=1.0, auto_write=False,
                                        pixel_order=neopixel.GRBW)

        # Configure motion detection
        GPIO.setup(Light.motion_detect_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(Light.motion_detect_pin, GPIO.BOTH, callback=self.motionHandler)


    def shutdown(self):
        self.turnOffDisplay()

    def motionHandler(self, channel):
        #logger.info('In motionHandler channel: %s' % channel)
        #motion_logger.info('Motion Detected')

        if GPIO.input(Light.motion_detect_pin):
            logger.info("Rising edge detected")
            self._stop_display_off_timer()
            self.dim_display()
 
        else:
            logger.info("Falling edge detected")
            # Start the off light timer when no more motion is detected
            self._stop_display_off_timer()
            self.display_off_timer = threading.Timer(
                Light.display_auto_off_time_seconds, self.turnOffDisplay)
            self.display_off_timer.daemon = True
            self.display_off_timer.start()


    def _stop_display_off_timer(self):
        if self.display_off_timer is not None:
            self.display_off_timer.cancel()
        self.display_off_timer = None

    def turnOffDisplay(self):
        logger.info('In turnOffDisplay')
        self._stop_display_off_timer()
        self.pixels.fill((0, 0, 0, 0))
        self.pixels.show()


    def dim_display(self):
        for i in range(28):
            self.pixels[i] = (2,1,0,0)
    
        for i in range(29,56, 1):
            self.pixels[i] = (0,0,0,0)

        self.pixels.show()


    def showStartup(self):
        self._STARTUP_Sequence()

    def _STARTUP_Sequence(self):
        self.pixels.fill((0, 128, 0, 0))
        self.pixels.show()
        time.sleep(1)
        self.pixels.fill((0, 0, 0, 0))
        self.pixels.show()

    def _ERROR_Sequence(self):
        speed = 0.2
        self.pixels[0] = Color.RED
        self.pixels[1] = Color.BLACK
        self.pixels.show()
        time.sleep(speed)
        self.pixels[0] = Color.BLACK
        self.pixels[1] = Color.RED
        self.pixels.show()
        time.sleep(speed)

