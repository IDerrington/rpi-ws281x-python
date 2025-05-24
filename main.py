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
LED_1_FREQ_HZ = 900000  # LED signal frequency in hertz (usually 800khz)
LED_1_DMA = 10          # DMA channel to use for generating signal (Between 1 and 14)
LED_1_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_1_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL = 0       # 0 or 1
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600       # Number of LED pixels.
LED_2_PIN = 13          # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ = 900000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA = 9           # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_2_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL = 1       # 0 or 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
    strip.show()

def mirror_bounce(stripA, stripB=None, color=(0, 0, 255), duration=10, speed=0.05):
    """
    Mirror bounce effect: pulses move from ends to center and back.

    :param stripA: First NeoPixel strip
    :param stripB: Optional second strip
    :param color: RGB tuple for pulse color
    :param duration: Duration in seconds
    :param speed: Delay between frames in seconds
    """
    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    midpoint = num_pixels // 2
    total_steps = midpoint + 1
    start_time = time.time()

    direction = 1  # 1 for inward, -1 for outward
    step = 0

    while time.time() - start_time < duration:
        # Clear strips
        for i in range(num_pixels):
            stripA.setPixelColor(i, Color(0, 0, 0, 0))
            if stripB:
                stripB.setPixelColor(i, Color(0, 0, 0, 0))

        # Draw pulses on both sides
        if direction == 1:
            # Moving inward: light from edges towards center
            if step <= midpoint:
                # Light pixels from both ends up to current step
                for i in range(step + 1):
                    stripA.setPixelColor(i, Color(*color, 0))
                    stripA.setPixelColor(num_pixels - 1 - i, Color(*color, 0))
                    if stripB:
                        stripB.setPixelColor(i, Color(*color, 0))
                        stripB.setPixelColor(num_pixels - 1 - i, Color(*color, 0))
        else:
            # Moving outward: light pulses from center back to ends
            if step <= midpoint:
                for i in range(step, midpoint + 1):
                    stripA.setPixelColor(i, Color(*color, 0))
                    stripA.setPixelColor(num_pixels - 1 - i, Color(*color, 0))
                    if stripB:
                        stripB.setPixelColor(i, Color(*color, 0))
                        stripB.setPixelColor(num_pixels - 1 - i, Color(*color, 0))

        stripA.show()
        if stripB:
            stripB.show()

        step += 1
        if step > total_steps:
            step = 0
            direction *= -1  # Reverse direction

        time.sleep(speed)

def fireflies(stripA, stripB=None, duration=30, max_fireflies=20, frame_rate=30):
    """
    Fireflies effect: random slow twinkles fading in and out.
    
    :param stripA: First NeoPixel strip
    :param stripB: Optional second strip
    :param duration: Duration in seconds
    :param max_fireflies: Max number of simultaneous fireflies
    :param frame_rate: Frames per second
    """
    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    frame_delay = 1.0 / frame_rate
    total_frames = int(duration * frame_rate)

    # Firefly state: each firefly is (pixel_index, brightness, fading_in)
    fireflies = []

    def set_pixel_brightness(pixel, brightness):
        # Fireflies glow soft yellow (255, 255, 100)
        base_color = (255, 255, 100)
        scaled_color = tuple(int(c * brightness) for c in base_color)
        return scaled_color

    for frame in range(total_frames):
        # Occasionally spawn a new firefly if under max count
        if len(fireflies) < max_fireflies and random.random() < 0.1:
            new_pixel = random.randint(0, num_pixels - 1)
            # Avoid spawning multiple fireflies on the same pixel
            if not any(f[0] == new_pixel for f in fireflies):
                fireflies.append([new_pixel, 0.0, True])  # start faded out, fading in

        # Clear strip to black before drawing
        for i in range(num_pixels):
            stripA.setPixelColor(i, Color(0, 0, 0, 0))
            if stripB:
                stripB.setPixelColor(i, Color(0, 0, 0, 0))

        # Update fireflies brightness
        to_remove = []
        for i, (pixel, brightness, fading_in) in enumerate(fireflies):
            if fading_in:
                brightness += 0.02  # fade in speed
                if brightness >= 1.0:
                    brightness = 1.0
                    fading_in = False
            else:
                brightness -= 0.01  # fade out speed
                if brightness <= 0:
                    to_remove.append(i)
                    continue
            fireflies[i] = [pixel, brightness, fading_in]

            # Set pixel color based on brightness
            color = set_pixel_brightness(pixel, brightness)
            stripA.setPixelColor(pixel, Color(*color, 0))
            if stripB:
                stripB.setPixelColor(pixel, Color(*color, 0))

        # Remove fully faded fireflies
        for index in reversed(to_remove):
            fireflies.pop(index)

        stripA.show()
        if stripB:
            stripB.show()
        time.sleep(frame_delay)

def rainbow_with_sparkles(stripA, stripB=None, duration=10, sparkle_chance=0.05, frame_rate=30):
    """
    Displays a flowing rainbow animation with random sparkles on both strips.

    :param stripA: First NeoPixel strip
    :param stripB: Optional second NeoPixel strip
    :param duration: Duration in seconds
    :param sparkle_chance: Chance per pixel per frame to sparkle
    :param frame_rate: Frames per second
    """
    def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    total_frames = int(duration * frame_rate)
    frame_delay = 1.0 / frame_rate
    color_offset = 0

    # Initialize sparkle fade trackers
    sparkle_fade = [0] * num_pixels

    for frame in range(total_frames):
        for i in range(num_pixels):
            # Sparkle logic
            if sparkle_fade[i] > 0:
                brightness = int(sparkle_fade[i] * 255)
                color = (brightness, brightness, brightness)
                sparkle_fade[i] -= 0.1
                if sparkle_fade[i] < 0:
                    sparkle_fade[i] = 0
            elif random.random() < sparkle_chance:
                color = (255, 255, 255)
                sparkle_fade[i] = 1.0
            else:
                # Rainbow color
                pos = (int(i * 256 / num_pixels) + color_offset) & 255
                color = wheel(pos)

            stripA.setPixelColor(i, Color(*color, 0))
            if stripB:
                stripB.setPixelColor(i, Color(*color, 0))

        stripA.show()
        if stripB:
            stripB.show()

        color_offset = (color_offset + 1) % 256
        time.sleep(frame_delay)

def timer_effect(stripA, stripB=None, total_time=10, reverse=False, frame_rate=30):
    """
    Timer countdown effect:
    - 0–50%: Solid Green
    - 50–75%: Fade Green → Amber
    - 75–100%: Fade Amber → Red
    - Final 5s: Flash on/off every 0.5s

    :param stripA: First NeoPixel strip
    :param stripB: Optional second strip
    :param total_time: Duration in seconds
    :param reverse: LEDs turn off over time if True
    :param frame_rate: Frames per second
    """
    import time
    from rpi_ws281x import Color

    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    total_frames = int(total_time * frame_rate)
    frame_delay = 1.0 / frame_rate
    flash_interval_frames = int(0.5 / frame_delay)

    def get_color(progress):
        """Return a color depending on the progress."""
        if progress < 0.5:
            # Solid green
            return (0, 255, 0, 0)
        elif progress < 0.75:
            # Green → Amber (255,191,0)
            t = (progress - 0.5) / 0.25
            r = int(t * 255)
            g = int(255 - t * (255 - 191))
            return (r, g, 0, 0)
        else:
            # Amber → Red
            t = (progress - 0.75) / 0.25
            r = 255
            g = int(191 * (1 - t))
            return (r, g, 0, 0)

    for frame in range(total_frames + 1):
        progress = frame / total_frames
        active_pixels = int(progress * num_pixels)
        if reverse:
            active_pixels = num_pixels - active_pixels

        in_final_5s = frame >= total_frames - (5 * frame_rate)
        flash_off = in_final_5s and ((frame // flash_interval_frames) % 2 == 1)
        color = get_color(progress)

        for i in range(num_pixels):
            if flash_off:
                pixel_color = (0, 0, 0, 0)
            elif (not reverse and i < active_pixels) or (reverse and i >= active_pixels):
                pixel_color = color
            else:
                pixel_color = (0, 0, 0, 0)

            stripA.setPixelColor(i, Color(*pixel_color))
            if stripB:
                stripB.setPixelColor(i, Color(*pixel_color))

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

def dice_visualizer_scaled(strip, roll=None, color=(255, 255, 255), roll_duration=2, frame_delay=0.08):
    """
    Dice visualizer for large LED strips (~600 LEDs), using clusters to form a die face.

    :param strip: NeoPixel strip object
    :param roll: Optional final roll (1-6), random if None
    :param color: RGB color for the dots
    :param roll_duration: Rolling animation duration
    :param frame_delay: Delay between frames during rolling
    :return: The final rolled number
    """
    num_leds = strip.numPixels()
    if num_leds < 90:
        raise ValueError("Requires at least 90 LEDs to look decent.")

    # Define 9 zones (3x3 dice grid), each with a cluster of LEDs
    cluster_size = num_leds // 9
    clusters = [(i * cluster_size, (i + 1) * cluster_size) for i in range(9)]

    # Define which clusters light up for each dice face
    dice_map = {
        1: [4],
        2: [0, 8],
        3: [0, 4, 8],
        4: [0, 2, 6, 8],
        5: [0, 2, 4, 6, 8],
        6: [0, 1, 2, 6, 7, 8],
    }

    def clear_strip():
        for i in range(num_leds):
            strip.setPixelColor(i, Color(0, 0, 0, 0))
        strip.show()

    def show_roll(roll_number):
        clear_strip()
        for idx in dice_map[roll_number]:
            start, end = clusters[idx]
            for i in range(start, end):
                strip.setPixelColor(i, Color(*color, 0))
        strip.show()

    # Rolling animation
    end_time = time.time() + roll_duration
    while time.time() < end_time:
        temp_roll = random.randint(1, 6)
        show_roll(temp_roll)
        time.sleep(frame_delay)

    # Final roll
    final_roll = roll if roll else random.randint(1, 6)
    show_roll(final_roll)
    time.sleep(2)
    clear_strip()

    return final_roll

import time
import math
import random
from rpi_ws281x import Color

def wave_ripple_dual(strip1, strip2, duration=10, speed=0.05, ripple_spacing=15, fade_factor=0.85, color_cycle=True, independent=False):
    """
    Dual-strip ripple effect for NeoPixel strips (~600 LEDs).

    :param strip1: First NeoPixel strip object
    :param strip2: Second NeoPixel strip object
    :param duration: Total time to run the effect
    :param speed: Delay between frames
    :param ripple_spacing: Distance between ripple rings
    :param fade_factor: Ripple brightness fade factor
    :param color_cycle: Enable color cycling
    :param independent: If True, run separate ripple events for each strip
    """
    def get_color(angle):
        i = int(angle * 256 * 6)
        if i < 256:
            return (255, i, 0)
        elif i < 512:
            return (255 - (i - 256), 255, 0)
        elif i < 768:
            return (0, 255, i - 512)
        elif i < 1024:
            return (0, 255 - (i - 768), 255)
        elif i < 1280:
            return (i - 1024, 0, 255)
        else:
            return (255, 0, 255 - (i - 1280))

    def clear(strip):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0, 0))

    def update_ripples(strip, ripples):
        num_leds = strip.numPixels()
        new_ripples = []
        for ripple in ripples:
            center = ripple['center']
            age = ripple['age']
            r, g, b = ripple['color']

            for offset in range(0, num_leds, ripple_spacing):
                for sign in [-1, 1]:
                    pos = center + sign * (age + offset)
                    if 0 <= pos < num_leds:
                        decay = fade_factor ** (offset // ripple_spacing + 1)
                        strip.setPixelColor(pos, Color(int(r * decay), int(g * decay), int(b * decay), 0))

            ripple['age'] += 1
            if ripple['age'] < num_leds:
                new_ripples.append(ripple)

        return new_ripples

    num_leds_1 = strip1.numPixels()
    num_leds_2 = strip2.numPixels()
    ripples1 = []
    ripples2 = [] if independent else ripples1

    start_time = time.time()
    while time.time() - start_time < duration:
        clear(strip1)
        clear(strip2)

        # Occasionally start a ripple
        if random.random() < 0.05:
            center = random.randint(0, num_leds_1 - 1)
            color = get_color(random.random()) if color_cycle else (0, 128, 255)
            ripple = {'center': center, 'age': 0, 'color': color}
            ripples1.append(ripple)
            if independent:
                # Optional second ripple for strip2
                if random.random() < 0.8:
                    center2 = random.randint(0, num_leds_2 - 1)
                    color2 = get_color(random.random()) if color_cycle else (255, 100, 0)
                    ripples2.append({'center': center2, 'age': 0, 'color': color2})

        ripples1 = update_ripples(strip1, ripples1)
        ripples2 = update_ripples(strip2, ripples2)
        strip1.show()
        strip2.show()
        time.sleep(speed)

    clear(strip1)
    clear(strip2)
    strip1.show()
    strip2.show()

import time
import random
from rpi_ws281x import Color

import time
import random
from rpi_ws281x import Color

def color_bounce(strip1, strip2, duration=15, num_bouncers=3, speed=0.001,
                 independent=False, change_color_on_bounce=True, bar_size=5):
    """
    Color bouncing effect on two NeoPixel strips.
    :param strip1: First NeoPixel strip object
    :param strip2: Second NeoPixel strip object 
    """ 

    num_leds_1 = strip1.numPixels()
    num_leds_2 = strip2.numPixels()

    def get_random_color():
        return tuple(random.randint(100, 255) for _ in range(3))

    def clear(strip):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))

    def init_bouncers(num_leds, count):
        return [{
            'pos': random.randint(0, num_leds - 1),
            'dir': random.choice([-1, 1]),
            'color': get_random_color()
        } for _ in range(count)]

    bouncers1 = init_bouncers(num_leds_1, num_bouncers)
    bouncers2 = init_bouncers(num_leds_2, num_bouncers) if independent else bouncers1

    start_time = time.time()

    while time.time() - start_time < duration:
        clear(strip1)
        clear(strip2)

        # Draw bars on strip1
        for bouncer in bouncers1:
            r, g, b = bouncer['color']
            center = int(bouncer['pos'])
            for offset in range(-(bar_size // 2), bar_size // 2 + 1):
                pos = center + offset
                if 0 <= pos < num_leds_1:
                    strip1.setPixelColor(pos, Color(r, g, b))

        # Draw bars on strip2
        for bouncer in bouncers2:
            r, g, b = bouncer['color']
            center = int(bouncer['pos'])
            for offset in range(-(bar_size // 2), bar_size // 2 + 1):
                pos = center + offset
                if 0 <= pos < num_leds_2:
                    strip2.setPixelColor(pos, Color(r, g, b))

        strip1.show()
        strip2.show()

        # Update positions and directions
        for bouncer in bouncers1:
            bouncer['pos'] += bouncer['dir']
            if bouncer['pos'] >= num_leds_1 or bouncer['pos'] < 0:
                bouncer['dir'] *= -1
                bouncer['pos'] += bouncer['dir'] * 2
                if change_color_on_bounce:
                    bouncer['color'] = get_random_color()

        if independent:
            for bouncer in bouncers2:
                bouncer['pos'] += bouncer['dir']
                if bouncer['pos'] >= num_leds_2 or bouncer['pos'] < 0:
                    bouncer['dir'] *= -1
                    bouncer['pos'] += bouncer['dir'] * 2
                    if change_color_on_bounce:
                        bouncer['color'] = get_random_color()

        time.sleep(speed)

    clear(strip1)
    clear(strip2)
    strip1.show()
    strip2.show()


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
  