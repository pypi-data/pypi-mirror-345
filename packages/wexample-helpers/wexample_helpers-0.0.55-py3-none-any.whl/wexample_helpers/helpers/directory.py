import os
import shutil
from contextlib import contextmanager
from typing import Any, Callable, List

from wexample_helpers.helpers.file import file_read

AnyCallable = Callable[..., Any]


def directory_remove_tree_if_exists(directory: str) -> None:
    """Remove a directory and all its contents if it exists."""
    if os.path.exists(directory):
        shutil.rmtree(directory)


@contextmanager
def directory_execute_inside(target_dir: str):
    """
    Context manager to execute code inside a specific directory.

    Usage:
        with directory_execute_inside('path/to/dir'):
            # code here
    """
    original_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(original_dir)


def directory_execute_inside_fn(target_dir: str, callback: AnyCallable) -> Any:
    """Execute a callback inside the target directory and return its result."""
    with directory_execute_inside(target_dir):
        return callback()


def directory_get_base_name(path: str) -> str:
    """Return the base name of a path (last component)."""
    return os.path.basename(os.path.normpath(path))


def directory_get_parent_path(path: str) -> str:
    """Return the parent directory path with trailing separator."""
    parent = os.path.dirname(os.path.normpath(path))
    return parent + os.sep if parent else os.sep


def directory_empty_dir(dir_path: str) -> None:
    """Remove all contents within a directory, but keep the directory itself."""
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"{dir_path!r} is not a directory.")
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path) and not os.path.islink(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)


def directory_list_files(dir_path: str) -> List[str]:
    """List all files in directory and subdirectories, sorted alphabetically."""
    file_paths: List[str] = []
    for root, _, files in os.walk(dir_path):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                file_paths.append(full_path)
    return file_paths


def directory_aggregate_all_files(file_paths: List[str]) -> str:
    """Aggregate contents of the given list of file paths."""
    return os.linesep.join(file_read(fp) for fp in file_paths)


def directory_aggregate_all_files_from_dir(dir_path: str) -> str:
    """Aggregate contents of all files in a directory and its subdirectories."""
    return directory_aggregate_all_files(directory_list_files(dir_path))
