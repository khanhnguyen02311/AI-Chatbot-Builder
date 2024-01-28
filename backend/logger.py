# https://www.youtube.com/watch?v=9L77QExPmI0

import logging.config
import pathlib
import json

logger = logging.getLogger("applogger")


def setup_logging():
    config_file = pathlib.Path("etc/logging_configs/config.json")
    with open(config_file) as f:
        config = json.load(f)
        logging.config.dictConfig(config)


def main():
    setup_logging()
    logger.info("Logger started.")
