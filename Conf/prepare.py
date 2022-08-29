from os import path
from typing import Dict, Tuple, Optional
from inspect import currentframe
from logging import Logger as Log
from Util import directory
from Logging import logging
from Common import common


def prepare(conf: Optional[Dict]) -> Tuple[Log, Dict]:
    """setup env such as logs and make sure necessary paramters are in place for execution

    Args:
        conf: main user configuration which includes necessary parameters for environment to work

    Returns:
        return logger object and user configuration

    """
    try:
        _logger = None
        if conf:

            # check whether job directory exists
            if not directory.is_dir_exist(conf.get("job_filepath", "")):
                common.error_logger(currentframe().f_code.co_name,
                                    f"the job filepath {conf.get('job_filepath', '')} does not exists", ignore_flag=False)

            # check whether log directory is provided
            if not conf.get("log_filepath", ""):
                common.error_logger(currentframe().f_code.co_name,
                                    f"the log filepath is not specified", ignore_flag=False)

            # check whether progress directory is provided
            if not conf.get("progress_filepath", ""):
                common.error_logger(currentframe().f_code.co_name,
                                    f"the progress filepath is not specified", ignore_flag=False)

            _logger = logging.setup_log("demo", path.join(conf.get("log_filepath"), "demo.log"))

        else:
            common.error_logger(currentframe().f_code.co_name,
                                "main.yml does not exists in the same directory as main.py", ignore_flag=False)

        return _logger, conf
    except Exception as err:
        common.error_logger(currentframe().f_code.co_name, err, None, ignore_flag=False)
