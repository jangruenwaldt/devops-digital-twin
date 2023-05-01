import os

from utils.constants.twin_constants import TwinConstants

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATA_DIR = os.path.join(ROOT_DIR, '.local-data')
DATA_EXPORT_DIR = os.path.join(ROOT_DIR, TwinConstants.DATA_EXPORT_DIR)
