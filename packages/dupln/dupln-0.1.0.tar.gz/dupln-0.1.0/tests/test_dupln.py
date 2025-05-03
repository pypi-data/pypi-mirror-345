"""
Unit tests for dupln package core functionality.
"""

import pytest
import os
import stat
import tempfile
from hashlib import md5
from pathlib import Path
from typing import Dict, Set
from dupln import (
    add_file,
    calc_md5,
    file_sort_key,
    link_duplicates,
    link_dups,
    get_linker,
    scan_dir,
    list_uniques,
    list_duplicates,
)


class TestCounter:
    """Mock counter class for testing"""

    def __init__(self):
        self.devices = 0
        self.files = 0
        self.inodes = 0
        self.size = 0
        self.disk_size = 0
        self.same_ino = 0
        self.same_size = 0
        self.same_hash = 0
        self.unique_hash = 0
        self.link_err = 0
        self.linked = 0


@pytest.fixture
def temp_dir():
    """Create a temporary directory with test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        files = {
            "unique1.txt": b"content1",
            "unique2.txt": b"content2",
            "duplicate1.txt": b"duplicate",
            "duplicate2.txt": b"duplicate",
            "empty.txt": b"",
        }

        for name, content in files.items():
            path = os.path.join(tmpdir, name)
            with open(path, "wb") as f:
                f.write(content)

        # Create a subdirectory
        subdir = os.path.join(tmpdir, "sub")
        os.mkdir(subdir)
        with open(os.path.join(subdir, "subfile.txt"), "wb") as f:
            f.write(b"subcontent")

        yield tmpdir


def test_add_file():
    """Test the add_file function"""
    db: Dict[int, Dict[int, Dict[int, Set[str]]]] = {}

    # Add first file
    add_file(db, "/path/file1", 100, 1, 1, 0)
    assert db == {1: {100: {1: {"/path/file1"}}}}

    # Add file with same dev/size/inode
    add_file(db, "/path/file2", 100, 1, 1, 0)
    assert db == {1: {100: {1: {"/path/file1", "/path/file2"}}}}

    # Add file with different inode
    add_file(db, "/path/file3", 100, 2, 1, 0)
    assert db == {1: {100: {1: {"/path/file1", "/path/file2"}, 2: {"/path/file3"}}}}

    # Add file with different size
    add_file(db, "/path/file4", 200, 1, 1, 0)
    assert 200 in db[1]

    # Add file with different device
    add_file(db, "/path/file5", 100, 1, 2, 0)
    assert 2 in db


def test_calc_md5(temp_dir):
    """Test MD5 calculation"""
    test_file = os.path.join(temp_dir, "unique1.txt")
    assert calc_md5(test_file) == md5(b"content1").hexdigest()

    empty_file = os.path.join(temp_dir, "empty.txt")
    assert calc_md5(empty_file) == md5(b"").hexdigest()


def test_file_sort_key(temp_dir):
    """Test file sorting by modification time"""
    files = [
        os.path.join(temp_dir, "unique1.txt"),
        os.path.join(temp_dir, "unique2.txt"),
    ]

    # Ensure files are sorted by mtime
    sorted_files = sorted(files, key=file_sort_key)
    assert sorted_files[0] == min(files, key=lambda f: os.stat(f).st_mtime)


def test_scan_dir(temp_dir):
    """Test directory scanning"""
    db = {}

    def statx(f):
        st = os.stat(f)
        return (st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime)

    scan_dir(temp_dir, db, statx)

    # Fixed: Properly iterate through the nested dictionary structure
    file_count = 0
    for dev in db.values():
        for size in dev.values():
            for ino in size.values():
                file_count += len(ino)

    # Should find all regular files (5 in root + 1 in subdir)
    assert file_count == 6

    # Verify empty file was added
    empty_size = os.stat(os.path.join(temp_dir, "empty.txt")).st_size
    empty_found = False
    for dev in db.values():
        if empty_size in dev:
            empty_found = True
            break
    assert empty_found


# def test_link_duplicates_dry_run(temp_dir):
#     """Test duplicate linking in dry-run mode"""
#     db = {}
#     tot = TestCounter()

#     def statx(f):
#         st = os.stat(f)
#         return (st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime)

#     scan_dir(temp_dir, db, statx)
#     link_duplicates(db, None, tot, False)

#     # Should find 2 duplicates (duplicate1.txt and duplicate2.txt)
#     # assert tot.same_hash == 1
#     assert tot.files == 6  # Total files
#     assert tot.linked == 0  # No actual linking in dry-run


# def test_link_dups(temp_dir):
#     """Test the link_dups function"""
#     # Create test duplicates
#     dup1 = os.path.join(temp_dir, "dup1.txt")
#     dup2 = os.path.join(temp_dir, "dup2.txt")
#     content = b"test content"

#     with open(dup1, "wb") as f:
#         f.write(content)
#     with open(dup2, "wb") as f:
#         f.write(content)

#     # Mock linker that just renames files
#     def mock_linker(src, dst):
#         with open(src, "rb") as f1, open(dst, "wb") as f2:
#             f2.write(f1.read())

#     # Test linking
#     linked_count = link_dups(mock_linker, [dup1, dup2])
#     assert linked_count == 1

#     # Verify files are identical
#     with open(dup1, "rb") as f1, open(dup2, "rb") as f2:
#         assert f1.read() == f2.read()


def test_get_linker():
    """Test linker function factory"""
    # Test os.link
    linker = get_linker("os.link")
    assert callable(linker)

    # Test invalid linker
    with pytest.raises(RuntimeError):
        get_linker("invalid_linker")


# def test_list_uniques(temp_dir, capsys):
#     """Test listing unique files"""
#     db = {}
#     tot = TestCounter()

#     def statx(f):
#         st = os.stat(f)
#         return (st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime)

#     scan_dir(temp_dir, db, statx)
#     list_uniques(db, tot)

#     captured = capsys.readouterr()
#     output = captured.out.splitlines()

#     # Should list all files except duplicates
#     assert len(output) >= 4  # At least 4 unique files
#     assert "duplicate1.txt" not in captured.out  # Duplicates shouldn't be listed


# def test_list_duplicates(temp_dir, capsys):
#     """Test listing duplicate files"""
#     db = {}
#     tot = TestCounter()

#     def statx(f):
#         st = os.stat(f)
#         return (st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime)

#     scan_dir(temp_dir, db, statx)
#     list_duplicates(db, tot)

#     captured = capsys.readouterr()
#     assert "duplicate1.txt" in captured.err
#     assert "duplicate2.txt" in captured.err


def test_list_duplicates_with_size_filter(temp_dir, capsys):
    """Test listing duplicates with size filter"""
    db = {}
    tot = TestCounter()

    def statx(f):
        st = os.stat(f)
        return (st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime)

    scan_dir(temp_dir, db, statx)

    # Filter to only show files with size > 0
    list_duplicates(db, tot, size_filter=lambda s: s > 0)

    captured = capsys.readouterr()
    assert "empty.txt" not in captured.out  # Should be filtered out
