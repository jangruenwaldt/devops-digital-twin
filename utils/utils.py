from datetime import datetime
from functools import reduce


class Utils:

    @staticmethod
    def str_to_datetime(date_string):
        if date_string is None:
            return None
        return datetime.fromtimestamp(int(date_string))

    @staticmethod
    def datetime_to_str(dt):
        return str(int(dt.timestamp()))

    # Source: https://stackoverflow.com/questions/25833613/safe-method-to-get-value-of-nested-dictionary
    def deep_get(dictionary, keys, default=None):
        return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."),
                      dictionary)
