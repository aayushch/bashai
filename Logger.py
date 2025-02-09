# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: February 7, 2025

import logging


class Logger:
    """Simple logging utility for the NL Command Tool."""

    def __init__(self, shell_pid: int):
        # @todo configurable or parameter
        self.log_file = f"/tmp/bashai_{shell_pid}.log"
        self._configure_logging()

    def _configure_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Also log to console for ERROR and above
        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def info(self, message: str):
        logging.info(message)

    def error(self, message: str):
        logging.error(message)

    def warning(self, message: str):
        logging.warning(message)
