import zlib
import os
from pathlib import Path

import datetime
import subprocess

from . import common


log = common.setup_log("fs")

PATH_INIT = None
PATH_WORK = None
ADD_FROM_DATE_FORMAT = "%Y-%m"


PATH_INIT = Path.cwd()


def find_up_file(fn):
    max_levels = len(PATH_INIT.parts)
    path_current = Path(PATH_INIT)
    for n_levels_up in range(max_levels):
        path_target = path_current / fn
        if path_target.is_file():
            return path_target
        path_current = (path_current / "..").resolve()
    else:
        raise FileNotFoundError("Limit reached, path not found")


def get_iterator(path):
    if path.is_file():
        if path.name[0] == ".":
            return
        yield path
    elif path.is_dir():
        for item in path.iterdir():
            yield from get_iterator(item)
    elif not path.exists():
        raise FileNotFoundError("File does not exists: '%s'" % path)
    else:
        raise FileNotFoundError("Unkown file type: '%s'" % path)


def remove(path):
    log.debug("Remove FS: %s", path)
    os.unlink(path)
    remove_empty_dir(path)
    # If the directory leading to this is empty, remove that also.


def remove_empty_dir(path):
    path = Path(path)
    log.debug("Remove dir: %s", path.parts)
    path = path.parent

    if path.exists() == False:
        return


    assert(path.is_dir())

    while len(path.parts) >= 0:
        log.debug("Remove dir: %s", path)
        for item in path.iterdir():
            return
        # No items in the directory, this can be removed
        path.rmdir()
        path = path.parent


def set_workdir(path):
    os.chdir(path)
    global PATH_WORK
    PATH_WORK = Path(path).resolve()


def import_file(info, target_path):
    time_prefix = datetime.datetime.fromtimestamp(
        info.timestamp).strftime(ADD_FROM_DATE_FORMAT)
    target_file = Path(target_path) / Path(time_prefix) / Path(info.name).name
    return FileInfo_Pure(target_file, info)


def import_file_do(info):
    # Make directories
    subprocess.run(("mkdir", "-p", info.name.parent), check=True)
    subprocess.run(("cp",
                    "--preserve=mode,timestamps",
                    str(info.path_content),
                    str(info.name)),
                   check=True)


def make_absolute(path):
    path = Path(PATH_WORK, path).resolve()


def make_relative(paths):
    rets = []
    for path in paths:
        path = Path(PATH_INIT, path).resolve()
        rets.append(path.relative_to(PATH_WORK))
    return rets


class FileInfo_Pure(common.FileBase):
    def __init__(self, new_name, old_info):
        self.timestamp = old_info.timestamp
        self.name = Path(new_name)
        self.size = old_info.size
        self.checksum = old_info.checksum
        self.path_content = Path(old_info.name)


def get_timestamp(path, multiply=1):
    return int(Path(path).stat().st_mtime * multiply)


class FileInfo(common.FileBase):
    def __init__(self, path, no_checksum=True):
        self.name = Path(path)
        

        stat = self.name.stat()
        self.timestamp = int(stat.st_mtime)
        self.size = int(stat.st_size)
        if no_checksum == True:
            self.checksum = None
        else:
            self.calc_checksum()

    def calc_checksum(self):
        with open(str(self.name), 'rb') as fid:
            self.checksum = zlib.adler32(fid.read())
        return self.checksum


def get_info(path, **kwargs):
    return FileInfo(path, **kwargs)
