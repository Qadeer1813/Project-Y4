from apscheduler.schedulers.background import BackgroundScheduler
from .app import reencryption

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(reencryption, 'cron', day_of_week='mon', hour=21, minute=50)
    scheduler.start()
    print("Re-encryption scheduler started.")
