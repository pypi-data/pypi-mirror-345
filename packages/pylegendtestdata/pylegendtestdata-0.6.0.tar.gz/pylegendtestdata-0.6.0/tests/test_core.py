import pytest
from git import GitCommandError

from legendtestdata import LegendTestData

ldata = LegendTestData()
ldata.checkout("49c7bdc")


def test_get_file():
    ldata.get_path("fcio/th228.fcio")
    ldata["fcio/th228.fcio"]


def test_get_directory():
    ldata.get_path("fcio")
    ldata["fcio"]


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        ldata.get_path("non-existing-file.ext")


def test_git_ref_not_found():
    with pytest.raises(GitCommandError):
        ldata.checkout("non-existent-ref")
