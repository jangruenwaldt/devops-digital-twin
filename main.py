from apscheduler.schedulers.blocking import BlockingScheduler


def main():
    print('TODO: Update data and database')


scheduler = BlockingScheduler()
scheduler.add_job(main, 'interval', hours=24)
scheduler.start()
