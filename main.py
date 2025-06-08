# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import random

from rpi_ws281x import ws, Color, Adafruit_NeoPixel

# LED strip configuration:
LED_1_COUNT = 600       # Number of LED pixels.
LED_1_PIN = 18          # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3).
LED_1_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_1_DMA = 10          # DMA channel to use for generating signal (Between 1 and 14)
LED_1_BRIGHTNESS = 200  # Set to 0 for darkest and 255 for brightest
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL = 0       # 0 or 1
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600       # Number of LED pixels.
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA = 9           # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 200  # Set to 0 for darkest and 255 for brightest
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL = 1       # 0 or 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

import time
import math
import random
from LedEffects import *
from rpi_ws281x import Color


# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel objects with appropriate configuration for each strip.
    strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ,
                               LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS,
                               LED_1_CHANNEL, LED_1_STRIP)

    strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ,
                               LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS,
                               LED_2_CHANNEL, LED_2_STRIP)

    # Intialize the library (must be called once before other functions).
    strip1.begin()
    strip2.begin()

    print('Press Ctrl-C to quit.')

    blackout(strip1)
    blackout(strip2)
    time.sleep(3)

    fill_color(strip1, (255, 0, 0, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip1, (0, 255, 0, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip1, (0, 0, 255, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip1, (0, 0, 0, 255))  # Clear strip1
    time.sleep(3)

    blackout(strip1)
    time.sleep(3)
    fill_color(strip2, (255, 0, 0, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip2,(0, 255, 0, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip2,(0, 0, 255, 0))  # Clear strip1
    time.sleep(3)
    fill_color(strip2,(0, 0, 0, 255))  # Clear strip1
    time.sleep(3)


    # Black out any LEDs that may be still on for the last run
    blackout(strip1)
    blackout(strip2)
    
    while True:

        # Synchronized bouncing colors
        color_bounce(strip1, strip2, duration=20, change_color_on_bounce = True)

        # Independent bounces, unique colors & positions
        color_bounce(strip1, strip2, duration=20, independent=True, change_color_on_bounce = True)

        wave_ripple_dual(strip1, strip2, duration=15)

        # Independent ripple on both strips
        wave_ripple_dual(strip1, strip2, duration=15, independent=True)
        
        #for _ in range(6):
        #    result = dice_visualizer_scaled(strip1, color=(0, 255, 0), roll_duration=2, frame_delay=0.08)
        #    print(f"Rolled: {result}")
        #    time.sleep(2)

        # Mirror bounce effect
        mirror_bounce(strip1, strip2, color=(0, 0 , 255), duration=20, speed=0.05)

        # Fireflies effect
        fireflies(strip1, strip2, duration=20, max_fireflies=50, frame_rate=30)

        # Rainbow with sparkles
        rainbow_with_sparkles(strip1, strip2, duration=20, sparkle_chance=0.01)

        # Timer effect
        timer_effect(strip1, strip2, total_time=20, reverse=True)
        
        # Alternate flash with varied colors
        alternate_flash_varied_colors(strip1, strip2,
                                       colors=[(255, 0, 0, 0), (0, 255, 0, 0), (0, 0, 255, 0)],
                                       off=(0, 0, 0, 0),
                                       flashes=10,
                                       delay=0.5)
        
        fire_effect(strip1, strip2, duration=5, cooling=50, sparking=100)
        union_jack_scroll_sparkle(strip1, strip2, duration=5,frame_delay=0.01, sparkle_chance=0)
        matrix_effect(strip1, strip2, duration=5, frame_delay=0.01, trail_length=8)

        # Multi Color wipe animations.
        #multiColorWipe(strip1, strip2, Color(255, 0, 0), Color(255, 0, 0))  # Red wipe
        #multiColorWipe(strip1, strip2, Color(0, 255, 0), Color(0, 255, 0))  # Blue wipe
        #multiColorWipe(strip1, strip2, Color(0, 0, 255), Color(0, 0, 255))  # Green wipe
        #multiColorWipe(strip1, strip2, Color(0, 0, 0, 255), Color(0, 0, 0, 255))  # White wipe

        # Move band
        move_band(strip1, strip2,
                  bandsize = 20, 
                  dir = 1,
                  foreground_colour = (0, 255 , 0, 0 ),
                  background_colour = (255, 0, 0, 0),
                  speed = 4
                 )
        
        # Alternate flash with varied colors    
        alternate_flash_varied_colors(strip1, strip2,
                                       off=(0, 0, 0, 0),
                                       flashes=10,
                                       delay=0.5)
        # Move band in reverse
        move_band(strip1, strip2,
                  bandsize = 20, 
                  dir = -1,
                  foreground_colour = (0, 255 , 0, 0 ),
                  background_colour = (255, 0, 0, 0),
                  speed = 4
                 )
        # Alternate flash with varied colors
        alternate_flash_varied_colors(strip1, strip2,
                                       colors=[(255, 0, 0, 0), (0, 255, 0, 0), (0, 0, 255, 0)],
                                       off=(0, 0, 0, 0),
                                       flashes=10,
                                       delay=0.5)
        # Sparkle effect
        sparkle_dual(strip1, strip2,
                     colorA=(255, 255, 255, 0), colorB=(255, 255, 255, 0),
                     background=(0, 0, 0, 0),
                     sparkles_per_frame=10,
                     duration=2.0, frame_delay=0.05)
        # Sparkle effect with fading

        sparkle_dual_fade(strip1, strip2,
                          background=(0, 0, 0, 0),
                          sparkles_per_frame=10,
                          duration=5.0, frame_delay=0.05, fade_steps=10)
  
