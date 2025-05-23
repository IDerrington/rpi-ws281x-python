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
LED_1_BRIGHTNESS = 50   # Set to 0 for darkest and 255 for brightest
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL = 0       # 0 or 1
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600       # Number of LED pixels.
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA = 9           # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 50   # Set to 0 for darkest and 255 for brightest
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL = 1       # 0 or 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
    strip.show()

def sparkle_dual_fade(stripA, stripB, 
                      background=(0, 0, 0, 0), 
                      sparkles_per_frame=10, 
                      duration=5.0, frame_delay=0.05, fade_steps=10):
    """
    Sparkles with fading random colors on two NeoPixel strips.

    :param stripA/B: NeoPixel strips.
    :param background: Background color to fade to.
    :param sparkles_per_frame: New sparkles per frame per strip.
    :param duration: Total effect duration (seconds).
    :param frame_delay: Delay between frames (seconds).
    :param fade_steps: How many frames a sparkle fades out over.
    """
    import random
    import time

    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    total_frames = int(duration / frame_delay)

    # Active sparkles: list of (pixel index, [r, g, b, w], fade_step)
    activeA, activeB = [], []

    def add_sparkles(active_list):
        indices = random.sample(range(num_pixels), min(sparkles_per_frame, num_pixels))
        for idx in indices:
            color = [random.randint(100, 255) for _ in range(4)]  # Bright random color
            active_list.append((idx, color, 0))

    def fade_and_draw(strip, active_list):
        fill_color(strip, background)
        remaining = []
        for idx, color, step in active_list:
            factor = 1.0 - (step / fade_steps)
            faded = [int(c * factor) for c in color]
            strip.setPixelColor(idx, Color(*faded))
            if step + 1 < fade_steps:
                remaining.append((idx, color, step + 1))
        strip.show()
        return remaining

    for _ in range(total_frames):
        add_sparkles(activeA)
        add_sparkles(activeB)
        activeA = fade_and_draw(stripA, activeA)
        activeB = fade_and_draw(stripB, activeB)
        time.sleep(frame_delay)

def sparkle_dual(stripA, stripB, 
                 colorA=(255, 255, 255, 0), colorB=(255, 255, 255, 0), 
                 background=(0, 0, 0, 0), 
                 sparkles_per_frame=10, 
                 duration=2.0, frame_delay=0.05):
    """
    Apply sparkles to two NeoPixel strips simultaneously.

    :param stripA: First strip.
    :param stripB: Second strip.
    :param colorA: Sparkle color for strip A.
    :param colorB: Sparkle color for strip B.
    :param background: Background color for both strips.
    :param sparkles_per_frame: Sparkles per strip per frame.
    :param duration: Total effect duration (in seconds).
    :param frame_delay: Time between frames (in seconds).
    """
    count = int(duration / frame_delay)
    num_pixels = min(stripA.numPixels(), stripB.numPixels())

    for _ in range(count):
        fill_color(stripA, background)
        fill_color(stripB, background)

        indicesA = random.sample(range(num_pixels), min(sparkles_per_frame, num_pixels))
        indicesB = random.sample(range(num_pixels), min(sparkles_per_frame, num_pixels))

        for i in indicesA:
            stripA.setPixelColor(i, Color(*colorA))
        for i in indicesB:
            stripB.setPixelColor(i, Color(*colorB))

        stripA.show()
        stripB.show()
        time.sleep(frame_delay)

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

        fill_color(stripA,color) 
        fill_color(stripB, off)
        stripA.show()
        stripB.show()
        time.sleep(delay)

        fill_color(stripA, off)
        fill_color(stripB, color)       
        stripA.show()
        stripB.show()
        time.sleep(delay)

def move_band( strip1, strip2,
               bandsize : int = 20, 
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

    num_pixels = len(strip1)
    
    fill_color(strip1, background_colour)
    fill_color(strip2, background_colour)   


    # Create the band
    for idx in range(bandsize):
        if dir > 0:
            strip1[idx] = Color(*foreground_colour)
            strip2[idx] = Color(*foreground_colour)
        if dir < 0:
            strip1 [num_pixels - 1 - idx] = Color(*foreground_colour)
            strip2 [num_pixels - 1 - idx] = Color(*foreground_colour)

    strip1.show()
    strip2.show()    
    
    # Move the band
    for position in range(num_pixels - bandsize -1):
        if dir > 0:
            strip1[position] = Color(*background_colour)
            strip1[bandsize + position] = Color(*foreground_colour)

            strip2[position] = Color(*background_colour)
            strip2[bandsize + position] = Color(*foreground_colour)
        if dir < 0:
            strip1[num_pixels - 1 - position] = Color(*background_colour)
            strip1[num_pixels - bandsize - position -1 ] = Color(*foreground_colour)

            strip2[num_pixels - 1 - position] = Color(*background_colour)
            strip2[num_pixels - bandsize - position -1 ] = Color(*foreground_colour)
        
        if position % speed == 0:
            strip1.show()
            strip2.show()


def multiColorWipe(strip1, strip2, color1, color2, wait_ms=5):
    """Wipe color across multiple LED strips a pixel at a time."""

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

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
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
        multiColorWipe(strip1, strip2, Color(255, 0, 0), Color(255, 0, 0))  # Red wipe
        multiColorWipe(strip1, strip2, Color(0, 255, 0), Color(0, 255, 0))  # Blue wipe
        multiColorWipe(strip1, strip2, Color(0, 0, 255), Color(0, 0, 255))  # Green wipe
        multiColorWipe(strip1, strip2, Color(0, 0, 0, 255), Color(0, 0, 0, 255))  # White wipe

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
  