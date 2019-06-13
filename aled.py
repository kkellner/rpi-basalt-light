#!/usr/bin/python3

import time
import board
import neopixel


# On CircuitPlayground Express, and boards with built in status NeoPixel -> board.NEOPIXEL
# Otherwise choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D1
#pixel_pin = board.NEOPIXEL

# On a Raspberry pi, use this instead, not all pins are supported
pixel_pin = board.D18
#pixel_pin = board.D21

# The number of NeoPixels
#num_pixels = 140
#num_pixels =  28
num_pixels =  56
#num_pixels = 60 

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRBW

#pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False,
#                           pixel_order=ORDER)
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False,
                           pixel_order=ORDER)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)


def dim_display():
    for i in range(num_pixels):
        if (i % 5) == 0:
            pixels[i] = (2,1,0,0) 
    pixels.show()

def dim2_display():
    for i in range(num_pixels):
       pixels[i] = (10,5,0,0) 
    pixels.show()

def dim3_display():
    for i in range(28):
        if (i % 1) == 0:
            pixels[i] = (2,1,0,0)
        else:
            pixels[i] = (0,0,0,0)
 
    for i in range(29,56, 1):
       pixels[i] = (0,0,0,0) 
    pixels.show()

def normal_display():
    pixels.fill((0, 0, 0, 32))
    pixels.show()

def bright_display():
    pixels.fill((0, 0, 0, 255))
    pixels.show()

def all_display():
    pixels.fill((255, 255, 255,255))
    pixels.show()


#while True:
#    rainbow_cycle(.01)
#    #pixels.fill((80, 40, 0, 0))
#    #pixels.show()


#while True:
#    pixels.fill((0, 0, 0, 128))
#    pixels.fill((0, 0, 0, 255))
#    pixels.fill((80, 0, 80, 0))  # Purple
#    pixels.fill((128, 25, 0, 0))  # Orange high
#    pixels.fill((32, 6, 0, 0))  # Orange low
#    pixels.fill((10, 5, 0, 0))  # dim

#    #pixels.fill((255, 255, 255, 255))
#    pixels.fill((128, 128, 128, 128))
#    pixels.show()
#    time.sleep(2)
    #pixels.fill((0, 0, 0, 255))

    #pixels.fill((0, 0, 0, 128))
   # pixels.fill((128, 64, 0, 32))
   # pixels.show()
   # time.sleep(2)

    #rainbow_cycle(0.001)    # rainbow cycle with 1ms delay per step
dim3_display()
#normal_display()
#bright_display()
#all_display()

