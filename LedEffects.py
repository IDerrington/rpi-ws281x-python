import time
import random
from rpi_ws281x import Color
import colorsys
import math
import time

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
    strip.show()

import time
import math
import random
from rpi_ws281x import Color

def sinister_pulse(strip1, strip2, duration: float = 20.0, fps: int = 30):
    """
    Sinister pulse effect for Blood on the Clocktower atmosphere.
    Pulses dark red/purple, occasionally scans a bright "eye".
    :param strip1: First NeoPixel strip
    :param strip2: Second NeoPixel strip
    :param duration: Duration to run the effect (seconds)
    :param fps: Frames per second
    """
    num_leds = strip1.numPixels()
    start_time = time.time()
    frame_delay = 1.0 / fps
    phase = 0.0
    eye_active = False
    eye_position = 0
    eye_direction = 1
    next_eye_time = time.time() + random.uniform(3.0, 8.0)

    def pulse_color(intensity):
        # Base red/purple tone with low intensity
        r = int(40 + 100 * intensity)
        g = 0
        b = int(40 + 60 * intensity)
        w = 0
        return Color(r, g, b, w)

    while time.time() - start_time < duration:
        frame_start = time.perf_counter()

        # Breathing effect using sine wave
        intensity = (1 + math.sin(phase)) / 2  # Range [0, 1]
        base_color = pulse_color(intensity)

        for i in range(num_leds):
            strip1.setPixelColor(i, base_color)
            strip2.setPixelColor(i, base_color)

        # Occasionally scan an "eye" of bright red
        if eye_active:
            eye_col = Color(255, 0, 0, 50)
            if 0 <= eye_position < num_leds:
                strip1.setPixelColor(eye_position, eye_col)
                strip2.setPixelColor(eye_position, eye_col)
            eye_position += eye_direction
            if eye_position >= num_leds or eye_position < 0:
                eye_active = False
                next_eye_time = time.time() + random.uniform(3.0, 8.0)
        elif time.time() >= next_eye_time:
            eye_active = True
            eye_position = 0 if random.random() < 0.5 else num_leds - 1
            eye_direction = 1 if eye_position == 0 else -1

        strip1.show()
        strip2.show()

        phase += 0.1

        # Maintain consistent FPS
        elapsed = time.perf_counter() - frame_start
        sleep_time = frame_delay - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

def morse_band_scroll(strip1, strip2, text, duration=10, direction=1, fps=30):
    """
    Scroll a Morse code message across two LED strips in a flashing band.

    :param strip1: First NeoPixel strip
    :param strip2: Second NeoPixel strip
    :param text: The text to scroll in Morse code
    :param duration: Duration to run the effect (seconds)
    :param direction: 1 = left-to-right, -1 = right-to-left
    :param fps: Frames per second
    """
    # Define Morse code dictionary
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
        'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
        'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----',
        ' ': ' '
    }

    # Union Jack color theme
    COLORS = {
        'dot': (255, 0, 0, 0),    # Red
        'dash': (0, 0, 255, 0),   # Blue
        'off': (0, 0, 0, 0),      # Black / off
        'bg': (0, 0, 0, 0),       # Background
        'flash': (255, 255, 255, 0)  # White for flashing edge
    }

    def text_to_morse_pattern(text):
        pattern = []
        for char in text.upper():
            morse = MORSE_CODE.get(char, '')
            for symbol in morse:
                if symbol == '.':
                    pattern += ['dot'] * 2 + ['off'] * 2
                elif symbol == '-':
                    pattern += ['dash'] * 6 + ['off'] * 2
            pattern += ['off'] * 4  # inter-character space
        return pattern

    # Convert text to morse pattern
    morse_pattern = text_to_morse_pattern(text)

    num_pixels = strip1.numPixels()
    band_width = 10
    frame_delay = 1.0 / fps
    start_time = time.time()

    # Pad pattern and duplicate for scrolling
    scroll_pattern = ['off'] * num_pixels + morse_pattern + ['off'] * num_pixels
    if direction < 0:
        scroll_pattern = list(reversed(scroll_pattern))
    pattern_len = len(scroll_pattern)

    offset = 0
    while time.time() - start_time < duration:
        frame_start = time.perf_counter()

        # Determine center of band
        band_center = offset % (pattern_len + num_pixels)
        for i in range(num_pixels):
            pos = i if direction > 0 else num_pixels - 1 - i
            pattern_index = (band_center - band_width // 2 + i) % pattern_len

            symbol = scroll_pattern[pattern_index] if 0 <= pattern_index < pattern_len else 'off'
            color = COLORS.get(symbol, COLORS['bg'])

            # Add a white flashing edge
            if i == (num_pixels - band_width) // 2 or i == (num_pixels + band_width) // 2:
                color = COLORS['flash']

            strip1.setPixelColor(pos, Color(*color))
            strip2.setPixelColor(pos, Color(*color))

        strip1.show()
        strip2.show()

        offset = (offset + 1) % pattern_len

        frame_elapsed = time.perf_counter() - frame_start
        sleep_time = frame_delay - frame_elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)



def mirror_bounce(stripA, stripB=None, color=(0, 0, 255, 0), duration=10):
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
                    stripA.setPixelColor(i, Color(*color))
                    stripA.setPixelColor(num_pixels - 1 - i, Color(*color))
                    if stripB:
                        stripB.setPixelColor(i, Color(*color))
                        stripB.setPixelColor(num_pixels - 1 - i, Color(*color))
        else:
            # Moving outward: light pulses from center back to ends
            if step <= midpoint:
                for i in range(step, midpoint + 1):
                    stripA.setPixelColor(i, Color(*color, 0))
                    stripA.setPixelColor(num_pixels - 1 - i, Color(*color))
                    if stripB:
                        stripB.setPixelColor(i, Color(*color, 0))
                        stripB.setPixelColor(num_pixels - 1 - i, Color(*color))

        stripA.show()
        if stripB:
            stripB.show()

        step += 1
        if step > total_steps:
            step = 0
            direction *= -1  # Reverse direction

        #time.sleep(speed)

def fireflies(stripA, stripB=None, duration=30, max_fireflies=20, frame_rate=30):
    """
    Fireflies effect: random slow twinkles fading in and out.
    
    :param stripA: First NeoPixel strip
    :param stripB: Optional second strip
    :param duration: Duration in seconds
    :param max_fireflies: Max number of simultaneous fireflies
    :param frame_rate: Frames per second
    """
    
    start_time = time.time()
    
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

    while time.time() - start_time < duration:
        # start = time.perf_counter()
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

        #end = time.perf_counter()
        #print(f"Function took {end - start:.6f} seconds")

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

    start_time = time.time()

    while time.time() - start_time < duration:
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
        #time.sleep(frame_delay)



 
def timer_effect(stripA, stripB=None, duration=10, reverse=False, frame_rate=30):
    """
    Timer countdown effect with real-time timing and consistent frame rate.
    :param stripA: First NeoPixel strip
    :param stripB: Optional second NeoPixel strip
    :param duration: Total duration in seconds
    :param reverse: If True, counts down from duration to 0
    :param frame_rate: Frames per second for smooth animation
    """
    start_time = time.time()
    num_pixels = stripA.numPixels()
    if stripB:
        num_pixels = min(num_pixels, stripB.numPixels())

    frame_delay = 1.0 / frame_rate
    last_flash_time = 0
    flash_state = True

    while True:
        frame_start = time.time()

        elapsed = frame_start - start_time
        if elapsed >= duration:
            break

        progress = elapsed / duration
        active_pixels = int(progress * num_pixels)
        if reverse:
            active_pixels = num_pixels - active_pixels

        # Flash logic (toggle every 0.5s in last 5 seconds)
        if elapsed >= duration - 5:
            if frame_start - last_flash_time >= 0.5:
                flash_state = not flash_state
                last_flash_time = frame_start
        else:
            flash_state = True

        # Determine color based on progress
        if progress < 0.5:
            color = (0, 255, 0, 0)
        elif progress < 0.75:
            t = (progress - 0.5) / 0.25
            r = int(t * 255)
            g = int(255 - t * (255 - 191))
            color = (r, g, 0, 0)
        else:
            t = (progress - 0.75) / 0.25
            r = 255
            g = int(191 * (1 - t))
            color = (r, g, 0, 0)

        # Set pixels
        for i in range(num_pixels):
            if not flash_state:
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

        # Maintain consistent frame rate
        frame_end = time.time()
        elapsed_frame_time = frame_end - frame_start
        sleep_time = frame_delay - elapsed_frame_time
        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.3f} seconds to maintain frame rate")
            time.sleep(sleep_time)



def fire_effect(stripA, stripB, duration=10.0, cooling=55, sparking=120, frame_rate=30):
    """
    Fire effect on two NeoPixel strips (based on Fire2012 by Mark Kriegsman),
    with accurate timing using frame rate and processing time compensation.

    :param stripA: First NeoPixel strip
    :param stripB: Second NeoPixel strip
    :param duration: Total duration to run the effect (in seconds)
    :param cooling: Rate at which heat cools (higher = more cooling)
    :param sparking: Chance of new sparks (0–255, higher = more sparks)
    :param frame_rate: Desired frames per second
    """
    import time, random
    from rpi_ws281x import Color

    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    heatA = [0] * num_pixels
    heatB = [0] * num_pixels
    frame_delay = 1.0 / frame_rate
    start_time = time.time()

    def heat_to_color(heat):
        """Convert heat value (0–255) to flame color."""
        t192 = (heat * 191) // 255
        heatramp = (t192 & 63) << 2  # scale up to 0–252

        if t192 > 128:
            return (255, 255, heatramp, 0)  # White-ish
        elif t192 > 64:
            return (255, heatramp, 0, 0)    # Orange
        else:
            return (heatramp, 0, 0, 0)      # Red

    def update_fire(heat, strip):
        # Step 1: Cool down
        for i in range(num_pixels):
            cool = random.randint(0, (cooling * 10) // num_pixels + 2)
            heat[i] = max(0, heat[i] - cool)

        # Step 2: Heat diffusion
        for k in range(num_pixels - 1, 2, -1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3: Sparking
        if random.randint(0, 255) < sparking:
            y = random.randint(0, 6)
            heat[y] = min(255, heat[y] + random.randint(160, 255))

        # Step 4: Map heat to color
        for j in range(num_pixels):
            color = heat_to_color(heat[j])
            strip.setPixelColor(j, Color(*color))
        strip.show()

    while (time.time() - start_time) < duration:
        frame_start = time.time()

        update_fire(heatA, stripA)
        update_fire(heatB, stripB)

        frame_end = time.time()
        elapsed = frame_end - frame_start
        sleep_time = frame_delay - elapsed
        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.3f} seconds to maintain frame rate")
            time.sleep(sleep_time)


def union_jack_scroll_sparkle(stripA, stripB, duration=10.0, frame_rate=20, sparkle_chance=0.1, fade_steps=8):
    """
    Stylized scrolling Union Jack effect with sparkles on two NeoPixel strips.

    :param stripA: First NeoPixel strip (Adafruit_NeoPixel).
    :param stripB: Second NeoPixel strip.
    :param duration: Total run time in seconds.
    :param frame_rate: Frames per second.
    :param sparkle_chance: Chance per pixel per frame for a sparkle.
    :param fade_steps: How long sparkles fade (in frames).
    """
    num_pixels = min(stripA.numPixels(), stripB.numPixels())
    frame_delay = 1.0 / frame_rate
    start_time = time.time()

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

    frame = 0
    while time.time() - start_time < duration:
        frame_start = time.time()

        sparklesA = update_strip(stripA, frame, sparklesA)
        sparklesB = update_strip(stripB, frame, sparklesB)

        frame += 1
        elapsed = time.time() - frame_start
        sleep_time = frame_delay - elapsed
        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.3f} seconds to maintain frame rate")
            time.sleep(sleep_time)


def matrix_effect(stripA, stripB, duration=10.0, frame_rate=30, min_trail=8, max_trail=20, reverse=False):

    rand1 = 20
    rand2 = 30
    frame_time = 1.0 / frame_rate
    start_time = time.perf_counter()
    num_pixels = min(stripA.numPixels(), stripB.numPixels())

    dropsA = []
    dropsB = []

    def brightness_curve(i, trail_length):
        # Exponential fade for smoother falloff
        return int(200 * (0.6 ** i))

    # Color phase timing variables
    color_phase = 'green'  # start phase
    next_phase_time = start_time + random.uniform(rand1, rand2)  # initial random duration

    while True:
        frame_start = time.perf_counter()
        elapsed = frame_start - start_time
        if elapsed >= duration:
            break

        # Switch color phase if time elapsed
        if frame_start >= next_phase_time:
            color_phase = 'blue' if color_phase == 'green' else 'green'
            next_phase_time = frame_start + random.uniform(rand1, rand2)

        # Possibly add new drops to each strip
        if random.random() < 0.3:
            dropsA.append({
                'head': (num_pixels - 1 if reverse else 0),
                'trail': random.randint(min_trail, max_trail)
            })
        if random.random() < 0.3:
            dropsB.append({
                'head': (num_pixels - 1 if reverse else 0),
                'trail': random.randint(min_trail, max_trail)
            })

        # Clear background to very dark green
        for i in range(num_pixels):
            stripA.setPixelColor(i, Color(0, 8, 0, 0))  # Very dark green background
            stripB.setPixelColor(i, Color(0, 8, 0, 0))

        def update_drops(drops, strip):
            new_drops = []
            for drop in drops:
                head = drop['head']
                trail = drop['trail']

                # Draw head (bright white-green)
                strip.setPixelColor(head, Color(180, 255, 180, 0))

                # Draw trail with flicker & exponential fade
                for i in range(1, trail + 1):
                    pos = head + i if reverse else head - i
                    if 0 <= pos < num_pixels:
                        base_brightness = brightness_curve(i, trail)
                        flicker = random.randint(-30, 30)
                        brightness = max(0, min(255, base_brightness + flicker))

                        if color_phase == 'green':
                            r = 0
                            g = brightness
                            b = brightness // 3  # greenish with blue tint
                        else:
                            # Shifted to bluish shades
                            r = brightness // 4
                            g = brightness // 2
                            b = brightness

                        strip.setPixelColor(pos, Color(r, g, b, 0))

                # Move head position
                next_head = head - 1 if reverse else head + 1
                if 0 <= next_head < num_pixels:
                    drop['head'] = next_head
                    new_drops.append(drop)
            return new_drops

        dropsA = update_drops(dropsA, stripA)
        dropsB = update_drops(dropsB, stripB)

        stripA.show()
        stripB.show()

        # Maintain frame rate accounting for processing time
        time_to_sleep = frame_time - (time.perf_counter() - frame_start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)




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


def sparkle_dual_fade(stripA, stripB, 
                      colorA=(0, 0, 0, 255), colorB=(0, 0, 0, 255), 
                      background=(0, 0, 0, 0), 
                      sparkles_per_frame=5, 
                      fade_steps=10, 
                      duration=5.0, frame_rate=30):
    """
    Sparkles with fading on two NeoPixel strips.

    :param stripA: First strip.
    :param stripB: Second strip.
    :param colorA: Base sparkle color for strip A.
    :param colorB: Base sparkle color for strip B.
    :param background: Background color.
    :param sparkles_per_frame: How many new sparkles per frame per strip.
    :param fade_steps: How many frames for sparkle to fade out.
    :param duration: Total run time in seconds.
    :param frame_rate: Frames per second.
    """
    def scale_color(color, scale):
        """Scale RGBW tuple by scale (0.0 to 1.0)."""
        return tuple(int(c * scale) for c in color)
    
    frame_time = 1.0 / frame_rate
    start_time = time.perf_counter()
    num_pixels = min(stripA.numPixels(), stripB.numPixels())

    sparklesA = []  # list of [index, age]
    sparklesB = []

    while True:
        frame_start = time.perf_counter()
        if frame_start - start_time >= duration:
            break

        # Clear background first
        fill_color(stripA, background)
        fill_color(stripB, background)

        # Add new sparkles randomly on strip A
        for _ in range(sparkles_per_frame):
            idx = random.randint(0, num_pixels - 1)
            sparklesA.append([idx, 0])  # age = 0

        # Add new sparkles randomly on strip B
        for _ in range(sparkles_per_frame):
            idx = random.randint(0, num_pixels - 1)
            sparklesB.append([idx, 0])

        # Draw and update sparkles on strip A
        new_sparklesA = []
        for idx, age in sparklesA:
            if age <= fade_steps:
                brightness = 1.0 - (age / fade_steps)
                color = scale_color(colorA, brightness)
                stripA.setPixelColor(idx, Color(*color))
                new_sparklesA.append([idx, age + 1])

        # Draw and update sparkles on strip B
        new_sparklesB = []
        for idx, age in sparklesB:
            if age <= fade_steps:
                brightness = 1.0 - (age / fade_steps)
                color = scale_color(colorB, brightness)
                stripB.setPixelColor(idx, Color(*color))
                new_sparklesB.append([idx, age + 1])

        sparklesA = new_sparklesA
        sparklesB = new_sparklesB

        stripA.show()
        stripB.show()

        # Maintain consistent frame rate
        elapsed = time.perf_counter() - frame_start
        sleep_time = frame_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

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
            (255, 255, 255, 0), # White (all RGB channels)
        ]

    for i in range(flashes):
        cycle_start = time.perf_counter()
        color = colors[i % len(colors)]

        fill_color(stripA, color)
        fill_color(stripB, off)
        stripA.show()
        stripB.show()

        # Wait remaining time considering processing
        elapsed = time.perf_counter() - cycle_start
        to_sleep = delay - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)

        cycle_start = time.perf_counter()
        fill_color(stripA, off)
        fill_color(stripB, color)
        stripA.show()
        stripB.show()

        elapsed = time.perf_counter() - cycle_start
        to_sleep = delay - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)


def move_band(strip1, strip2,
              bandsize: int = 20,
              dir: int = 1,
              foreground_colour=(0, 255, 0, 0),
              background_colour=(255, 0, 0, 0),
              speed: float = 0.1):
    """
    Move a band of colour through two NeoPixel strips, accounting for processing time.

    :param strip1: First NeoPixel strip
    :param strip2: Second NeoPixel strip
    :param bandsize: Size of the moving band (number of LEDs)
    :param dir: Direction (1 for forward, -1 for backward)
    :param foreground_colour: Color of the band (RGBA tuple)
    :param background_colour: Color of the background (RGBA tuple)
    :param speed: Desired time delay between moves (seconds, smaller = faster)
    """
    num_pixels = strip1.numPixels()

    fill_color(strip1, background_colour)
    fill_color(strip2, background_colour)

    if dir > 0:
        start_pos = 0
        end_pos = num_pixels - bandsize
        step = 1
    else:
        start_pos = num_pixels - bandsize
        end_pos = 0
        step = -1

    # Draw initial band
    for i in range(bandsize):
        pos = start_pos + i * dir
        strip1.setPixelColor(pos, Color(*foreground_colour))
        strip2.setPixelColor(pos, Color(*foreground_colour))
    strip1.show()
    strip2.show()

    pos = start_pos
    while pos != end_pos + step:
        frame_start = time.perf_counter()

        trailing_pixel = pos - dir
        if 0 <= trailing_pixel < num_pixels:
            strip1.setPixelColor(trailing_pixel, Color(*background_colour))
            strip2.setPixelColor(trailing_pixel, Color(*background_colour))

        leading_pixel = pos + bandsize * dir
        if 0 <= leading_pixel < num_pixels:
            strip1.setPixelColor(leading_pixel, Color(*foreground_colour))
            strip2.setPixelColor(leading_pixel, Color(*foreground_colour))

        strip1.show()
        strip2.show()

        pos += step

        frame_end = time.perf_counter()
        elapsed = frame_end - frame_start
        sleep_time = speed - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


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



def color_wave_brightness(strip1, strip2, duration=15, fps=60,
                          wave_speed=0.2, wave_frequency=2.0):
    """
    Slowly changes color while varying brightness across the strips in a wave pattern.
    Uses precise timing and compensates for processing overhead.
    
    :param strip1: First NeoPixel strip
    :param strip2: Second NeoPixel strip
    :param duration: Total duration of effect in seconds
    :param fps: Target frames per second
    :param wave_speed: Speed of the brightness wave (cycles/sec)
    :param wave_frequency: Number of wave peaks across the strip
    """
    num_pixels = strip1.numPixels()
    frame_interval = 1 / fps
    start_time = time.perf_counter()

    def apply_wave(strip, base_color, t):
        for i in range(strip.numPixels()):
            x = i / strip.numPixels()
            angle = 2 * math.pi * (wave_frequency * x + wave_speed * t)
            brightness = (math.sin(angle) + 1) / 2

            r = int(base_color[0] * brightness)
            g = int(base_color[1] * brightness)
            b = int(base_color[2] * brightness)
            w = int(base_color[3] * brightness)

            strip.setPixelColor(i, Color(r, g, b, w))
        strip.show()

    while True:
        now = time.perf_counter()
        elapsed = now - start_time
        if elapsed > duration:
            break

        # Hue cycles at 1 cycle every 10 seconds
        hue = (elapsed / 10.0) % 1.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        base_color = (r, g, b, 0)  # Optional: add W channel as needed

        apply_wave(strip1, base_color, elapsed)
        apply_wave(strip2, base_color, elapsed)

        frame_time = time.perf_counter() - now
        sleep_time = frame_interval - frame_time
        if sleep_time > 0:
            time.sleep(sleep_time)


def theater_chase_effect(strip_a, strip_b, color=(255, 0, 0),
                         spacing=3, duration=10, fps=30):
    """
    Theater chase effect with processing overhead compensation.
    """

    num_pixels = strip_a.numPixels()
    assert strip_b.numPixels() == num_pixels, "Strips must be the same length"

    chase_color = Color(*color)
    off_color = Color(0, 0, 0)

    frame_duration = 1.0 / fps
    start_time = time.time()
    next_frame_time = start_time + frame_duration
    offset = 0

    while (time.time() - start_time) < duration:
        # Draw current frame
        for i in range(num_pixels):
            if (i + offset) % spacing == 0:
                strip_a.setPixelColor(i, chase_color)
                strip_b.setPixelColor(i, chase_color)
            else:
                strip_a.setPixelColor(i, off_color)
                strip_b.setPixelColor(i, off_color)

        strip_a.show()
        strip_b.show()

        # Step offset for next frame
        offset = (offset + 1) % spacing

        # Time adjustment for consistent fps
        sleep_time = next_frame_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        next_frame_time += frame_duration


import time
import math
from rpi_ws281x import Color

def blood_artery_effect(strip_a, strip_b, speed=30, bpm=60, pulse_depth=0.3,
                        min_blob_len=5, max_blob_len=15,
                        duration=10, fps=60):
    """
    Blood-in-artery effect with heartbeat-synced blobs and distinct visuals.
    """

    def heartbeat_wave(t, bpm):
        """Returns 0–1 pulse strength based on heartbeat."""
        beat_time = 60.0 / bpm
        t = t % beat_time
        if t < 0.1 * beat_time:
            return 1.0 - (t / (0.1 * beat_time))  # Quick up
        elif t < 0.2 * beat_time:
            return 0.5 - ((t - 0.1 * beat_time) / (0.1 * beat_time))  # Quick down
        else:
            return 0.2  # Rest

    num_pixels = strip_a.numPixels()
    assert strip_b.numPixels() == num_pixels, "Strips must be same length"

    base_color = (100, 0, 0)
    blob_color = (255, 0, 0)
    blobs = []  # List of (pos, length)

    frame_duration = 1.0 / fps
    start_time = time.time()
    next_frame_time = start_time + frame_duration

    beat_interval = 60.0 / bpm
    next_beat_time = start_time

    while (time.time() - start_time) < duration:
        now = time.time()
        elapsed = now - start_time

        # Global heartbeat pulse modulation
        pulse = heartbeat_wave(elapsed, bpm)
        pulse = 1.0 - pulse * pulse_depth

        # Spawn a blob at each heartbeat
        if now >= next_beat_time:
            blob_len = math.floor(min_blob_len + (max_blob_len - min_blob_len) * 0.5)
            blobs.append((-blob_len, blob_len))  # Start off-screen
            next_beat_time += beat_interval

        # Update blobs' positions
        updated_blobs = []
        for pos, length in blobs:
            new_pos = pos + speed * frame_duration
            if new_pos - length < num_pixels:
                updated_blobs.append((new_pos, length))
        blobs = updated_blobs

        # Draw frame
        for i in range(num_pixels):
            # Start with pulsing artery base
            red = int(base_color[0] * pulse)

            # Add any blob contribution
            for pos, length in blobs:
                if pos <= i < pos + length:
                    rel = (i - pos) / length
                    edge_fade = math.sin(math.pi * rel)  # Smooth bell shape
                    blob_red = int(blob_color[0] * edge_fade * pulse)
                    red = max(red, blob_red)
                    break  # Only one blob per pixel

            color = Color(red, 0, 0)
            strip_a.setPixelColor(i, color)
            strip_b.setPixelColor(i, color)

        strip_a.show()
        strip_b.show()

        # Maintain frame timing with processing time accounted for
        sleep_time = next_frame_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        next_frame_time += frame_duration



def starfield_effect(strip_a, strip_b,
                     color=(255, 255, 255, 0),
                     spawn_rate=10,
                     speed=100,
                     fade=0.9,
                     duration=10,
                     fps=60,
                     direction=1):

    num_leds = strip_a.numPixels()
    frame_delay = 1.0 / fps
    pixels = [(0, 0, 0, 0)] * num_leds
    stars = []
    spawn_interval = 1.0 / spawn_rate
    last_spawn_time = time.time()
    start_time = time.time()
    next_frame_time = time.time()

    while time.time() - start_time < duration:
        frame_start = time.time()

        # Fade all pixels
        pixels = [tuple(int(c * fade) for c in px) for px in pixels]

        # Spawn new stars
        if frame_start - last_spawn_time >= spawn_interval:
            pos = 0 if direction == 1 else num_leds - 1
            stars.append({"pos": pos, "t": frame_start})
            last_spawn_time = frame_start

        # Move stars
        now = frame_start
        new_stars = []
        for star in stars:
            elapsed = now - star["t"]
            move_px = int(elapsed * speed)
            pos = star["pos"] + direction * move_px
            if 0 <= pos < num_leds:
                pixels[pos] = color
                new_stars.append(star)
        stars = new_stars

        # Update strips
        for i in range(num_leds):
            strip_a.setPixelColor(i, Color(*pixels[i]))
            strip_b.setPixelColor(i, Color(*pixels[i]))

        strip_a.show()
        strip_b.show()

        # Frame pacing — subtract processing time
        frame_end = time.time()
        next_frame_time += frame_delay
        sleep_time = next_frame_time - frame_end
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_frame_time = time.time()  # reset if behind



def aurora_effect(strip_a, strip_b,
                  palette=[(0, 255, 100, 0), (0, 100, 255, 0), (100, 0, 255, 0)],
                  speed=0.5,
                  fade=0.9,
                  duration=20,
                  fps=60,
                  scale=0.1,
                  background_color=(0, 0, 0, 0)):
    
    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(4))

    def get_aurora_color(x, t, palette, scale): 
        # Use sine to get a smooth blending factor
        wave = 0.5 * (1 + math.sin(x * scale + t))
        i = int(wave * (len(palette) - 1))
        j = (i + 1) % len(palette)
        blend_t = (wave * (len(palette) - 1)) % 1.0
        return lerp_color(palette[i], palette[j], blend_t)

    num_leds = strip_a.numPixels()
    frame_delay = 1.0 / fps
    pixels = [background_color] * num_leds
    start_time = time.time()
    next_frame_time = time.time()

    while time.time() - start_time < duration:
        frame_start = time.time()
        t = (frame_start - start_time) * speed

        # Fade existing pixels
        pixels = [tuple(int(c * fade) for c in px) for px in pixels]

        # Update colors using smooth wave functions
        for i in range(num_leds):
            color = get_aurora_color(i, t, palette, scale)
            pixels[i] = tuple(min(255, max(p, c)) for p, c in zip(pixels[i], color))

        # Output to strips
        for i in range(num_leds):
            strip_a.setPixelColor(i, Color(*pixels[i]))
            strip_b.setPixelColor(i, Color(*pixels[i]))
        strip_a.show()
        strip_b.show()

        # Frame timing
        frame_end = time.time()
        next_frame_time += frame_delay
        sleep_time = next_frame_time - frame_end
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_frame_time = time.time()


def comet_effect(strip_a, strip_b,
                 color=(255, 0, 0, 0),         # comet RGBW
                 tail_length=20,
                 speed=50,                    # pixels/sec
                 fade_factor=0.6,
                 duration=10,
                 fps=60,
                 direction=1,
                 num_comets=1,
                 min_spacing=30,
                 background_color=(0, 0, 0, 0)):
    """
    RGBW comet effect with randomized spacing and background.

    Args:
        color: RGBW comet color
        tail_length: Length of fading tail
        speed: Movement speed in pixels/sec
        fade_factor: Brightness decay factor [0-1]
        duration: Duration in seconds
        fps: Frames per second
        direction: 1 = left to right, -1 = right to left
        num_comets: Number of comets
        min_spacing: Minimum spacing between comet start positions
        background_color: RGBW background color (default off)
    """
    num_pixels = strip_a.numPixels()
    assert strip_b.numPixels() == num_pixels, "Strip lengths must match"

    if num_comets * min_spacing > num_pixels:
        raise ValueError(f"Too many comets for spacing: {num_comets} × {min_spacing} > {num_pixels}")

    frame_duration = 1.0 / fps
    start_time = time.time()
    next_frame_time = start_time + frame_duration

    r_base, g_base, b_base, w_base = color
    r_bg, g_bg, b_bg, w_bg = background_color
    packed_bg = Color(r_bg, g_bg, b_bg, w_bg)

    # Generate non-overlapping random start positions
    taken = []
    comet_offsets = []

    while len(comet_offsets) < num_comets:
        pos = random.randint(0, num_pixels - 1)
        if all(abs(pos - other) >= min_spacing for other in taken):
            comet_offsets.append(pos)
            taken.append(pos)

    while (time.time() - start_time) < duration:
        # Fill background first
        for i in range(num_pixels):
            strip_a.setPixelColor(i, packed_bg)
            strip_b.setPixelColor(i, packed_bg)

        now = time.time()
        elapsed = now - start_time

        for offset in comet_offsets:
            base_pos = offset + direction * speed * elapsed
            head_pos = base_pos % (num_pixels + tail_length)

            for t in range(tail_length):
                pos = int(head_pos) - t * direction
                if 0 <= pos < num_pixels:
                    fade = fade_factor ** t
                    r = int(r_base * fade)
                    g = int(g_base * fade)
                    b = int(b_base * fade)
                    w = int(w_base * fade)
                    packed = Color(r, g, b, w)
                    strip_a.setPixelColor(pos, packed)
                    strip_b.setPixelColor(pos, packed)

        strip_a.show()
        strip_b.show()

        sleep_time = next_frame_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        next_frame_time += frame_duration




def color_bounce(strip1, strip2, duration=15, num_bouncers=3, fps=60,
                 independent=False, change_color_on_bounce=True, bar_size=5):
    import time
    import random
    import colorsys

    def get_distinct_color(last_color=None):
        # Ensure new color is visibly different (distance > threshold)
        while True:
            color = tuple(random.randint(80, 255) for _ in range(4))  # RGBW
            if not last_color:
                return color
            diff = sum(abs(c1 - c2) for c1, c2 in zip(color, last_color))
            if diff > 100:  # Tune this threshold if needed
                return color

    def clear(strip):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0, 0))

    def init_bouncers(num_leds, count):
        spacing = num_leds // (count + 1)
        return [
            {
                'pos': spacing * (i + 1),
                'dir': random.choice([-1, 1]),
                'color': get_distinct_color()
            } for i in range(count)
        ]

    def draw_bouncers(strip, bouncers, num_leds):
        for b in bouncers:
            r, g, b_, w = b['color']
            center = int(b['pos'])
            for offset in range(-(bar_size // 2), bar_size // 2 + 1):
                idx = center + offset
                if 0 <= idx < num_leds:
                    strip.setPixelColor(idx, Color(r, g, b_, w))

    def detect_collisions(bouncers, num_leds):
        collided = set()
        for i in range(len(bouncers)):
            a = bouncers[i]
            a_range = set(range(int(a['pos']) - bar_size // 2, int(a['pos']) + bar_size // 2 + 1))
            for j in range(i + 1, len(bouncers)):
                if (i, j) in collided:
                    continue
                b = bouncers[j]
                b_range = set(range(int(b['pos']) - bar_size // 2, int(b['pos']) + bar_size // 2 + 1))
                if a_range & b_range:
                    # Bounce both and assign distinct colors
                    a['dir'] *= -1
                    b['dir'] *= -1
                    collided.add((i, j))
                    if change_color_on_bounce:
                        a['color'] = get_distinct_color(a['color'])
                        b['color'] = get_distinct_color(b['color'])

    # Main loop (unchanged except call updated functions)
    num_leds_1 = strip1.numPixels()
    num_leds_2 = strip2.numPixels()
    delay = 1.0 / fps

    bouncers1 = init_bouncers(num_leds_1, num_bouncers)
    bouncers2 = init_bouncers(num_leds_2, num_bouncers) if independent else bouncers1

    start_time = time.perf_counter()

    while time.perf_counter() - start_time < duration:
        frame_start = time.perf_counter()

        clear(strip1)
        clear(strip2)

        draw_bouncers(strip1, bouncers1, num_leds_1)
        draw_bouncers(strip2, bouncers2, num_leds_2)

        strip1.show()
        strip2.show()

        for b in bouncers1:
            b['pos'] += b['dir']
            if b['pos'] < 0 or b['pos'] > num_leds_1 - 1:
                b['dir'] *= -1
                b['pos'] = max(0, min(b['pos'], num_leds_1 - 1))
                if change_color_on_bounce:
                    b['color'] = get_distinct_color(b['color'])

        if independent:
            for b in bouncers2:
                b['pos'] += b['dir']
                if b['pos'] < 0 or b['pos'] > num_leds_2 - 1:
                    b['dir'] *= -1
                    b['pos'] = max(0, min(b['pos'], num_leds_2 - 1))
                    if change_color_on_bounce:
                        b['color'] = get_distinct_color(b['color'])

        detect_collisions(bouncers1, num_leds_1)
        if independent:
            detect_collisions(bouncers2, num_leds_2)

        elapsed = time.perf_counter() - frame_start
        if (sleep := delay - elapsed) > 0:
            time.sleep(sleep)





def blackout(strip):
    for i in range(max(strip.numPixels(), strip.numPixels())):
        strip.setPixelColor(i, Color(0, 0, 0, 0))
    
    strip.show()

def fill_color(strip, color):
    """Set all pixels on the strip to the given (r, g, b, w) color tuple."""
    for i in range(strip.numPixels()):
        strip[i] = Color(*color)
    strip.show()