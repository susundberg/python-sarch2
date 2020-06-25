

import common
import unittest
import os
from pathlib import Path

unique_name = common.unique_name


class Test(common.TestBase):
    def test_0_basic(self):
        self.repo.cmd("status")

    def test_1_untracked_root(self):
        un1 = unique_name()
        un2 = unique_name()
        self.repo.file_make((un1, un2))
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save", un1)
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save", un2)
        self.repo.cmd("status")
        uns = (unique_name(), unique_name())
        self.repo.file_make(uns)
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save", *uns)
        self.repo.cmd("status")

    def test_1_untracked_subdir(self):
        uns = (unique_name() + "/" + unique_name(), "sub1/" + unique_name())
        for un in uns:
            self.repo.file_make(un)
            self.repo.cmd("status", assume_fail=True)
            self.repo.cmd("save")
            self.repo.cmd("status")

    def test_2_del(self):

        for fn in ("root_file_1", "sub1/sub2/file_121"):
            self.repo.file_del(fn)
            self.repo.cmd("status", assume_fail=True)
            self.repo.cmd("save")
            self.repo.cmd("status")

        for fn in ("root_file_2", "sub1/sub2/file_122"):
            self.repo.file_del(fn)

        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save")
        self.repo.cmd("status")

        self.repo.tempdir_new()
        self.repo.create_repo1()

    def test_2_del_dir(self):
        un2 = unique_name() + "/" + unique_name()
        self.repo.file_make(un2)

        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.file_del(un2)
        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.dir_check(un2.split("/")[0], exists=False)

    def test_2_del_dir_gone(self):
        un2 = unique_name() + "/" + unique_name()
        self.repo.file_make(un2)
        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.file_remove_dir( un2.split("/")[0] )
        self.repo.dir_check(un2.split("/")[0], exists=False)
        self.repo.cmd("save")
        self.repo.cmd("status")



    def test_2_del_reapear(self):
        un1 = "sub1/sub2/sub3/sub4/" + unique_name()
        self.repo.file_make(un1)

        self.repo.cmd("save")
        self.repo.file_del(un1)
        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.file_make(un1)
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.file_check(un1, exists=False)
        self.repo.dir_check("sub1/sub2/sub3/", exists=False)

    def test_3_modify(self):
        self.repo.file_make("root_file_1",
                            content="This is really unique content")
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save")
        self.repo.cmd("status")

    def test_4_conflict(self):
        self.repo.file_del("root_file_1")
        self.repo.cmd("save")
        self.repo.cmd("status")
        self.repo.file_make("root_file_1", content=unique_name())
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save", assume_fail=True)
        self.repo.cmd("save", "root_file_1", assume_fail=True)
        self.repo.cmd("save", "root_file_1", "--really")
        self.repo.cmd("status")

    def test_5_subdir(self):
        self.repo.file_make("sub2/" + unique_name())
        self.repo.cmd("status", ".", assume_fail=True)
        os.chdir(self.repo.path / Path("sub1"))
        self.repo.cmd("status", ".")
        self.repo.cmd("save")
        os.chdir(self.repo.path)
        self.repo.cmd("status", ".", assume_fail=True)
        os.chdir(self.repo.path / Path("sub2"))
        self.repo.cmd("status", ".", assume_fail=True)
        self.repo.cmd("save")
        self.repo.cmd("status", ".")
        os.chdir(self.repo.path)
        self.repo.cmd("status")

    def test_9_double_create(self):
        self.repo.tempdir_new()
        os.chdir(self.repo.path)
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("init")
        self.repo.cmd("status")
        self.repo.create_base1()
        self.repo.cmd("init", assume_fail=True)
        self.repo.cmd("status", assume_fail=True)
        self.repo.cmd("save", "--path", ".")
        self.repo.cmd("status")


if __name__ == "__main__":
    unittest.main()
