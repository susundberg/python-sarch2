import common
import unittest
import os
import datetime

from pathlib import Path

unique_name = common.unique_name




class Test(common.TestBase):
    
    @classmethod
    def setUp(self):
        super().setUpClass()
        cls.other = common.RepoDir()
        cls.other.tempdir_new()
        
   
    def test_0_basic( self ):
       self.repo.cmd("sync", self.other.path, assume_fail = True )
       os.chdir( self.other.path )
       self.other.cmd("init")
       os.chdir( self.repo.path )
       self.repo.cmd("sync", self.other.path )
       un = unique_name() / unique_name()
       self.repo.file_make( un )
       self.repo.file_del( "root_1" )
       self.repo.cmd("save")
       self.repo.cmd("sync", self.other.path )
       self.other.file_check( un, exists=True )
       self.other.file_check( "root_1", exists=False )
       
       
       
