import hashlib
import os
import sched
import shutil
import time
from pathlib import Path
from typing import Set

from init_config import Config


def file_hash(path: Path):
    """

    :param path: Absolute path to the file
    :return: sha256 hexdigest (hashlib.hexdigest)
    """
    sha256_hash = hashlib.new('sha256')
    with open(path, "rb") as f:
        """
        Use 4096 chunks for efficiency - iterate until the last chunk 
        is an empty bytestring
        """
        for byte_chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_chunk)
    return sha256_hash.hexdigest()


def create_relative_file_and_directory_name_sets(path: Path):
    """

    :param path: Absolute path to the root directory
    :return: dir_set, file_set: set of absolute paths to directories and files under the root directory
    """
    dir_set: Set[Path] = set()
    file_set: Set[Path] = set()
    # root = current dir path; dirs/files = dirs/files under root
    for root, dirs, files in Path.walk(path):
        for subdir in dirs:
            dir_set.add(Path(f"{root.relative_to(path)}/{subdir}"))
        for file in files:
            file_set.add(Path(f"{root.relative_to(path)}/{file}"))
    return dir_set, file_set


def sync(config: Config):
    """
    Runs a single synchronization operation.
    :param config: Program config object
    :return:
    """
    try:
        config.logger.info(f"Running sync every {config.time_interval} second(s)...")

        input_dir_set, input_file_set = create_relative_file_and_directory_name_sets(config.input_path)
        output_dir_set, output_file_set = create_relative_file_and_directory_name_sets(config.output_path)
        """
        1. if a directory
            a) in input_dir_set is not in output_dir_set -> create the missing directory
            b) in output_dir_set is not in input_dir_set -> delete the directory, recursively
        2. if filename in output_file_set
            a) is not in input_file_set - delete it
        3. if a filename in input_file_set
            a) is not in output_file_set -> copy the file (create directories recursively)
            b) is in output_file_set -> check the hash and overwrite the file if it differs

        """

        """
        1a. Create missing directories (this includes empty directories) in output directory
        """
        dirs_missing_relative = input_dir_set - output_dir_set
        files_missing_relative = input_file_set - output_file_set

        # print(f"dirs_missing_relative = {dirs_missing_relative}, files_missing_relative = {files_missing_relative}")

        for dir_to_create in dirs_missing_relative:
            config.logger.info(f"Creating missing directory {dir_to_create}")
            # Reconstruct full path to the directory
            dir_to_create_absolute = config.output_path.joinpath(dir_to_create)
            # need to create the dirs recursively
            os.makedirs(dir_to_create_absolute, exist_ok=True)
        """
        1b. Delete redundant directories and files
        Ok, if not found (that is the point.)
        using shutil.rmtree for simplicity
        """
        dirs_redundant_relative = output_dir_set - input_dir_set
        files_redundant_relative = output_file_set - input_file_set

        for dir_to_delete in dirs_redundant_relative:

            """
            Delete the files from the files_redundant_relative set (as they wont't exist anymore)
            Has to be first, as dir_to_delete is converted to a full path afterwards
            """
            files_redundant_relative = \
                {file for file in files_redundant_relative if not file.is_relative_to(dir_to_delete)}

            # Reconstruct the full path to the directory
            dir_to_delete_absolute = config.output_path.joinpath(dir_to_delete)
            if dir_to_delete_absolute.exists():
                config.logger.info(f"Deleting directory {dir_to_delete}")
                shutil.rmtree(dir_to_delete)

        """
        2a. Delete files that are not in input directory (ok if file does not exist.) 
        """
        for file_to_delete in files_redundant_relative:
            # Reconstruct the full path to the file
            file_dst = config.output_path.joinpath(file_to_delete)
            config.logger.info(f"Removing redundant file: {file_to_delete}")

            file_dst.unlink(missing_ok=True)

        """
        3a. Copy missing files (parent directories should exist now)
        """
        for file_missing in files_missing_relative:
            # Reconstruct the absolute paths
            file_src = config.input_path.joinpath(file_missing)
            file_dst = config.output_path.joinpath(file_missing)
            config.logger.info(f"Copying missing file {file_missing}")
            shutil.copyfile(file_src, file_dst)
        """
        3b. Calculate hashes for files of input and output files now, and overwrite files that differ
        """
        _, output_file_set = create_relative_file_and_directory_name_sets(config.output_path)
        for file in input_file_set:
            file_absolute_path_src = config.input_path.joinpath(file)
            file_absolute_path_dst = config.output_path.joinpath(file)
            while True:
                src_hash = file_hash(file_absolute_path_src)
                dst_hash = file_hash(file_absolute_path_dst)
                if src_hash != dst_hash:
                    config.logger.info(
                        f"Overwriting file\n"
                        f"{file_absolute_path_dst}\n"
                        f"as its hash\n"
                        f"{src_hash} differs with\n"
                        f"{file_absolute_path_src}\n"
                        f"{dst_hash}.")

                    shutil.copy2(file_absolute_path_src, file_absolute_path_dst)

                    """
                    Recalculate the hashes for the copied file
                    """
                    if file_hash(file_absolute_path_src) == file_hash(file_absolute_path_dst):
                        config.logger.info(f"File overwritten successfully, its hash matches the source file hash.")
                        break
                    else:
                        config.logger.error(f"Copied file hash does not match the source file. "
                                            f"Trying again to overwrite the file. "
                                            f"If this hangs, terminate the process and check "
                                            f"the permissions of the file.")
                else:
                    break

    except FileNotFoundError:  # as e:
        print(f"Error: The processed file was not found.")
    except PermissionError:
        print(f"Error: Permission denied when copying file.")
    # except BaseException as e:
    #     print(f"An unhandled exception occurred: {e}, exception type: {type(e).__name__} cause: {e.__cause__}")


def periodic_scheduler(scheduler, interval, function_to_schedule, config):
    """
    A helper function that enables periodic scheduling (it recursively schedules itself
    along with the function that is to be periodically executed)
    """
    scheduler.enter(delay=interval,
                    priority=1,
                    action=periodic_scheduler,
                    argument=(scheduler, interval, function_to_schedule, config)
                    )
    function_to_schedule(config)


def periodic_sync(config: Config):
    """
    Schedules sync as per --time-interval (in seconds) received from the CLI.
    :param config:
    """
    s = sched.scheduler(time.time, time.sleep)
    periodic_scheduler(scheduler=s,
                       interval=config.time_interval,
                       function_to_schedule=sync,
                       config=config)
    s.run()
