#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
import subprocess
import time

from filelock import FileLock

from logging import Handler, NOTSET
from pathlib import Path
from .types import PathWithDatetime


class TimedRotatingFileHandler(Handler):
    """
    compare to logging.TimedRotatingFileHandler, this handler will write
    log directly to file like 'info.log.2025-04-19'.
    """

    def __init__(self, level=NOTSET, filename="log.log",
                 datetime_formatter="%Y-%m-%d", max_keep=10, flat_keep=2):
        """
        params:
            max_keep: how many files will the rotation keep
            flat_keep: how many files will stay in text mod, the other (max_keep-flat_keep) will be compressed using gzip
        """
        self.filepath: Path = None
        self.filename = Path(filename).name
        self.base_dir = Path(filename).parent
        self.datetime_formatter = datetime_formatter
        self.current_time_str = self.get_time_str()
        self.stream = self.init_stream()
        self.max_keep = max_keep
        self.flat_keep = flat_keep
        super().__init__(level)

    def init_stream(self):
        self.filepath = self.base_dir.joinpath(
                f"{self.filename}.{self.get_time_str()}")
        return open(self.filepath, "a")

    def get_time_str(self) -> str:
        return datetime.datetime.now().strftime(self.datetime_formatter)

    def emit(self, record):
        if self.should_rollover():
            self.do_rollover()
        self.stream.write(self.format(record) + "\n")
        self.stream.flush()

    def should_rollover(self) -> bool:
        new_time_str = self.get_time_str()
        return new_time_str != self.current_time_str

    def do_rollover(self):
        if self.filepath.exists():
            self.stream.close()
        self.stream = self.init_stream()
        paths: List[Path] = [
                i
                for i in self.base_dir.iterdir()
                if i.is_file() and i.name.startswith(self.filename)
        ]
        paths.sort(key=lambda x: x.name, reverse=True)
        to_delete: Path
        for to_delete in paths[self.max_keep:]:
            if to_delete == self.filepath:
                continue
            to_delete.unlink(missing_ok=True)
        for to_gzip_path in paths[self.flat_keep:self.max_keep]:
            # here use the system gzip command to ignore exceptions like
            # permission denied or file not found
            if to_gzip_path == self.filepath:
                continue
            try:
                if not to_gzip_path.stat().st_size:
                    to_gzip_path.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if to_gzip_path.suffix == ".gz":
                continue
            lock_path = self.base_dir.joinpath(".lock." + self.filename)
            lock_path.touch()
            with FileLock(lock_path, timeout=10):
                target_file = to_gzip_path.parent.joinpath(
                        to_gzip_path.name + ".gz"
                )
                if target_file.exists():
                    target_file.rename(target_file.parent.joinpath(
                        target_file.stem + "_" + str(time.time())
                    ).with_suffix(".gz"))
                cmds = ["gzip", to_gzip_path]
                subprocess.run(cmds)
