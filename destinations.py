import os

from utils.constants.constants import TwinConstants

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_VALUE_DATA_EXPORT_DIR = os.path.join(ROOT_DIR, TwinConstants.DATA_DIR_NAME, TwinConstants.KEY_VALUE_DATA_DIR_NAME)
RAW_API_DATA_EXPORT_DIR = os.path.join(ROOT_DIR, TwinConstants.DATA_DIR_NAME, TwinConstants.API_DATA_DIR_NAME)
TWIN_DATA_EXPORT_DIR = os.path.join(ROOT_DIR, TwinConstants.DATA_DIR_NAME, TwinConstants.TWIN_DATA_EXPORT_DIR_NAME)
