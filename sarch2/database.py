

import sqlite3
import time

from pathlib import Path
from contextlib import contextmanager

from . import common

log = common.setup_log("db")

DATABASE_FILENAME = ".sarch2.db"

STATUS_INVALID = 0
STATUS_OK = 1
STATUS_DEL = 2

TABLE_DESC = (
    "filename STRING UNIQUE NOT NULL , size UNSIGNED INTEGER NOT NULL, timestamp UNSIGNED INTEGER NOT NULL,"
    "checksum STRING NOT NULL, status INTEGER NOT NULL, db_time UNSIGNED INTEGER NOT NULL ")


class FileDB(common.FileBase):
    def __init__(self, info_tpl):
        self.name = Path(info_tpl[0])
        self.size = info_tpl[1]
        self.timestamp = info_tpl[2]
        self.checksum = info_tpl[3]
        self.status = info_tpl[4]
        self.db_time = info_tpl[5]


class Database():

    def __init__(self, path, relative = True ):
        pathobj = Path(path).resolve()
        self.path_abs = pathobj.parent
        self.path_db = str(pathobj)
        
        if relative:
           self.path_current = Path.cwd().relative_to(self.path_abs)
        else:
            self.path_current = None
            
        log.debug("INIT DB at: %s - curr: %s", self.path_db, self.path_current)
        assert(pathobj.suffix == ".db")

    @contextmanager
    def db_connection(self, commit):
        # log.debug("Open DB: %s - commit %d", self.path_db, commit  )
        self.conn = sqlite3.connect(self.path_db)
        yield True
        if commit:
            self.conn.commit()
        self.conn.close()
        self.conn = None

    def save(self):
        assert(self.conn is not None)
        self.conn.commit()

    @contextmanager
    def db_cursor(self):
        assert(self.conn is not None)
        yield self.conn.cursor()

    def create(self):
        with self.db_cursor() as c:
            c.execute('CREATE TABLE files (%s)' % TABLE_DESC)

    def get_iterator(self, path):
        path = str(path)
        # log.debug("Get iterator: '%s'", path )
        with self.db_cursor() as c:

            if path == "" or path == ".":
                c.execute("SELECT * FROM files")
            else:
                c.execute(
                    "SELECT * FROM files WHERE filename LIKE ?", (path + r"%", ))

            for row in c.fetchall():
                # log.debug("GOT: %s", row )
                yield FileDB(row)

    def add(self, file_info):
        with self.db_cursor() as c:
            c.execute("INSERT INTO files values (?,?,?,?,?,?)",
                      (str(file_info.name),
                       file_info.size,
                       file_info.timestamp,
                       file_info.checksum,
                       STATUS_OK,
                       int(time.time())))

    def get(self, filename):
        # log.debug("Get: %s", filename )
        with self.db_cursor() as c:
            c.execute("SELECT * FROM files WHERE filename=?", (str(filename),))
            row = c.fetchone()
            if row is None:
                return None
            # log.debug("GOT: %s", row)
            return FileDB(row)

    def update(self, file_info, status=None):
        with self.db_cursor() as c:
            cmd = "size=?, timestamp=?, checksum=?, db_time=?"
            values = [file_info.size, file_info.timestamp,
                      file_info.checksum, int(time.time()), ]
            if status is not None:
                cmd += ", status=? "
                values.append(status)
            values.append(str(file_info.name))
            log.info("Update %s %s", cmd, values)
            c.execute("UPDATE files SET %s  WHERE filename=?" % cmd, values)
            assert(c.rowcount == 1)

    def remove(self, filename):
        # log.debug("Remove: %s", filename )
        with self.db_cursor() as c:
            c.execute("UPDATE files SET status=?, db_time=? WHERE filename=?",
                      (STATUS_DEL, int(time.time()), str(filename),))
            assert(c.rowcount == 1)
