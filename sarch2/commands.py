
import abc
from pathlib import Path

from . import filesystem
from . import output
from . import database


class WorkerImportBase(abc.ABC):

    def __init__(self):
        super().__init__()
        self.db_info = None
        self.fs_info = None

    @abc.abstractmethod
    def action_import_none(self):
        pass

    @abc.abstractmethod
    def action_import_del_equal(self):
        pass

    @abc.abstractmethod
    def action_import_del_conflict(self):
        pass

    @abc.abstractmethod
    def action_import_del_older(self):
        pass

    @abc.abstractmethod
    def action_import_normal_equal(self):
        pass

    @abc.abstractmethod
    def action_import_normal_conflict(self):
        pass

    @abc.abstractmethod
    def action_import_normal_older(self):
        pass


class WorkerBase(abc.ABC):

    def __init__(self):
        super().__init__()
        self.db_info = None
        self.fs_info = None
        self.status = 0

    def action_all_files( self ):
        pass

    @abc.abstractmethod
    def action_normal_missing(self):
        pass

    @abc.abstractmethod
    def action_normal_ok(self):
        pass

    @abc.abstractmethod
    def action_normal_changed(self):
        pass

    @abc.abstractmethod
    def action_none_normal(self):
        pass

    @abc.abstractmethod
    def action_del_ok(self):
        pass

    @abc.abstractmethod
    def action_del_conflict(self):
        pass

    @abc.abstractmethod
    def action_del_re_appear(self):
        pass

    def status_ok(self):
        return self.status


def full_scan_import(repo, path, worker):
    path = Path(path).resolve()
    fs_iter = filesystem.get_iterator(path)

    for fs_item in fs_iter:
        fs_info = filesystem.get_info(fs_item, no_checksum=False)
        fs_info_new = filesystem.import_file(fs_info, repo.path_current)

        db_info = repo.get(fs_info_new.name)

        worker.db_info = db_info
        worker.fs_info = fs_info_new
        

        if db_info is None:
            worker.action_import_none()
        else:
            if db_info.status == database.STATUS_DEL:
                if fs_info_new.equals(db_info):
                    worker.action_import_del_equal()
                else:
                    if db_info.timestamp > fs_info.timestamp:
                        worker.action_import_del_older()
                    else:
                        worker.action_import_del_conflict()
            elif db_info.status == database.STATUS_OK:
                if fs_info_new.equals(db_info):
                    worker.action_import_normal_equal()
                else:
                    if db_info.timestamp > fs_info.timestamp:
                        worker.action_import_normal_older()
                    else:
                        worker.action_import_normal_conflict()
            else:
                raise Exception("Unknown DB status: '%s'" % db_info.status)


def full_scan_work_db(fs_check_done, repo, path, worker):
    for db_info in repo.get_iterator(path):

        if db_info.name in fs_check_done:
            continue  # This file was processed

        # Ok, this file is in database, but not in FS
        worker.fs_info = None
        worker.db_info = db_info

        if db_info.status == database.STATUS_OK:
            worker.action_normal_missing()
        elif db_info.status == database.STATUS_DEL:
            worker.action_del_ok()
        else:
            raise Exception("Unknown DB status: '%s'" % db_info.status)


def full_scan_work_fs(repo, path, worker, flag_verify):
    fs_iter = filesystem.get_iterator(path)
    fs_check_done = set()
    
    for fs_item in fs_iter:
        fs_check_done.add(fs_item)

        fs_info = filesystem.get_info(fs_item, no_checksum=not flag_verify)

        worker.fs_info = fs_info
        worker.db_info = None

        db_info = repo.get(fs_item)
        worker.db_info = db_info
        worker.action_all_files()

        if db_info is None:
            worker.action_none_normal()
        else:
            if db_info.status == database.STATUS_OK:
                if fs_info.equals(db_info, has_checksum = flag_verify ):
                    worker.action_normal_ok()  # File seems to be same, continue to next
                else:
                    # File has changed
                    worker.action_normal_changed()

            elif db_info.status == database.STATUS_DEL:
                # The file exists in FS, altough marked as deleted
                fs_info.calc_checksum()

                if fs_info.equals(db_info):
                    worker.action_del_re_appear()
                else:
                    worker.action_del_conflict()
            else:
                raise Exception("Unknown DB status: '%s'" % db_info.status)
    return fs_check_done


def full_scan(repo, path, worker, flag_verify=True):
    fs_checked = full_scan_work_fs(repo, path, worker, flag_verify)
    full_scan_work_db(fs_checked, repo, path, worker)


class WorkerImportPrint(WorkerImportBase):
    def action_import_none(self):
        output.info("IMPORT: {}", self.fs_info.name)

    def action_import_del_equal(self):
        output.debug("SKIP-DELETED: {}", self.fs_info.name)

    def action_import_del_conflict(self):
        output.info("CONFLICT-DELETED: {}", self.fs_info.name)

    def action_import_del_older(self):
        output.info("SKIP-DELETED-OLD: {}", self.fs_info.name)

    def action_import_normal_equal(self):
        output.debug("SKIP-NORMAL: {}", self.fs_info.name)

    def action_import_normal_conflict(self):
        output.info("CONFLICT-NORMAL: {}", self.fs_info.name)

    def action_import_normal_older(self):
        output.debug("SKIP-NORMAL-OLD: {}", self.fs_info.name)


class WorkerImport(WorkerImportBase):

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def action_import_none(self):
        self.repo.add(self.fs_info)
        filesystem.import_file_do(self.fs_info)

    def action_import_del_equal(self):
        output.debug("SKIP-DELETED: {}", self.fs_info.name)

    def action_import_del_conflict(self):
        output.info(
            "CONFLICT-DELETED: {} -> SKIP (db deleted older than imported)",
            self.fs_info.name)

    def action_import_del_older(self):
        output.info("SKIP-DELETED-OLD: {}", self.fs_info.name)

    def action_import_normal_equal(self):
        output.debug("SKIP-NORMAL: {}", self.fs_info.name)

    def action_import_normal_conflict(self):
        output.info(
            "CONFLICT-NORMAL: {} -> SKIP (file meta not match)",
            self.fs_info.name)

    def action_import_normal_older(self):
        output.info(
            "SKIP-NORMAL-OLD: {} -> SKIP (file older than DB)",
            self.fs_info.name)


class WorkerSave(WorkerBase):

    def __init__(self, resolves, repo):
        super().__init__()
        self.resolves = resolves
        self.repo = repo

    def action_normal_missing(self):
        self.repo.remove(self.db_info.name)
        filesystem.remove_empty_dir(self.db_info.name)

    def action_normal_ok(self):
        pass

    def action_normal_changed(self):
        self.repo.update(self.fs_info)

    def action_none_normal(self):
        self.repo.add(self.fs_info)

    def action_del_ok(self):
        pass

    def action_del_conflict(self):
        if self.resolves:
            output.info(
                "RESOLVED: {} -> Update as normal file",
                self.fs_info.name)
            self.repo.update(self.fs_info, status=database.STATUS_OK)
            return
        output.info("DEL-CONFLICT: {} -> Skipping", self.fs_info.name)
        self.status = 1

    def action_del_re_appear(self):
        filesystem.remove(self.fs_info.name)


class WorkerStatus(WorkerBase):
    def __init__(self, *pargs, **kwargs ):
        super().__init__( *pargs, **kwargs )
        self.ok_files = 0
        self.total_files = 0

    def action_all_files( self ):
        self.total_files += 1

    def action_normal_missing(self):
        output.info("MISSING: {}", self.db_info.name)
        self.status = 1

    def action_normal_ok(self):
        output.debug("OK: {}", self.fs_info.name)
        self.ok_files += 1

    def action_normal_changed(self):
        output.info("CHANGED: {}", self.fs_info.name)
        self.status = 1

    def action_none_normal(self):
        output.info("UNTRACKED: {}", self.fs_info.name)
        self.status = 1

    def action_del_ok(self):
        output.debug("DELETED: {}", self.db_info.name)
        

    def action_del_conflict(self):
        output.info("DELETED-CHANGED: {}", self.db_info.name)
        self.status = 1

    def action_del_re_appear(self):
        output.info("RE-APPEARED: {}", self.db_info.name)
        self.status = 1

    def status_ok(self):
        return self.status
