"""
This module contains functions and methods for dynamically monkey-patching a class and adding a
custom method. Additionally, it includes a utility to inject a Python Command containing
an inline Python script into a `WorkUnit` object to move files to an output directory.
"""

from typing import List, Optional

from dnv.onecompute.flowmodel import WorkUnit

from ...oneworkflow.composite_executable_command import CompositeExecutableCommand
from ...oneworkflow.python_command import PythonCommand
from ...oneworkflow.worker_command import WorkerCommand

# Motivation for monkey-patching is:
# - https://mail.python.org/pipermail/python-dev/2008-January/076194.html


def _monkeypatch_method(cls):
    """A decorator function that dynamically adds methods to a class."""

    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


def _monkeypatch_class(name, bases, namespace):
    """
    Dynamically monkeypatches a class by adding attributes from the given namespace to the
    specified base class.
    """
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base


# Inline Python Script for moving the files from the load-case folder to a given destination folder
# folder
INLINE_SCRIPT_MOVE_FILES_FROM_LOAD_CASE_TO_RESULTS_FOLDER = """
import os
import glob
import shutil

destination_dir = os.path.normpath(r'{destination_dir}')
patterns = {file_search_patterns}
destination = os.path.normpath(os.path.join(os.pardir, os.pardir, destination_dir))

os.makedirs(destination, exist_ok=True)

for pattern in patterns:
    for file in glob.glob(pattern, recursive=True):
        try:
            shutil.move(file, destination)
        except shutil.Error as e:
            print(str(e))
"""

# Inline Python Script for copying the files from the shared folder to the load-case folder
INLINE_SCRIPT_COPY_COMMON_FILES_TO_LOAD_CASE_FOLDER = """
import fnmatch
import glob
import os
import shutil
job_prep_wd_evn = 'AZ_BATCH_JOB_PREP_WORKING_DIR'
job_prep_working_dir = os.environ[job_prep_wd_evn] if job_prep_wd_evn in os.environ else None
if job_prep_working_dir is None:
    job_prep_dir = '..\\..\\..\\jobpreparation'
    job_prep_wd_evn = 'OC_SHARED_FOLDER'
    job_prep_working_dir = os.environ[job_prep_wd_evn] if job_prep_wd_evn in os.environ else job_prep_dir
job_prep_working_dir = job_prep_working_dir.strip()
src_folder = os.path.join(job_prep_working_dir, '{shared_foldername}')
src_folder = os.path.normpath(src_folder)
print(f'The source directory is: {{src_folder}}')
load_case_path = os.getcwd()
dest_folder = load_case_path
print(f'The destination directory is: {{dest_folder}}')
os.makedirs(dest_folder, exist_ok=True)
all_files = glob.glob(os.path.join(src_folder, '**/*.*'), recursive=True)
files_to_copy = [
    f
    for f in all_files
    if not any(fnmatch.fnmatch(f, pattern) for pattern in {exclude_files})
]
copied_files = [shutil.copy(file_path, dest_folder) for file_path in files_to_copy]
print('Copied the following files from', src_folder, ':\\n ', '\\n  '.join(copied_files))
"""


def inject_move_file_inline_py_script(
    work_unit: WorkUnit,
    include_files: Optional[List[str]] = None,
    load_case_folder: Optional[str] = None,
    results_folder: Optional[str] = None,
):
    """
    Injects a Python Command containing inline Python script into WorkUnit to move files.

    This function injects a Python Command containing an inline Python script into a 'WorkUnit'
    object. The purpose is to facilitate the movement of files to a specified output directory.
    The function takes the 'WorkUnit' object as a parameter, extracts necessary information such
    as the destination directory and file search patterns from the 'WorkUnit', and prepares the
    inline script to move matching files to the specified output directory.

    If the 'load_case_folder' or 'results_folder' parameters are provided, they will be used as
    the working directory and destination directory, respectively. Otherwise, these values will
    be extracted from the 'WorkUnit' object.

    The function checks the type of the WorkUnit's content. If the content is a
    CompositeExecutableCommand, it appends the inline command to the list of executable commands.
    If the content is a WorkerCommand, it creates a new CompositeExecutableCommand that includes
    the original content and the inline command, and replaces the WorkUnit's content with this
    new CompositeExecutableCommand

    Args:
        work_unit (WorkUnit): The 'WorkUnit' object to which the Python Command will be injected.
        include_files (Optional[List[str]]): List of file search patterns. If not provided,
            patterns will be extracted from the 'WorkUnit'.
        load_case_folder (Optional[str]): The working directory for the Python Command. If not
            provided, the working directory will be extracted from the 'WorkUnit'.
        results_folder (Optional[str]): The destination directory for moved files. If not
            provided, the directory will be extracted from the 'WorkUnit'.
    """
    content = work_unit.data.content
    destination_dir = results_folder or work_unit.output_file_selectors[0].directory
    file_search_patterns = (
        include_files or work_unit.output_file_selectors[0].include_files
    )
    working_directory = load_case_folder or getattr(content, "working_directory", "")
    inline_cmd = PythonCommand("")
    inline_cmd.working_directory = working_directory
    inline_cmd = PythonCommand("")
    script = INLINE_SCRIPT_MOVE_FILES_FROM_LOAD_CASE_TO_RESULTS_FOLDER.format(
        destination_dir=destination_dir,
        file_search_patterns=file_search_patterns,
    )
    inline_cmd.inline_script = script
    inline_cmd.working_directory = working_directory

    if isinstance(content, CompositeExecutableCommand):
        cmds = content.executable_commands
        cmds.append(inline_cmd)
    elif isinstance(content, WorkerCommand):
        composite_exe_cmd = CompositeExecutableCommand(
            [content, inline_cmd], working_directory
        )
        work_unit.data.content = composite_exe_cmd


@_monkeypatch_method(WorkUnit)
def transfer_files_from_loadcase_to_output_directory(
    self: WorkUnit,
    include_files: Optional[List[str]] = None,
    load_case_folder: Optional[str] = None,
    results_folder: Optional[str] = None,
) -> WorkUnit:
    """
    Moves files from the working directory to the output directory of a WorkUnit.

    This method modifies a WorkUnit by injecting a Python Command that contains an inline Python
    script. The script moves specified files from the working directory to the output directory
    of the WorkUnit. The working and output directories, as well as the files to be moved, can be
    specified as parameters. If not provided, these values will be extracted from the WorkUnit.

    Args:
        include_files (Optional[List[str]]): List of file search patterns to be moved. If not
            provided, patterns will be extracted from the WorkUnit.
        load_case_folder (Optional[str]): The working directory for the Python Command. If not
            provided, the working directory will be extracted from the WorkUnit.
        results_folder (Optional[str]): The destination directory for moved files. If not
            provided, the directory will be extracted from the WorkUnit.

    Returns:
        WorkUnit: The same WorkUnit instance, modified to include the file-moving command.
    """
    inject_move_file_inline_py_script(
        self, include_files, load_case_folder, results_folder
    )
    return self


@_monkeypatch_method(WorkUnit)
def with_shared_files_copied_to_loadcase(
    self: WorkUnit,
    shared_foldername: str,
    exclude_files: Optional[List[str]] = None,
) -> WorkUnit:
    """
    Copies Common Files to the Load Case Directory.

    This function injects a Python Command as a first command containing inline Python script into
    a 'WorkUnit' object to facilitate copying files to a load-case directory.

    Args:
        self (WorkUnit): The WorkUnit object.
        shared_foldername (str): The path to the shared folder.
        exclude_files (Optional[List[str]]): A list of file patterns to exclude from the copy
            operation. Defaults to None.

    Returns:
        A modified WorkUnit containing the PythonCommand, which includes the inline Python script.
    """
    exclude_files = exclude_files or []

    work_unit = self
    content = work_unit.data.content
    working_directory = getattr(content, "working_directory", "")

    inline_cmd = PythonCommand("")
    script = INLINE_SCRIPT_COPY_COMMON_FILES_TO_LOAD_CASE_FOLDER.format(
        shared_foldername=shared_foldername, exclude_files=exclude_files
    )
    inline_cmd.inline_script = script
    inline_cmd.working_directory = working_directory

    if isinstance(inline_cmd, WorkerCommand):
        if isinstance(content, CompositeExecutableCommand):
            cmds = content.executable_commands
            cmds.insert(0, inline_cmd)
        elif isinstance(content, WorkerCommand):
            composite_exe_cmd = CompositeExecutableCommand(
                [inline_cmd, content], working_directory
            )
            work_unit.data.content = composite_exe_cmd

    return self
