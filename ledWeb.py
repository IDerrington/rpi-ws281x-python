from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_socketio import disconnect
import threading

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
@register_effect("Color Bounce", params={"duration": {"min": 5, "max": 60, "default": 15},
                                         "num_bouncers": {"min": 1, "max": 10, "default": 5},
                                         "independent": {"min": 0, "max": 1, "default": 0},
                                         "change_color_on_bounce": {"min": 0, "max": 1, "default": 0},
                                         "bar_size": {"min": 1, "max": 20, "default": 5}})
def run_color_bounce(duration=15, 
                     num_bouncers=3, 
                     speed=0.001, 
                     independent=False, 
                     change_color_on_bounce=True, 
                     bar_size=5):
    color_bounce(strip1, strip2, 
                 duration=duration, 
                 num_bouncers=num_bouncers, 
                 speed=speed,
                 independent=independent, 
                 change_color_on_bounce=change_color_on_bounce, 
                 bar_size=bar_size )

@register_effect("Mirror Bounce", params={"duration":   {"min": 5, "max": 60, "default": 15},
                                         "red":         {"min": 0, "max": 255, "default": 255},
                                         "green":       {"min": 0, "max": 255, "default": 0},
                                         "blue":        {"min": 0, "max": 255, "default": 0},
                                         "white":       {"min": 0, "max": 255, "default": 0}})
def run_mirror_bounce(duration=15, 
                      red=255,
                      green=0,
                      blue=0,
                      white=0):
    mirror_bounce(strip1,strip2, color=(red, green, blue, white), duration=duration)

@register_effect("Fireflies", params={"duration": {"min": 5, "max": 60, "default": 15},
                                      "max_fireflies": {"min": 1, "max": 50, "default": 20}})
def run_fireflies(duration=15, 
                  max_fireflies=5):
    fireflies(strip1, strip2, 
              duration=duration, 
              max_fireflies=max_fireflies)

@register_effect("Matrix", params={"duration": {"min": 5, "max": 60, "default": 15}, 
                                   "trail_length": {"min": 5, "max": 100, "default": 10}})
def run_matrix(duration=15,
               frame_delay=0.01, 
               trail_length=10):
    matrix_effect(strip1, strip2, 
                  duration=duration, 
                  frame_delay=frame_delay, trail_length=trail_length)

@register_effect("Timer", params={"total_time": {"min": 1, "max": 60, "default": 1}, 
                                  "reverse":    {"min": 0, "max": 1, "default": 0}})                              
def run_timer(total_time=10, 
              reverse=False, 
              frame_rate=30):
    timer_effect(strip1, strip2, 
                 total_time=total_time*60,  
                 reverse=reverse, 
                 frame_rate=30)

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


if __name__ == "__main__":
    strip1.begin()
    strip2.begin()
    blackout(strip1)
    blackout(strip2)

    socketio.run(app, host="0.0.0.0", port=5000,debug=True, allow_unsafe_werkzeug=True)
