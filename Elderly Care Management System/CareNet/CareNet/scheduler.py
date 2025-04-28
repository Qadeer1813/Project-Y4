from apscheduler.schedulers.background import BackgroundScheduler
from .app import reencryption
from .import config

def scheduled_reencryption_job():
    print("Starting scheduled re-encryption...")
    config.MAINTENANCE_MODE = True
    try:
        reencryption()
    except Exception as e:
        print(f"Scheduled re-encryption failed: {e}")
    print("Scheduled re-encryption completed.")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_reencryption_job, 'cron', day_of_week='Mon', hour=00, minute=40)
    scheduler.start()
    print("Re-encryption scheduler started.")
