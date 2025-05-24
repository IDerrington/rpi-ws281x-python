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
LED_1_BRIGHTNESS = 200   # Set to 0 for darkest and 255 for brightest
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL = 0       # 0 or 1
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600       # Number of LED pixels.
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA = 9           # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 200   # Set to 0 for darkest and 255 for brightest
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL = 1       # 0 or 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
    strip.show()

def timer_effect(stripA, stripB=None, total_time=10, reverse=False, color=(0, 255, 0, 0), bg_color=(0, 0, 0, 0), frame_rate=30):
    """
    Display a timer progress effect on one or two LED strips.
    
    :param stripA: First NeoPixel strip.
    :param stripB: (Optional) Second NeoPixel strip.
    :param total_time: Total countdown time (seconds).
    :param reverse: If True, lights turn off as time progresses.
    :param color: Foreground color (e.g. (0,255,0,0) for green).
    :param bg_color: Background color (default off).
    :param frame_rate: Updates per second.
    """
    import time
    from rpi_ws281x import Color

    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    total_frames = total_time * frame_rate
    frame_delay = 1.0 / frame_rate

    for frame in range(total_frames + 1):
        # Calculate progress (0.0 to 1.0)
        progress = frame / total_frames
        active_pixels = int(progress * num_pixels)

        if reverse:
            active_pixels = num_pixels - active_pixels

        for i in range(num_pixels):
            if (not reverse and i < active_pixels) or (reverse and i >= active_pixels):
                stripA.setPixelColor(i, Color(*color))
                if stripB:
                    stripB.setPixelColor(i, Color(*color))
            else:
                stripA.setPixelColor(i, Color(*bg_color))
                if stripB:
                    stripB.setPixelColor(i, Color(*bg_color))

        stripA.show()
        if stripB:
            stripB.show()

        time.sleep(frame_delay)

def fire_effect(stripA, stripB, duration=10.0, cooling=55, sparking=120, frame_delay=0.03):
    """
    Fire effect on two NeoPixel strips (based on Fire2012 by Mark Kriegsman).
    
    :param stripA: First NeoPixel strip
    :param stripB: Second NeoPixel strip
    :param duration: Total duration to run the effect (in seconds)
    :param cooling: Rate at which heat cools (higher = more cooling)
    :param sparking: Chance of new sparks (0–255, higher = more sparks)
    :param frame_delay: Delay between frames (in seconds)
    """
    import time, random
    from rpi_ws281x import Color

    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    heatA = [0] * num_pixels
    heatB = [0] * num_pixels
    total_frames = int(duration / frame_delay)

    def heat_to_color(heat):
        """Convert heat value (0–255) to flame color."""
        t192 = (heat * 191) // 255

        heatramp = t192 & 63  # 0..63
        heatramp <<= 2        # scale up to 0..252

        if t192 > 128:
            return (255, 255, heatramp, 0)  # White-ish
        elif t192 > 64:
            return (255, heatramp, 0, 0)    # Orange
        else:
            return (heatramp, 0, 0, 0)      # Red

    def update_fire(heat, strip):
        # Step 1: Cool down every cell a little
        for i in range(num_pixels):
            cool = random.randint(0, (cooling * 10) // num_pixels + 2)
            heat[i] = max(0, heat[i] - cool)

        # Step 2: Heat diffusion upward
        for k in range(num_pixels - 1, 2, -1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3: Spark new heat near the bottom
        if random.randint(0, 255) < sparking:
            y = random.randint(0, 6)
            heat[y] = min(255, heat[y] + random.randint(160, 255))

        # Step 4: Map heat to color and write to LEDs
        for j in range(num_pixels):
            color = heat_to_color(heat[j])
            strip.setPixelColor(j, Color(*color))
        strip.show()

    for _ in range(total_frames):
        update_fire(heatA, stripA)
        update_fire(heatB, stripB)
        time.sleep(frame_delay)

def union_jack_scroll_sparkle(stripA, stripB, duration=10.0, frame_delay=0.05, sparkle_chance=0.1, fade_steps=8):
    """
    Stylized scrolling Union Jack effect with sparkles on two NeoPixel strips.

    :param stripA: First NeoPixel strip (Adafruit_NeoPixel).
    :param stripB: Second NeoPixel strip.
    :param duration: Total run time in seconds.
    :param frame_delay: Time between frames (seconds).
    :param sparkle_chance: Chance per pixel per frame for a sparkle.
    :param fade_steps: How long sparkles fade (in frames).
    """
    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    total_frames = int(duration / frame_delay)

    # Color definitions
    RED   = (255, 0, 0, 0)
    WHITE = (255, 255, 255, 0)
    BLUE  = (0, 0, 255, 0)
    BG    = BLUE   # background color
    CROSS = RED    # cross color
    EDGE  = WHITE  # outer diagonal white pattern

    # Union Jack stylized 1D pattern (scrollable)
    pattern = [BG, BG, CROSS, EDGE, CROSS, BG, BG]  # 7-pixel loop

    # Sparkles as lists of [pixel_index, [r, g, b, w], step]
    sparklesA = []
    sparklesB = []

    def update_strip(strip, frame, sparkles):
        # Scroll pattern across the strip
        for i in range(num_pixels):
            color = pattern[(frame + i) % len(pattern)]
            strip.setPixelColor(i, Color(*color))

        # Possibly add new sparkles
        for _ in range(num_pixels):
            if random.random() < sparkle_chance:
                idx = random.randint(0, num_pixels - 1)
                color = [random.randint(180, 255) for _ in range(4)]
                sparkles.append([idx, color, 0])

        # Draw and fade sparkles
        next_sparkles = []
        for idx, col, step in sparkles:
            fade_factor = max(0, 1.0 - (step / fade_steps))
            faded = [int(c * fade_factor) for c in col]
            strip.setPixelColor(idx, Color(*faded))
            if step + 1 < fade_steps:
                next_sparkles.append([idx, col, step + 1])

        strip.show()
        return next_sparkles

    # Main loop
    for frame in range(total_frames):
        sparklesA = update_strip(stripA, frame, sparklesA)
        sparklesB = update_strip(stripB, frame, sparklesB)
        time.sleep(frame_delay)


def matrix_effect(stripA, stripB, 
                  duration=10.0, frame_delay=0.05, 
                  trail_length=10):
    """
    Matrix rain effect on two NeoPixel strips.
    
    :param stripA: First NeoPixel strip.
    :param stripB: Second NeoPixel strip.
    :param duration: Total time to run effect (seconds).
    :param frame_delay: Delay between frames (seconds).
    :param trail_length: How many LEDs the trail lasts.
    """

    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    total_frames = int(duration / frame_delay)

    # Each strip keeps a list of active drops, each drop = current head position
    dropsA = []
    dropsB = []

    for frame in range(total_frames):
        # Occasionally start a new drop with some probability
        if random.random() < 0.3:  # Adjust frequency
            dropsA.append(0)  # new drop starts at the top pixel index 0
        if random.random() < 0.3:
            dropsB.append(0)

        # Clear strips (fade previous frame by dimming)
        for i in range(num_pixels):
            # Fade every pixel by some factor (dimming trail)
            for strip in (stripA, stripB):
                # Get current color and fade it down
                # Unfortunately Adafruit_NeoPixel doesn't have getPixelColor with RGBA tuple,
                # so we approximate by storing colors ourselves or just fade by setting a dim green.
                # Here we just set background as near black.
                strip.setPixelColor(i, Color(0, 30, 0, 0))  # dark green fade

        # Update and draw drops for strip A
        new_dropsA = []
        for head in dropsA:
            # Draw head pixel bright green
            stripA.setPixelColor(head, Color(0, 255, 0, 0))
            # Draw trail behind the head, gradually dimmer
            for t in range(1, trail_length):
                trail_pos = head - t
                if 0 <= trail_pos < num_pixels:
                    brightness = max(0, 255 - (255 // trail_length) * t)
                    stripA.setPixelColor(trail_pos, Color(0, brightness, 0, 0))
            # Move drop down
            if head + 1 < num_pixels:
                new_dropsA.append(head + 1)
        dropsA = new_dropsA

        # Update and draw drops for strip B
        new_dropsB = []
        for head in dropsB:
            stripB.setPixelColor(head, Color(0, 255, 0, 0))
            for t in range(1, trail_length):
                trail_pos = head - t
                if 0 <= trail_pos < num_pixels:
                    brightness = max(0, 255 - (255 // trail_length) * t)
                    stripB.setPixelColor(trail_pos, Color(0, brightness, 0, 0))
            if head + 1 < num_pixels:
                new_dropsB.append(head + 1)
        dropsB = new_dropsB

        stripA.show()
        stripB.show()
        #time.sleep(frame_delay)

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

        timer_effect(strip1, strip2, total_time=60, reverse=True, color=(0, 255, 0, 0))
        fire_effect(strip1, strip2, duration=5, cooling=50, sparking=100)
        union_jack_scroll_sparkle(strip1, strip2, duration=5,frame_delay=0.01, sparkle_chance=0)
        matrix_effect(strip1, strip2, duration=15, frame_delay=0.01, trail_length=8)

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
  