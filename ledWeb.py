from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_socketio import disconnect
import threading
import json
import os

from LedEffects import *  # Your custom effects like fireflies, matrix, etc.
from rpi_ws281x import ws, Color, Adafruit_NeoPixel

app = Flask(__name__)
socketio = SocketIO(app)
connected_client_sid = None

# LED strip configuration:
LED_1_COUNT = 600
LED_1_PIN = 18
LED_1_FREQ_HZ = 800000
LED_1_DMA = 10
LED_1_BRIGHTNESS = 50
LED_1_INVERT = False
LED_1_CHANNEL = 0
LED_1_STRIP = ws.SK6812_STRIP_GRBW

LED_2_COUNT = 600
LED_2_PIN = 13
LED_2_FREQ_HZ = 800000
LED_2_DMA = 9
LED_2_BRIGHTNESS = 50
LED_2_INVERT = False
LED_2_CHANNEL = 1
LED_2_STRIP = ws.SK6812_STRIP_GRBW

strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ,
                           LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS,
                           LED_1_CHANNEL, LED_1_STRIP)
strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ,
                           LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS,
                           LED_2_CHANNEL, LED_2_STRIP)

# Global effect registry
EFFECTS = {}

# Currently running effect
current_effect = {"name": None, "thread": None}

def register_effect(name, params=None):
    def decorator(fn):
        EFFECTS[name] = {
            "function": fn,
            "params": params or {}
        }
        return fn
    return decorator

# Sample effects
@register_effect("Color Bounce", params={"duration":        {"min": 5, "max": 60, "default": 15, "step": 1},
                                         "num_bouncers":    {"min": 1, "max": 30, "default": 5, "step": 1},
                                         "independent":     {"min": 0, "max": 1, "default": 0, "step": 1},
                                         "change_color_on_bounce": {"min": 0, "max": 1, "default": 1, "step": 1},
                                         "bar_size":        {"min": 1, "max": 20, "default": 5, "step": 1}})
def run_color_bounce(duration=15, 
                     num_bouncers=3, 
                     speed=0.001, 
                     independent=False, 
                     change_color_on_bounce=True, 
                     bar_size=5):
    color_bounce(strip1, strip2, 
                 duration=duration, 
                 num_bouncers=num_bouncers, 
                 independent=independent, 
                 change_color_on_bounce=change_color_on_bounce, 
                 bar_size=bar_size )

@register_effect("Mirror Bounce", params={"duration":   {"min": 5, "max": 60, "default": 15, "step": 1},
                                         "red":         {"min": 0, "max": 255, "default": 255, "step": 1},
                                         "green":       {"min": 0, "max": 255, "default": 0, "step": 1},
                                         "blue":        {"min": 0, "max": 255, "default": 0, "step": 1},
                                         "white":       {"min": 0, "max": 255, "default": 0, "step": 1}})
def run_mirror_bounce(duration=15, 
                      red=255,
                      green=0,
                      blue=0,
                      white=0):
    mirror_bounce(strip1,strip2, color=(red, green, blue, white), duration=duration)



@register_effect("Fireflies", params={"duration":       {"min": 5, "max": 60, "default": 15, "step": 1},
                                      "max_fireflies":  {"min": 1, "max": 50, "default": 20, "step": 1}})
def run_fireflies(duration=15, 
                  max_fireflies=5):
    fireflies(strip1, strip2, 
              duration=duration, 
              max_fireflies=max_fireflies)



@register_effect("Fire Effect", params={"duration":     {"min": 5, "max": 60, "default": 10, "step": 1},
                                        "cooling":      {"min": 1, "max": 100, "default": 55,  "step": 1},
                                        "sparking":     {"min": 1, "max": 255, "default": 120, "step": 1}})
def run_fire_effect(duration=10.0, cooling=55, sparking=120):
    fire_effect(strip1, strip2, 
                duration=duration, 
                cooling=cooling, 
                sparking=sparking)



@register_effect("Matrix", params={ "duration":      {"min": 5, "max": 600, "default": 20, "step": 1}})
def run_matrix(duration=15):
    matrix_effect(strip1, strip2, duration=duration, reverse=True)



@register_effect("Timer", params={"duration":  {"min": 1, "max": 60, "default": 1, "step": 1}, 
                                  "reverse":   {"min": 0, "max": 1, "default": 0, "step": 1}})                              
def run_timer(duration=10, reverse=False):
    timer_effect(strip1, strip2, duration=duration*60, reverse=reverse)



@register_effect("Rainbow With Sparkles", params={  "duration":              {"min": 1,  "max": 60, "default": 10, "step": 1}, 
                                                    "sparkle_chance":        {"min": 0.0, "max": 0.1, "default": 0.05, "step": 0.01}})                              
def run_rainbow_with_sparkles(duration=10, sparkle_chance=0.05):
    rainbow_with_sparkles(strip1, strip2, duration=duration, sparkle_chance=sparkle_chance)



@register_effect("Union Jack Scroll Sparkle", params={"duration":         {"min": 1,   "max": 60,  "default": 10,   "step": 1},
                                                      "sparkle_chance":   {"min": 0.0, "max": 0.1, "default": 0.05, "step": 0.01},
                                                      "fade_steps":       {"min": 1,   "max": 20,  "default": 8,    "step": 1}}) 
def run_union_jack_scroll_sparkle( duration=10.0, frame_rate=20, sparkle_chance=0.1, fade_steps=8):
    union_jack_scroll_sparkle(strip1, strip2, 
                              duration=duration, 
                              frame_rate=frame_rate, 
                              sparkle_chance=sparkle_chance, 
                              fade_steps=fade_steps)



@register_effect("Dual Sparkle Effect", params={"duration": {"min": 1, "max": 60, "default": 10, "step": 1},
                                                "sparkles_per_frame": {"min": 0.0, "max": 100, "default": 5, "step": 1},
                                                "fade_steps": {"min": 1, "max": 20, "default": 8, "step": 1}})
def run_sparkle_effect(duration=10.0, sparkles_per_frame=5, fade_steps=8):
    sparkle_dual_fade(strip1, strip2,
                      duration=duration,
                      sparkles_per_frame=sparkles_per_frame, 
                      fade_steps=fade_steps)
 


@register_effect("Flash", params={"flashes": {"min": 1, "max": 100, "default": 1, "step": 10},
                                  "delay": {"min": 0.01, "max": 5.0, "default": 0.5, "step": 0.1}})
def run_alternate_flash_varied_colors(flashes=10, delay=0.5):
    alternate_flash_varied_colors(strip1, strip2, 
                                   flashes=flashes, 
                                   delay=delay) 



@register_effect("Color Wave Brightness", params={"duration": {"min": 5, "max": 60, "default": 15, "step": 1},
                                                  "wave_speed": {"min": 0.01, "max": 1.0, "default": 0.2, "step": 0.01},
                                                  "wave_frequency": {"min": 0.1, "max": 10.0, "default": 2.0, "step": 0.1}})
def run_color_wave_brightness(duration=15,
                              wave_speed=0.2, 
                              wave_frequency=2.0):
    color_wave_brightness(strip1, strip2,
                          duration=duration, 
                          wave_speed=wave_speed, 
                          wave_frequency=wave_frequency)



@register_effect("Morse Band Scroll", params={"duration": {"min": 1, "max": 60, "default": 10, "step": 1}})                        
def run_morse_band_scroll(text="Welcome to Garden Gaming Day", duration=10):
    morse_band_scroll(strip1, strip2, 
                      text=text, 
                      duration=duration, 
                      direction=1)




@register_effect("Sinister Pulse", params={"duration": {"min": 1, "max": 600, "default": 20, "step": 1}})
def run_sinister_pulse(duration: float = 20.0, fps: int = 30):
    sinister_pulse(strip1, strip2, duration=duration) 



@register_effect("Blood Pulse", params={"duration": {"min": 1, "max": 600, "default": 20, "step": 1}, 
                                        "speed": {"min": 1, "max": 100, "default": 20, "step": 1},
                                        "bpm": {"min": 30, "max": 300, "default": 60, "step": 1},
                                        "min_blob_len": {"min": 1,   "max": 10,  "default": 5,  "step": 1},
                                        "max_blob_len": {"min": 10,  "max": 30,  "default": 15,  "step": 1},
                                        "pulse_depth":  {"min": 0.0, "max": 1.0, "default": 0.5, "step": 0.1}})
def run_blood_pulse_effect(speed=20, bpm=60, pulse_depth=0.5, duration=10,min_blob_len=5, max_blob_len=15, spawn_rate=1.0 ):
    blood_artery_effect(strip1, strip2,
                       duration=duration,bpm=bpm, 
                       speed=speed,
                       pulse_depth=pulse_depth, 
                       min_blob_len=min_blob_len, 
                       max_blob_len=max_blob_len)
                       


@register_effect("Theater Chase", params={"Red":        {"min": 0, "max": 255, "default": 255, "step": 1},
                                          "Green":      {"min": 0, "max": 255, "default": 0, "step": 1},
                                          "Blue":       {"min": 0, "max": 255, "default": 0,"step": 1},
                                          "spacing":    {"min": 1, "max": 10, "default": 3, "step": 1},
                                          "duration":   {"min": 1, "max": 60, "default": 10, "step": 1}})
def run_theater_chase_effect(Red= 255, Green=0, Blue=0,
                            spacing=3, duration=10, fps=30):
    theater_chase_effect(strip1, strip2,
                         color=(Red, Green, Blue), spacing=spacing, duration=duration, fps=fps)



@register_effect("Comet Effect", params={"red":          {"min": 0, "max": 255, "default": 255, "step": 1}, 
                                         "green":        {"min": 0, "max": 255, "default": 20, "step": 1},
                                         "blue":         {"min": 0, "max": 255, "default": 20, "step": 1},
                                         "white":        {"min": 0, "max": 255, "default": 255, "step": 1},
                                         "tail_length":  {"min": 1, "max": 100, "default": 80, "step": 1},
                                         "speed":        {"min": 1, "max": 100, "default": 100, "step": 1},
                                         "fade_factor":  {"min": 0, "max": 1, "default": 0.8, "step": 0.01},
                                         "duration":     {"min": 5, "max": 60, "default": 20,   "step": 1},
                                         "direction" :   {"min" :-1, "max" : 1 , "default" : 1 , "step" : 1},
                                         "num_comets":   {"min": 1, "max": 10, "default": 5, "step": 1},
                                         "min_spacing":  {"min": 20, "max": 100, "default": 30, "step": 1}})
def run_comet_effect(red=255, green=0, blue=0, white=0,
                    tail_length=20,
                    speed=50,       # pixels per second
                    fade_factor=0.6,
                    duration=10,
                    fps=60,
                    direction=1,
                    num_comets=1,
                    min_spacing=20):
    
    fade_factor = float(fade_factor)
    
    comet_effect(strip1, strip2,
                 color=(red, green, blue, white),
                 tail_length=tail_length,
                 speed=speed,
                 fade_factor=fade_factor,
                 duration=duration,
                 fps=fps,
                 direction=direction,
                 num_comets=num_comets,
                 min_spacing=min_spacing,
                 background_color=(0, 0, 5, 2))


@register_effect("Starfield Effect", params={
    "red":          {"min": 0, "max": 255, "default": 255, "step": 1},
    "green":        {"min": 0, "max": 255, "default": 255, "step": 1},
    "blue":         {"min": 0, "max": 255, "default": 255, "step": 1},
    "white":        {"min": 0, "max": 255, "default": 0, "step": 1},
    "spawn_rate":   {"min": 1, "max": 50, "default": 10, "step": 1},  # stars/sec
    "speed":        {"min": 10, "max": 300, "default": 100, "step": 10},  # px/sec
    "fade":         {"min": 0.7, "max": 1.0, "default": 0.9, "step": 0.01},
    "duration":     {"min": 5, "max": 60, "default": 20, "step": 1},
    "direction":    {"min": -1, "max": 1, "default": 1, "step": 1}
})
def run_starfield_effect(red=255, green=255, blue=255, white=0,
                         spawn_rate=10, speed=100, fade=0.9,
                         duration=20, fps=60, direction=1):
    
    starfield_effect(strip1, strip2,
                     color=(red, green, blue, white),
                     spawn_rate=spawn_rate,
                     speed=speed,
                     fade=fade,
                     duration=duration,
                     direction=direction)

@register_effect("Aurora Effect", params={
    "speed":          {"min": 0.01, "max": 1.0, "default": 1, "step": 0.01},
    "fade":           {"min": 0.1, "max": 1.0, "default": 0.9, "step": 0.01},
    "duration":       {"min": 5, "max": 60, "default": 20, "step": 1},
    "scale":          {"min": 0.01, "max": 1.0, "default": 0.04, "step": 0.01}})
def run_aurora_effect(  speed=0.5,
                        fade=0.9,
                        duration=20,
                        scale=0.1):       
    aurora_effect(strip1, strip2,
                  speed=speed,
                  fade=fade,
                  duration=duration,
                  scale=scale)       

@register_effect("CE3K Signal", params={"note_delay": {"min": 0.1, "max": 2.0, "default": 0.8, "step": 0.1}})
def run_ce3k_signal(note_delay=0.8):
    ce3k_signal(strip1, strip2, note_delay=note_delay)      

@register_effect("0 Blackout")
def run_blackout():
    blackout(strip1)    
    blackout(strip2)         

def log_effect_run(effect_name, params, filename="effect_log.json"):
    entry = {"name": effect_name, "params": params}
    data = []

    # Read existing log
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass  # Start fresh if corrupted

    data.append(entry)

    # Write updated log
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)         

@socketio.on('connect')
def on_connect():
    global connected_client_sid
    if connected_client_sid is not None:
        print(f"Rejecting connection from {request.sid} — already connected: {connected_client_sid}")
        # Reject new connection by disconnecting it immediately
        disconnect()
    else:
        connected_client_sid = request.sid
        print(f"Accepted connection: {connected_client_sid}")

@socketio.on('disconnect')
def on_disconnect():
    global connected_client_sid
    if request.sid == connected_client_sid:
        print(f"Client disconnected: {connected_client_sid}")
        connected_client_sid = None

@app.route("/")
def index():
    return render_template("index.html", effects=EFFECTS.keys())

@app.route("/metadata")
def metadata():
    return {name: data["params"] for name, data in EFFECTS.items()}

@socketio.on("start_effect")
def start_effect(data):
    name = data.get("name")
    params = data.get("params", {})

    if name not in EFFECTS:
        emit("status_update", {"status": "Effect not found"})
        return

    if current_effect["thread"] and current_effect["thread"].is_alive():
        print(f"Stopping current effect: {current_effect['name']}")
        # Optional: use threading.Event to signal stop

    def run_effect():
        print(f"Running effect: {name} with params {params}")

        log_effect_run(name, params)
        try:
            EFFECTS[name]["function"](**params)
        except Exception as e:
            print(f"Error in effect: {e}")
        
        print(f" Effect: {name} Completed")
        current_effect["name"] = None
        socketio.emit("status_update", {"status": "Idle"})

    thread = threading.Thread(target=run_effect)
    
    thread.start()
    current_effect["name"] = name
    current_effect["thread"] = thread
    socketio.emit("status_update", {"status": f"Running {name}"})

@socketio.on("play_file")
def play_file():
    
    if current_effect["thread"] and current_effect["thread"].is_alive():
        emit("status_update", {"status": "Busy — another effect is running"})
        return
    try:
        with open("playback.json", "r") as f:
            sequence = json.load(f)

        def run_sequence():
            for entry in sequence:
                name = entry.get("name")
                params = entry.get("params", {})
                if name in EFFECTS:
                    print(f"Playing effect from file: {name} with params {params}")
                    socketio.emit("status_update", {"status": f"Running {name} from file"})
                    EFFECTS[name]["function"](**params)
            socketio.emit("status_update", {"status": "Idle"})

        thread = threading.Thread(target=run_sequence)
        thread.start()
    except Exception as e:
        print(f"Error loading or playing file: {e}")
        socketio.emit("status_update", {"status": f"Error: {e}"})

@socketio.on("play_starwars")
def play_starwars():
    if current_effect["thread"] and current_effect["thread"].is_alive():
        emit("status_update", {"status": "Busy — another effect is running"})
        return
    try:
        with open("starwars_playback.json", "r") as f:
            sequence = json.load(f)

        def run_sequence():
            for entry in sequence:
                name = entry.get("name")
                params = entry.get("params", {})
                if name in EFFECTS:
                    print(f"Playing Star Wars effect: {name} with params {params}")
                    socketio.emit("status_update", {"status": f"Running {name} (Star Wars)"})
                    EFFECTS[name]["function"](**params)
            socketio.emit("status_update", {"status": "Idle"})

        thread = threading.Thread(target=run_sequence)
        thread.start()

    except Exception as e:
        print(f"Error playing Star Wars file: {e}")
        socketio.emit("status_update", {"status": f"Error: {e}"})

 


if __name__ == "__main__":
    strip1.begin()
    strip2.begin()
    blackout(strip1)
    blackout(strip2)

    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
