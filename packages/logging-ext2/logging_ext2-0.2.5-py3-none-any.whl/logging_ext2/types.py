#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathWithDatetime:
    path: Path
    datetime: datetime.datetime
