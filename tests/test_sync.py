import common
import unittest
import os
import datetime

from pathlib import Path

unique_name = common.unique_name


    
class Test(common.TestBase):

    def setUp(self):
        super().setUpClass()
        self.other = common.RepoDir()
        self.other.tempdir_new()

    def tearDown(self):
        self.other.tempdir_clear()
    
    
    
    def test_0_basic(self):
        self.repo.cmd("sync", "--dry-run", self.other.path, assume_fail=True)
        self.other.file_check("root_file_1", exists=False)
        os.chdir(self.other.path)
        self.other.cmd("init")
        self.other.cmd("status")
        os.chdir(self.repo.path)
        self.repo.cmd("sync", self.other.path)
        self.other.file_check("root_file_1", exists=True)

        un = unique_name() + "/" + unique_name()
        self.repo.file_make(un)
        self.repo.file_del("root_file_1")
        self.repo.cmd("save")
        self.repo.cmd("sync", "--dry-run", self.other.path)
        self.other.file_check(un, exists=False)
        self.repo.cmd("sync", self.other.path)
        self.other.file_check(un, exists=True)
        self.other.file_check("root_file_1", exists=False)
    
    def test_1_conflict( self ):
        os.chdir(self.other.path)
        self.other.cmd("init")
        un = unique_name() + "/" + unique_name()
        self.other.file_make( un )
        self.other.cmd("save")
        
        os.chdir(self.repo.path)
        self.repo.cmd("sync", "--dry-run", self.other.path, assume_fail=True)
        self.repo.cmd("sync", self.other.path, assume_fail=True)
        
        
   
if __name__ == "__main__":
    unittest.main()
