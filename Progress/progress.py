from os import path
from inspect import currentframe
from logging import Logger as Log
from typing import Dict, Union, Tuple, List
from Process import process
from SDK import sdk_metadata
from Util import file, util, directory
from Common import common


class Progress:
    def __init__(self, logger: Log = None, home_dir: str = None):
        self._home_dir = home_dir
        self._logger = logger
        directory.createdirectory(self._home_dir)
        self._flow_progress = {}
        self._job_filepath = None

    @property
    def get_home_dir(self):
        return self._home_dir

    def new(self, job_filepath: str) -> str:
        """start a new job, create the necessary path if it hasn't exist yet and generate a job identification token

        Args:
            job_filepath: the directory path of a job which may contains multiple yml task files

        Returns:
            return a job identification token

        """
        try:
            _identity_code = util.get_random_string(16)
            directory.createdirectory(path.join(self._home_dir, _identity_code))
            self.save_progress(_identity_code, None, {}, [])
            self._job_filepath = job_filepath
            return _identity_code
        except Exception as err:
            if _identity_code and directory.is_dir_exist(path.join(self._home_dir, _identity_code)):
                directory.remove_directory(path.join(self._home_dir, _identity_code))
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)

    def set(self, job_filepath: str) -> bool:
        """set job path

        Args:
            job_filepath: the directory path of a job which may contains multiple yml task files

        Returns:
            return a job identification token

        """
        try:
            self._job_filepath = job_filepath if directory.is_dir_exist(job_filepath) else None
            return True
        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)

    def check_progress(self, identity_code: str, step: str) -> bool:
        """check job progress

        Args:
            identity_code: unique job identification token
            step: the step number within a job

        Returns:
            return True if specified step has been completed otherwise False

        """
        try:
            self.check_integrity(identity_code)
            self._flow_progress = file.json_load(path.join(self._home_dir, identity_code, "progress.json"))
            return self._flow_progress.get(step, False)

        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)

    def save_progress(self, identity_code: str,
                      flow_step: Union[str, None],
                      flow_variable: Union[Dict, None],
                      destroy_res_stmt: Union[List, None],
                      destroy_counter: int = None) -> None:
        """save job progress

        Args:
            identity_code: unique job identification token
            flow_step: the step number within a job
            flow_variable: saved variables collected
            destroy_res_stmt: resource removal statment
            destroy_counter: resource removal counter used for task ordering

        Returns:
            None

        """

        try:
            if flow_step is not None:
                self._flow_progress[flow_step] = True
            file.json_dump(path.join(self._home_dir, identity_code, "progress.json"), self._flow_progress)
            file.json_dump(path.join(self._home_dir, identity_code, "variable.json"), flow_variable)
            if destroy_res_stmt:
                file.yaml_dump(path.join(self._home_dir, identity_code, f"{str(destroy_counter)}_destroy_resource.yml"),
                               destroy_res_stmt)

        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)
            raise err

    def load_progress(self, identity_code: str) -> Tuple[Dict, Dict]:
        """load job progress from disk

        Args:
            identity_code: unique job identification token


        Returns:
            return both saved variable and job counter - how far the job has progressed

        """
        try:
            self.check_integrity(identity_code)
            return file.json_load(path.join(self._home_dir, identity_code, "variable.json")), \
                   file.json_load(path.join(self._home_dir, identity_code, "progress.json"))

        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)
            raise err

    def run(self, identity_code: str):
        """run a job

        Args:
            identity_code: unique job identification token


        Returns:
            None

        """

        _resource_removal = []
        try:
            _saved_variable, _saved_progress = self.load_progress(identity_code)

            _completed_steps = {int(_step) for _step, _result in _saved_progress.items() if _result}

            for _job in [file_name for file_name in sorted([fname for fname in directory.files_in_dir(self._job_filepath)
                                                      if fname.endswith(".yml")], key=lambda x:int(x.split("_")[0]))]:

                _job_id = int(_job.split("_")[0])
                if _job_id not in _completed_steps:
                    _job_detail = file.yaml_load_from_f(path.join(self._job_filepath, _job))
                    if not _job_detail: continue
                    _saved_variable, _des_res_stmt = process.preprocessing(sdk_metadata._SDK_FUNC_DICT,
                                                                           _job_detail,
                                                                           _saved_variable,
                                                                           self._logger)

                    self.save_progress(identity_code, str(_job_id), _saved_variable, None, 0)

                    if _des_res_stmt:
                        _resource_removal.append(_des_res_stmt)
                else:
                    print(f"skipping job id {_job_id}... it has been successfully completed")

            _destroy_counter = 10000
            for _res_removal_task in _resource_removal[::-1]:
                file.yaml_dump(path.join(self._home_dir, identity_code,
                                         f"{str(_destroy_counter)}_destroy_resource.yml"),
                                         _res_removal_task)
                _destroy_counter += 1000

        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, logger=self._logger, ignore_flag=False)

    def check_integrity(self, identity_code: str) -> None:
        """check integrity of save progress feature to see whether required resources are work properly

        Args:
            identity_code: unique job identification token


        Returns:
            None

        """
        try:
            if not directory.is_dir_exist(path.join(self._home_dir, identity_code)):
                common.error_logger(currentframe().f_code.co_name, "identity code is not valid", self._logger)
                raise "ERROR: identity code is not valid"

            if not file.is_file_exist(path.join(self._home_dir, identity_code, "variable.json")):
                common.error_logger(currentframe().f_code.co_name,
                                    f"variable file is not found in {path.join(self._home_dir, identity_code)}",
                                    self._logger)
                print(f"ERROR: variable file is not found in {path.join(self._home_dir, identity_code)}")
                raise

            if not file.is_file_exist(path.join(self._home_dir, identity_code, "progress.json")):
                common.error_logger(currentframe().f_code.co_name,
                                    f"progress file is not found in {path.join(self._home_dir, identity_code)}",
                                    self._logger)
                print(f"ERROR: progress file is not found in {path.join(self._home_dir, identity_code)}")
                raise

        except Exception as err:
            common.error_logger(currentframe().f_code.co_name, err, self._logger, ignore_flag=False)
