from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from features.twins.twin_builder import TwinBuilder
from utils.config import Config
from utils.data_manager import DataManager
from utils.utils import Utils

scheduler = BlockingScheduler()


class ScheduledRunner:

    @staticmethod
    def _build_twin_and_reschedule():
        scheduler.get_jobs()[0].remove()

        TwinBuilder.build()
        ScheduledRunner._add_schedule_from_config_setting()

    @staticmethod
    def _add_schedule_from_config_setting():
        scheduler.add_job(TwinBuilder.build, 'interval', minutes=Config.update_interval_in_minutes())

    # Check when last data update was and schedule so that data is updated according to
    # Config.update_interval_in_minutes() setting; 60 minutes by default. Update data immediately if data was never
    # updated before.
    @staticmethod
    def start():
        last_data_fetch = Utils.str_to_datetime(DataManager.retrieve_by_key('last_data_fetch'))
        minutes_until_next_run = 0

        if last_data_fetch is not None:
            minutes_passed_since_last_run = (datetime.now() - last_data_fetch).total_seconds() / 60
            minutes_until_next_run = Config.update_interval_in_minutes() - minutes_passed_since_last_run
            if Config.get_enable_logs():
                print(f'Last data fetch was {last_data_fetch}, i.e. {minutes_passed_since_last_run} minutes ago. '
                      f'The next fetch will therefore be in {minutes_until_next_run} minutes.')
        elif Config.get_enable_logs():
            print(f'No previous fetches were found, fetching data immediately...')

        if minutes_until_next_run <= 0 or Config.get_force_update_on_first_launch():
            if Config.get_force_update_on_first_launch():
                print('force_update_on_first_launch = true, updating...')

            TwinBuilder.build()
            ScheduledRunner._add_schedule_from_config_setting()
        else:
            # schedule first run in minutes_until_next_run minutes, then cancel the scheduler and go back to schedule
            # according to config setting.
            scheduler.add_job(ScheduledRunner._build_twin_and_reschedule, 'interval', minutes=minutes_until_next_run)

        scheduler.start()
