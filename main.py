from apscheduler.schedulers.blocking import BlockingScheduler

from features.twins.twin_builder import TwinBuilder
from utils.config import Config

scheduler = BlockingScheduler()
scheduler.add_job(TwinBuilder.build, 'interval', hours=Config.get_update_interval_in_hours())
scheduler.start()
