import argparse
import sys
import inspect
from contextlib import contextmanager

from . import commands
from . import filesystem
from . import database
from . import common


class SarchException(Exception):
    pass


class SarchExceptionNoDB(SarchException):
    pass


log = common.setup_log("main")


class Sarch2(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='File manager',
            usage='''sarch2 <command> [<args>]
The sarch2 commands are:
   init    <>           Create new database on current directory"
   save    <>|<path>   Saves current filesystem status to REPO, except Conflicts
   status   <>|<path>   Shows status of files, resolves conflicts
   save     <fn>        Saves given file to REPO
   import   <path>      Imports given path to current REPO
   sync     <path>      Sync with remote database (rsync target)
''')

        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command + "_exe"):
            parser.print_help()
            raise SarchException('Unrecognized command')

        parser_sub_create = getattr(self, args.command + "_cmd")
        parser_sub = parser_sub_create()

        target_fun = getattr(self, args.command + "_exe")
        fun_params = inspect.getfullargspec(target_fun)

        has_extra = "extra" in fun_params[0]

        log.info("Command: %s", args.command)

        if has_extra:
            config, extra = parser_sub.parse_known_args(sys.argv[2:])
            ret = target_fun(config, extra)
        else:
            config = parser_sub.parse_args(sys.argv[2:])
            ret = target_fun(config)
        exit(ret)

    @contextmanager
    def _open_db_and_cwd(self, write_db):
        try:
            path = filesystem.find_up_file(database.DATABASE_FILENAME)
        except FileNotFoundError:
            log.debug("No DB found!")
            raise SarchExceptionNoDB("Could not find database!")
        log.debug("Database found: %s" % path)

        self.repo = database.Database(path)

        filesystem.set_workdir(self.repo.path_abs)

        with self.repo.db_connection(write_db):
            yield True

        filesystem.set_workdir(filesystem.PATH_INIT)

    def init_cmd(self):
        parser = argparse.ArgumentParser(
            description='Creates REPO to curren path')
        return parser

    def init_exe(self, config):
        try:
            with self._open_db_and_cwd(False):
                raise SarchException("Repository exists already!")
        except SarchExceptionNoDB:
            pass

        repo = database.Database(database.DATABASE_FILENAME)
        with repo.db_connection(True):
            repo.create()
        log.debug("Database created ok!")

    def save_cmd(self):
        parser = argparse.ArgumentParser(
            description='Saves current filesystem to REPO')
        parser.add_argument(
            '--path',
            nargs='+',
            help="Optional path to work with, if skipped uses repository base-path",
            default=[
                "",
            ])
        parser.add_argument(
            '--really',
            action='store_true',
            help="Resolve conflicts")
        return parser

    def save_exe(self, config, extra):
        log.debug("Extra is %s", extra)
        if extra:
            config.path = extra
        with self._open_db_and_cwd(False):
            worker = commands.WorkerSave(
                repo=self.repo, resolves=config.really)
            paths = filesystem.make_relative(config.path)
            for path in paths:
                commands.full_scan(path=path, worker=worker, repo=self.repo)
            self.repo.save()
            return worker.status_ok()

    def status_cmd(self):
        parser = argparse.ArgumentParser(
            description='Shows current REPO status')
        parser.add_argument(
            '--verify',
            action="store_true",
            help="Verify contents (checksum) in each file")
        parser.add_argument(
            '--path',
            nargs='+',
            help="Optional path to work with, if skipped uses repository base-path",
            default=[
                "",
            ])
        return parser

    def status_exe(self, config, extra):
        worker = commands.WorkerStatus()

        if extra:
            config.path = extra

        with self._open_db_and_cwd(False):
            paths = filesystem.make_relative(config.path)
            for path in paths:
                commands.full_scan(
                    path=path,
                    worker=worker,
                    repo=self.repo,
                    flag_verify=config.verify)
        return worker.status_ok()

    def sync_cmd(self):
        parser = argparse.ArgumentParser(
            description='Sync with remote repository')
        parser.add_argument('path', nargs=1, help="What path to sync with (rsync target)")
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Do not really sync but print what would happen")
        return parser

    def sync_exe(self, config):
        with self._open_db_and_cwd(False):
            if config.dry_run:
                worker = commands.WorkerSyncPrint()
            else:
                worker = commands.WorkerSync(self.repo)

            # First try to copy remote
            commands.full_scan_import(
                    worker=worker, path=path, repo=self.repo)
            if not config.dry_run:
                self.repo.save()
                
    def import_cmd(self):
        parser = argparse.ArgumentParser(
            description='Import files from given path')
        parser.add_argument('path', nargs=1, help="What path to import")
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Do not import but print what would happen")
        return parser

    def import_exe(self, config):

        with self._open_db_and_cwd(False):
            if config.dry_run:
                worker = commands.WorkerImportPrint()
            else:
                worker = commands.WorkerImport(self.repo)

            for path in config.path:
                commands.full_scan_import(
                    worker=worker, path=path, repo=self.repo)
            if not config.dry_run:
                self.repo.save()


if __name__ == '__main__':
    try:
        Sarch2()
    except SarchException as err:
        print("Error: %s" % err)
        exit(1)
