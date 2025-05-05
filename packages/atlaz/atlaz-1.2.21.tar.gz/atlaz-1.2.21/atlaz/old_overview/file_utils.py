from pathlib import Path

def skip_depth(root_path: Path, base_path: Path, max_depth: int) -> bool:
    """
    Returns True if root_path is deeper than max_depth relative to base_path.
    """
    return len(root_path.relative_to(base_path).parts) > max_depth

def filter_dirs(root_path: Path, dirs: list, ignore_spec, manual_ignore_files: list) -> list:
    """
    Removes directories from 'dirs' if they match ignore patterns or
    are in manual_ignore_files.
    """
    return [d for d in dirs if not is_ignored_file(root_path / d, ignore_spec, manual_ignore_files)]

def filter_files(root_path: Path, files: list, ignore_spec, manual_ignore_files: list) -> list:
    """
    Removes files from 'files' if they match ignore patterns or
    are in manual_ignore_files.
    """
    return [f for f in files if not is_ignored_file(root_path / f, ignore_spec, manual_ignore_files)]

def is_ignored_file(file_path: Path, ignore_spec, manual_ignore_files: list) -> bool:
    """
    Returns True if file_path is matched by ignore_spec or is explicitly
    in manual_ignore_files.
    """
    if ignore_spec and ignore_spec.match_file(file_path.relative_to(file_path.anchor).as_posix()):
        return True
    if manual_ignore_files and file_path.name in manual_ignore_files:
        return True
    return False
