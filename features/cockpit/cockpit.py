import requests

from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config


# The cockpit of a digital twin is a layer above the data itself, it usually includes a user interface, for now
# it is just code that works on twin data.
class Cockpit:
    @staticmethod
    def calculate_average_lead_time():
        # TODO
        return 0
