import common
import unittest
import os
import datetime

unique_name = common.unique_name


def get_timestamp(y, m, d):
    ts = datetime.datetime(y, m, d, 9, 0, 0)
    return int(datetime.datetime.timestamp(ts))


class Test(common.TestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other = common.RepoDir()
        cls.other.tempdir_new()

    def make_import(self):
        self.other.file_make("imp_1", timestamp=get_timestamp(2017, 11, 29))
        self.other.file_make(
            "sub_1/imp_2",
            timestamp=get_timestamp(
                2017,
                11,
                29))
        self.other.file_make(
            "sub_2/imp_3",
            timestamp=get_timestamp(
                2019,
                1,
                1))

    def test_0_basic(self):
        self.make_import()
        self.repo.cmd("import", "--dry-run", str(self.other.path))
        self.repo.file_check("2017-11/imp_2", exists=False)
        self.repo.cmd("import", str(self.other.path))
        self.repo.cmd("status")
        self.repo.file_check("2017-11/imp_1", exists=True)
        self.repo.file_check("2017-11/imp_2", exists=True)

    def test_1_re_import(self):
        self.make_import()
        self.repo.cmd("import", str(self.other.path))
        self.repo.file_del("2019-01/imp_3")
        self.repo.cmd("save")
        self.other.file_check("sub_2/imp_3", exists=True)
        self.repo.cmd("import", str(self.other.path))
        self.repo.cmd("status")
        self.repo.file_check("2019-01/imp_3", exists=False)


if __name__ == "__main__":
    unittest.main()
