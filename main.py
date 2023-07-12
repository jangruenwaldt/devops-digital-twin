from apscheduler.schedulers.blocking import BlockingScheduler

from utils.config import Config


def main():
    print('TODO: Update data and database')


scheduler = BlockingScheduler()
scheduler.add_job(main, 'interval', hours=Config.get_update_interval_in_hours())
scheduler.start()
