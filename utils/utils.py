from datetime import datetime


class Utils:

    @staticmethod
    def str_to_datetime(date_string):
        if date_string is None:
            return None
        return datetime.fromtimestamp(int(date_string))

    @staticmethod
    def datetime_to_str(dt):
        return str(int(dt.timestamp()))
