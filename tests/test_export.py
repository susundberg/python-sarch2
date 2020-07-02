import common
import unittest
import os
import datetime
import subprocess
from pathlib import Path

unique_name = common.unique_name


def get_timestamp(y, m, d):
    ts = datetime.datetime(y, m, d, 9, 0, 0)
    return int(datetime.datetime.timestamp(ts))


    
class Test(common.TestBase):

    def setUp(self):
        super().setUpClass()
        self.other = common.RepoDir()
        self.other.tempdir_new()

    def tearDown(self):
        self.other.tempdir_clear()
    
    
    
    def test_0_basic(self):
        self.repo.cmd("export", self.other.path, "--chunk-size", "1b" , "--dry-run")
        assert( self.other.n_files() == 0 )
        self.repo.cmd("export", self.other.path, "--chunk-size", "1b")
        assert( self.other.n_files(verbose=True) > 0 )
        # Ok, the file should there, lets extract

        os.chdir(self.other.path)
        subprocess.run( "cat *.split_tgz.*|tar -vzx ", shell=True )
        os.chdir(self.repo.path)
        self.other.file_check("root_file_1", exists=True)



    
if __name__ == "__main__":
    unittest.main()
    
