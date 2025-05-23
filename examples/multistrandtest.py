# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from rpi_ws281x import ws, Color, Adafruit_NeoPixel

# LED strip configuration:
LED_1_COUNT = 600       # Number of LED pixels.
LED_1_PIN = 18          # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3).
LED_1_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_1_DMA = 10          # DMA channel to use for generating signal (Between 1 and 14)
LED_1_BRIGHTNESS = 100   # Set to 0 for darkest and 255 for brightest
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL = 0       # 0 or 1
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600       # Number of LED pixels.
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA = 9           # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 100   # Set to 0 for darkest and 255 for brightest
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL = 1       # 0 or 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

def alternate_flash_varied_colors(stripA, stripB, colors=None, off=(0, 0, 0, 0), flashes=10, delay=0.5):
    """
    Flash two strips alternately with a different color each cycle.

    :param stripA: First NeoPixel strip.
    :param stripB: Second NeoPixel strip.
    :param colors: List of (R, G, B, W) tuples to cycle through.
    :param off: Off color (default = black).
    :param flashes: Number of total flash cycles.
    :param delay: Time between swaps in seconds.
    """
    if colors is None:
        colors = [
            (255, 0, 0, 0),     # Red
            (0, 255, 0, 0),     # Green
            (0, 0, 255, 0),     # Blue
            (255, 255, 0, 0),   # Yellow
            (0, 255, 255, 0),   # Cyan
            (255, 0, 255, 0),   # Magenta
            (0, 0, 0, 255),     # White LED channel only
        ]

    for i in range(flashes):
        color = colors[i % len(colors)]

        stripA.fill(color)
        stripB.fill(off)
        stripA.show()
        stripB.show()
        time.sleep(delay)

        stripA.fill(off)
        stripB.fill(color)
        stripA.show()
        stripB.show()
        time.sleep(delay)

def move_band( bandsize : int = 20, 
               dir = 1,
               foreground_colour = (0, 255 , 0, 0 ),
               background_colour = (255, 0, 0, 0),
               speed = 4
              ):
    """
    A band of colour moves through the strip.   
    
    lpixels:            NeoPixel object
    bandsize:           size of the band
    dir:                direction of the band
    foreground_colour:  colour of the band
    background_colour:  colour of the background
    speed:              speed of the band
    """

    global strip1
    global strip2
    
    strip1.fill(background_colour)
    strip2.show()

    # Create the band
    for idx in range(bandsize):
        if dir > 0:
            strip1[idx] = foreground_colour
            strip2[idx] = foreground_colour
        if dir < 0:
            lpixels [num_pixels - 1 - idx] = foreground_colour

    strip1.show()
    strip2.show()    
    # Move the band
    for position in range(num_pixels - bandsize -1):
        if dir > 0:
            lpixels[position] = background_colour
            lpixels[bandsize + position] = foreground_colour
        if dir < 0:
            lpixels[num_pixels - 1 - position] = background_colour
            lpixels[num_pixels - bandsize - position -1 ] = foreground_colour
        
        if position % speed == 0:
            lpixels.show()

def multiColorWipe(color1, color2, wait_ms=5):
    """Wipe color across multiple LED strips a pixel at a time."""
    global strip1
    global strip2

    for i in range(strip1.numPixels()):
            strip1.setPixelColor(i, color1)
            strip2.setPixelColor(i, color2)
            strip1.show()
            strip2.show()
            #time.sleep(wait_ms / 1000.0)



def blackout(strip):
    for i in range(max(strip.numPixels(), strip.numPixels())):
        strip.setPixelColor(i, Color(0, 0, 0, 0))
    
    strip.show()


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

    # Black out any LEDs that may be still on for the last run
    blackout(strip1)
    blackout(strip2)
    
    while True:
        # Multi Color wipe animations.
        multiColorWipe(Color(255, 0, 0), Color(255, 0, 0))  # Red wipe
        multiColorWipe(Color(0, 255, 0), Color(0, 255, 0))  # Blue wipe
        multiColorWipe(Color(0, 0, 255), Color(0, 0, 255))  # Green wipe
        # multiColorWipe(Color(255, 255, 255), Color(255, 255, 255))  # Composite White wipe
        multiColorWipe(Color(0, 0, 0, 255), Color(0, 0, 0, 255))  # White wipe
        # multiColorWipe(Color(255, 255, 255, 255), Color(255, 255, 255, 255))  # Composite White + White LED wipe
        
        alternate_flash_varied_colors(strip1, strip2, flashes=15, delay=0.3)