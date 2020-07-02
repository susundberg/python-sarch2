from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile
import subprocess
import datetime

from . import database
from . import common
from . import filesystem

log = common.setup_log("sync")


class SarchExceptionSyncFail(common.SarchException):
    pass


@contextmanager
def with_temp_dir():
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path)


def get_rsync_args(url, dry_run):
    if ":" in url:  # Pretty bad, bad should work with sane urls:
        args = "-hazv"
    else:
        args = "-hav"

    if dry_run:
        args += "n"
    return args


def run_sync_call(cmd):
    log.debug("Running '%s'", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        log.error("Sync command '%s' failed, bailing out!", " ".join(cmd))
        raise SarchExceptionSyncFail("Sync failed")


def copy_from(url, remote_file, local_target):
    cmd = (
        "rsync",
        get_rsync_args(
            url,
            False),
        url +
        str(remote_file),
        str(local_target))
    run_sync_call(cmd)


def sync(url, local_repo, dry_run):
    log.info("Try sync with '%s' - dry run: %s", url, dry_run)

    # Ok first we need to make tempdir
    with with_temp_dir() as path:
        remote_db_path = path / Path(database.DATABASE_FILENAME)

        copy_from(url, database.DATABASE_FILENAME, remote_db_path)

        # Ok, dataabse found, check timestamps
        ts_local = filesystem.get_timestamp(local_repo.path_db, 1000)
        ts_remote = filesystem.get_timestamp(remote_db_path, 1000)

        db_remote = database.Database(remote_db_path, relative=False)
        with db_remote.db_connection(False):
            count = sum(1 for i in db_remote.get_iterator("."))

        if ts_remote > ts_local:

            # Only exception is with empty databases!
            if count == 0:
                log.info("Remote DB seems empty, syncing")
            else:
                log.error(
                    "Remote database is newer than ours, this is not currently supported!")
                raise SarchExceptionSyncFail("Remote DB newer")

        elif ts_remote == ts_local:
            log.info("Remote timestamp same as ours, no changes.")
            return

        # Ok sanity check pass, start syncing
        cmd = ("rsync", get_rsync_args(url, dry_run),
               "--delete", str(local_repo.path_abs) + "/", url)
        run_sync_call(cmd)


def export( remote_path, local_repo, chunk_size, dry_run ):

    #import pdb; pdb.set_trace();

    remote_path = Path( remote_path ).resolve()
    local_path  = local_repo.path_abs

    if remote_path.exists() == False:
            log.error("Target path '%s' does not exists", remote_path )
            raise SarchExceptionSyncFail("Remote does not exists")
    elif remote_path.is_dir() == False:
        log.error("Remote path '%s' exists but is not directory!", remote_path )
        raise SarchExceptionSyncFail("Remote exists and not directory!")
    # Ok, then we are ready to do 
    # tar czpvf - /path/to/archive | split -d -b 100M - tardisk
    
    local_name = str(local_path.parts[-1]) 
    outfile = remote_path / Path( local_name + "_" + datetime.datetime.now().strftime("%Y-%d-%m") + ".split_tgz." )
    
    log.info("Export to '%s' -> '%s'", local_path, outfile )

    cmd = "tar cpvf - .|gzip --stdout --fast|split -a 3 -d -b %s - %s" % ( chunk_size, outfile )
    log.info("Running: '%s'", cmd )
    if dry_run:
        log.info("Dry run defined, skipping execution!")
    else:
        subprocess.run( cmd, check=True, shell=True )
    log.info("All done, bye!")

    

        

   


    