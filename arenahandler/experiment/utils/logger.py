"""
This module is used to manage the logging for the applicaiton.
"""
import logging
import os

from .readconfig import config


def get_logger(logger_name='main'):
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    log_file = os.path.join("logs/", '{}.log'.format(logger_name))
    if not os.path.exists("logs/"):
        os.makedirs("logs/")
    formatter = logging.Formatter(config['logformat'])
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.setLevel(config['loglevel'])
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
