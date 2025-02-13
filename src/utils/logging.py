import logging

import json_log_formatter

formatter = json_log_formatter.JSONFormatter()

json_handler = logging.StreamHandler()
json_handler.setFormatter(formatter)

logger = logging.getLogger("app_logger")
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("src/logs/app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
