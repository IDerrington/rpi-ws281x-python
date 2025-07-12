from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import random
from led_effects import run_effect  # Replace with your actual effect runner

# Define the effects to cycle through
EFFECTS = ["aurora", "fireflies", "matrix", "sparkles", "morse", "ce3k", "blood_pulse", "star_wars"]

def scheduled_led_trigger():
    now = datetime.now()
    effect = random.choice(EFFECTS)
    print(f"[{now.strftime('%H:%M:%S')}] Triggering effect: {effect}")
    run_effect(effect, {})  # Add effect parameters if needed

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Run every 15 minutes, from 19:00 (7 PM) to 23:45 (11:45 PM)
    cron_trigger = CronTrigger(minute='0,15,30,45', hour='19-23')

    scheduler.add_job(scheduled_led_trigger, cron_trigger)
    scheduler.start()