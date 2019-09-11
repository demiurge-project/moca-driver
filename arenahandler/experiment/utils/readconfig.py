"""
This module is used to read the configuration file in order to set the serial
port in which the Arduino is going to be connected, the baud rate for the comm-
unication and the log level and log format.
"""
import os
import json

config_example = \
"""
{
    "serialport":"/dev/ttyS5",
    "baudrate": 57600,
    "loglevel":"INFO",
    "logformat":"%(asctime)s %(name)s [%(levelname)s] %(message)s"
}
"""

config = json.loads(open('config/config.json').read())
