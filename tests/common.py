
import unittest
import os
import tempfile
import shutil
import subprocess
import uuid

from pathlib import Path


def unique_name( prefix="." ):
     return str(uuid.uuid4())
       

class RepoDir:
   def __init__(self):
       self.path = None
       
   def tempdir_new( self ):
       if self.path:
           self.tempdir_clear()
       self.path  = tempfile.mkdtemp()
   
   def tempdir_clear( self ):
      shutil.rmtree( self.path )
      
   def dir_check( self, filename, exists ):
       f = Path(filename)
       assert( f.is_dir() ==  exists )
       if exists == False:
          assert( f.exists() == False )
          
   def file_check( self, filename, exists  ):
       f = Path(filename)
       assert( f.is_file() ==  exists )
       if exists == False:
          assert( f.exists() == False )
       
   def file_del ( self, filename ):
      fn = Path( filename )
      os.unlink( str(fn) )
   
   def file_copy( self, filename_source, filename_target):
      subprocess.run( "rsync", "-av", filename_source, filename_target, check=True )

   def cmd( self, *pargs, assume_fail = False):
       
       cmd_full = ["python3","-m","sarch2"] + list(pargs) 
       ret = subprocess.run( cmd_full )
       if assume_fail == False:
           if ret.returncode != 0:
              raise Exception("Command '%s' failed with nonzero return!" % cmd_full )
       else: 
           if ret.returncode == 0:
               raise Exception("Command '%s' succeeded though should fail!" % cmd_full )
           
       
   def file_make( self, filenames , content : str = None , timestamp :int = (2**20 + 3145) ):
      
      if type( filenames ) == str:
              filenames = (filenames,)
                           
      for filename in filenames:
        absname_path = Path( filename ).resolve() 
        absname = str(absname_path)
        
        subprocess.run( ("mkdir", "-p", absname_path.parent), check=True )
        
        if content == None:
            content = ( filename ) * 8
            
        with open( absname, 'wb' ) as fid:
            fid.write( bytes(content,"utf8") )
            
        os.utime( str(filename), (timestamp, timestamp ) )
      

   def create_base1( self ):
        self.file_make( "root_file_1")
        self.file_make( "root_file_2")
        self.file_make( "sub1/file_12")
        self.file_make( "sub1/file_12")
        self.file_make( "sub1/sub2/file_121")
        self.file_make( "sub1/sub2/file_122")
        self.file_make( "sub1/sub2/file_123")
        self.file_make( "sub2/file_21")
        subprocess.run( ("find",".") )
  
   def create_repo1( self ):
       os.chdir( self.path )
       self.create_base1()
       self.cmd("init")
       self.cmd("save")
       
       
    
class TestBase( unittest.TestCase ):
   
   
   @classmethod
   def setUpClass( cls ):
       cls.repo = RepoDir()
       cls.repo.tempdir_new()
       cls.repo.create_repo1() 
       
   @classmethod     
   def tearDownClass( cls ):
       cls.repo.tempdir_clear()
      
