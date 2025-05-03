# SPDX-FileCopyrightText: 2025-present Xiang Wang <ramwin@qq.com>
#
# SPDX-License-Identifier: MIT

import logging
import time
import unittest
from logging_ext2.handlers import TimedRotatingFileHandler


class Test(unittest.TestCase):

    def test(self):
        loggera = logging.getLogger("loggera")
        handlera = TimedRotatingFileHandler(
            filename="tests/info.log",
            datetime_formatter="%Y-%m-%d_%H:%M:%S",
            max_keep=20, flat_keep=2)
        loggera.addHandler(logging.StreamHandler())
        loggera.addHandler(handlera)
        loggera.setLevel(logging.INFO)
        handlera.setFormatter(logging.Formatter("%(lineno)d %(process)d %(asctime)s %(message)s"))

        loggerb = logging.getLogger("loggerb")
        loggerb.addHandler(TimedRotatingFileHandler(
            filename="tests/info.log",
            datetime_formatter="%Y-%m-%d_%H:%M:%S",
            max_keep=20, flat_keep=2))
        loggerb.addHandler(logging.StreamHandler())
        loggerb.setLevel(logging.INFO)

        loggera.info("first")
        loggera.info("second")
        loggera.info("third")
        loggerb.info("first")
        loggerb.info("second")
        loggerb.info("third")
        time.sleep(1)
        loggera.info("first")
        loggera.info("second")
        loggera.info("third")
        loggerb.info("first")
        loggerb.info("second")
        loggerb.info("third")
        time.sleep(1)
        loggera.info("first")
        loggera.info("second")
        loggera.info("third")
        loggerb.info("first")
        loggerb.info("second")
        loggerb.info("third")
