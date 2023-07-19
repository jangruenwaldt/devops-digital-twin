from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from features.twins.twin_builder import TwinBuilder
from utils.config import Config
from utils.data_manager import DataManager
from utils.utils import Utils

scheduler = BackgroundScheduler()


class ScheduledRunner:

    @staticmethod
    def _run_and_reschedule():
        scheduler.get_jobs()[0].remove()

        TwinBuilder.build()
        ScheduledRunner._add_schedule_from_config_setting()

    @staticmethod
    def _add_schedule_from_config_setting():
        scheduler.add_job(TwinBuilder.build, 'interval', hours=Config.get_update_interval_in_hours())

    # Check when last data update was and schedule so that data is updated according to
    # Config.get_update_interval_in_hours() setting; 24 hours by default. Update data immediately if data was never
    # updated before.
    @staticmethod
    def start():
        last_data_fetch = Utils.str_to_datetime(DataManager.retrieve_by_key('last_data_fetch'))
        minutes_until_next_run = 0

        if last_data_fetch is not None:
            minutes_passed_since_last_run = (datetime.now() - last_data_fetch).total_seconds() / 60
            minutes_until_next_run = Config.get_update_interval_in_hours() * 60 - minutes_passed_since_last_run

        if minutes_until_next_run <= 0:
            # run now
            TwinBuilder.build()

            ScheduledRunner._add_schedule_from_config_setting()
            scheduler.start()
        else:
            # schedule first run in minutes_until_next_run minutes, then cancel the scheduler and go back to schedule
            # according to config setting.
            scheduler.add_job(ScheduledRunner._run_and_reschedule, 'interval', minutes=minutes_until_next_run)
            scheduler.start()
