"""
dupln - A Python package for finding and managing duplicate files.

This module provides core functionality for:
- Scanning directories and building a file metadata database
- Identifying duplicate files by size, inode, and content hash
- Linking duplicates to save disk space
- Listing unique/duplicate files with various filters
"""

from hashlib import md5
from os.path import join, dirname, exists, samefile
from os import walk, unlink, chmod, rename, link, symlink, stat
from logging import info, error
from tempfile import mktemp
from stat import S_ISREG, S_IWUSR


def add_file(db, path, size, ino, dev, mtime):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], str, int, int, int, float) -> None
    """
    Add a file to the database structure organized by:
    - Device ID (to handle multiple filesystems)
    - File size (first level of duplicate detection)
    - Inode number (for hardlink detection)
    - File paths (set of paths sharing same inode/size)

    Args:
        db: The database dictionary to populate
        path: Full path to the file
        size: File size in bytes
        ino: Inode number
        dev: Device ID
        mtime: Modification time (unused in current implementation)
    """
    # Get or create device map
    dev_map = db.get(dev)
    if dev_map is None:
        dev_map = db[dev] = {}

    # Get or create size map for this device
    size_map = dev_map.get(size)
    if size_map is None:
        size_map = dev_map[size] = {}

    # Get or create inode map for this size
    ino_map = size_map.get(ino)
    if ino_map is None:
        size_map[ino] = set([path])  # New entry with single path
    else:
        ino_map.add(path)  # Add to existing set of paths


def calc_md5(src, block_size=131072):
    # type: (str, int) -> str
    """
    Calculate MD5 hash of a file in chunks to handle large files efficiently.

    Args:
        src: Path to the file
        block_size: Read buffer size in bytes (default: 128KB)

    Returns:
        Hexadecimal MD5 hash string
    """
    m = md5()
    with open(src, "rb") as h:
        while True:
            b = h.read(block_size)
            if not b:
                break
            m.update(b)
    return m.hexdigest()


def file_sort_key(x):
    # type: (str) -> float
    """
    Key function for sorting files by modification time (oldest first).
    Used to determine which file to keep as original when linking duplicates.
    """
    return stat(x).st_mtime


def link_duplicates(db, linker, tot, carry_on):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Union[Callable[[str, str], None],None], Any, bool) -> None
    """
    Process the database to identify and link duplicate files.

    Args:
        db: The file database structure
        linker: Function to use for linking (None for dry-run)
        tot: Counter object to accumulate statistics
        carry_on: Continue on errors if True
    """
    if len(db) > 1:
        tot.devices = len(db)

    while db:
        dev, size_map = db.popitem()
        while size_map:
            size, ino_map = size_map.popitem()

            # Skip files with unique sizes or zero-length files
            if len(ino_map) < 2 or size < 1:
                while ino_map:
                    ino, paths = ino_map.popitem()
                    n = len(paths)
                    if n > 1:
                        tot.same_ino += 1  # Count hardlinks
                    tot.files += n
                    tot.inodes += 1
                    tot.size += n * size
                    tot.disk_size += size
                continue
            else:
                tot.same_size += 1  # Potential duplicates

            # Initialize MD5 map if we're actually linking files
            md5_map = {} if linker else 0

            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                if n > 1:
                    tot.same_ino += 1
                tot.files += n
                tot.inodes += 1

                if md5_map == 0:
                    # Just count files if not linking
                    tot.size += size * n
                    tot.disk_size += size
                else:
                    # Calculate MD5 hashes for potential duplicates
                    src = paths.pop()
                    file_hash = calc_md5(src)
                    files = md5_map.get(file_hash)
                    if files is None:
                        md5_map[file_hash] = set([src])
                    else:
                        files.add(src)

            # Process files with matching hashes
            while md5_map:
                file_hash, files = md5_map.popitem()
                n = len(files)
                tot.size += size * n

                if n > 1:
                    tot.same_hash += 1
                    try:
                        if linker is None:
                            n = len(files)  # Just count for dry-run
                        else:
                            # Actually link the duplicates
                            n = link_dups(linker, sorted(files, key=file_sort_key))
                    except Exception:
                        tot.link_err += 1
                        if not carry_on:
                            raise
                        from sys import exc_info

                        error(exc_info()[1])
                    else:
                        tot.linked += n
                        tot.disk_size += size
                else:  # n == 1
                    tot.unique_hash += 1
                    tot.disk_size += size


def link_dups(linker, dups):
    # type: (Callable[[str, str], None], List[str]) -> int
    """
    Replace duplicate files with links to a single original.

    Args:
        linker: Function to create links
        dups: List of duplicate file paths (sorted with original first)

    Returns:
        Number of successful links created
    """
    src = ""  # Will hold the original file path
    n = 0  # Count of successful links

    while dups:
        dup = dups.pop()
        if src:
            # Safety checks
            assert dup != src
            assert exists(dup)

            # Use temp file for atomic replacement
            tmp = mktemp(dir=dirname(dup))
            rename(dup, tmp)  # Move duplicate to temp location
            assert exists(tmp)
            assert not exists(dup)

            info(" - %r - %r [%s]", dup, tmp, len(dups))
            try:
                # Attempt to create link
                linker(src, dup)
            except OverflowError:
                # Too many hardlinks - revert
                if exists(tmp):
                    rename(tmp, dup)
                src = dup  # Use this as new original
                info("\t! Too many links")
            except Exception:
                # Other errors - revert
                info("\t! Link failed")
                if exists(tmp):
                    rename(tmp, dup)
                raise
            else:
                # Success - delete temp file
                n += 1
                assert exists(dup)
                assert samefile(src, dup)
                chmod(tmp, S_IWUSR)  # Ensure write permission
                unlink(tmp)
        else:
            # First file becomes the original
            src = dup
            info("++ %r [%s]", src, len(dups))
    return n


def get_linker(use_linker):
    # type: (str) -> Callable[[str, str], None]
    """
    Factory function to create appropriate linker function.

    Args:
        use_linker: Type of linker to use ('os.link', 'ln', etc.)

    Returns:
        Function that takes (src, dst) and creates a link
    """
    from subprocess import call

    if use_linker == "ln":

        def fun(src, dst):
            call(["ln", src, dst])

    elif use_linker == "lns":

        def fun(src, dst):
            call(["ln", "-s", src, dst])

    elif use_linker == "os.link":
        fun = link
    elif use_linker == "os.symlink":
        fun = symlink
    else:
        raise RuntimeError(f"Unknown linker {use_linker!r}")
    return fun


def list_uniques(db, tot):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Any) -> None
    """
    Print all unique files (no duplicates found).

    Args:
        db: The file database
        tot: Counter object for statistics
    """
    tot.devices = len(db)

    while db:
        dev, size_map = db.popitem()
        tot.unique_size = len(size_map)
        while size_map:
            size, ino_map = size_map.popitem()
            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                if n > 1:
                    tot.same_ino += 1
                tot.files += n
                tot.inodes += 1
                tot.size += n * size
                tot.disk_size += size
                path = paths.pop()
                print(path)


def list_duplicates(db, tot, size_filter=None, filesizef=None):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Any, Union[Callable[[int], bool], None], Union[Callable[[int], str], None]) -> None
    """
    Print all duplicate files with optional filtering.

    Args:
        db: The file database
        tot: Counter object for statistics
        size_filter: Optional function to filter by size
        filesizef: Optional function to format size for display
    """
    tot.devices = len(db)
    if filesizef is None:
        filesizef = lambda x: str(x)

    while db:
        dev, size_map = db.popitem()
        tot.unique_size = len(size_map)
        while size_map:
            size, ino_map = size_map.popitem()
            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                w = n > 1
                if w:
                    if size_filter is not None:
                        w = size_filter(size)
                    tot.same_ino += 1
                    if w:
                        print(f"+ inode:{ino} links:{n} size:{filesizef(size)}")
                        for p in paths:
                            print(f" - {p}")
                tot.files += n
                tot.inodes += 1
                tot.size += n * size
                tot.disk_size += size
                path = paths.pop()


def dump_db(db):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]]) -> None
    """
    Print the database structure in YAML or JSON format.

    Args:
        db: The file database to dump
    """
    from sys import stdout

    data = db.popitem()[1] if len(db) == 1 else db  # type: Any

    try:
        from yaml import safe_dump
    except ImportError:
        from json import dump, JSONEncoder

        class SetEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, set):
                    return list(obj)
                return JSONEncoder.default(self, obj)

        dump(data, stdout, cls=SetEncoder, indent=4)
    else:
        return safe_dump(data, stdout, canonical=False, tags=False, indent=True)


def scan_dir(tree, db, statx):
    # type: (str, Dict[int, Dict[int, Dict[int, Set[str]]]], Callable[[str], tuple]) -> None
    """
    Recursively scan a directory and populate the file database.

    Args:
        tree: Root directory to scan
        db: Database to populate
        statx: Function to get file metadata
    """
    info("Scanning: %r", tree)
    for root, dirs, files in walk(tree):
        for name in files:
            f = join(root, name)
            (mode, size, ino, dev, mtime) = statx(f)
            if S_ISREG(mode):  # Only process regular files
                add_file(db, f, size, ino, dev, mtime)


# Type checking support
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *
