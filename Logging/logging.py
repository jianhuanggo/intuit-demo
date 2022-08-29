import logging
from inspect import currentframe
from logging import Logger as Log
from logging.handlers import RotatingFileHandler
from Common import common
from Util import directory


def setup_log(log_name: str, log_filepath: str) -> Log:
    """Start a logger with rotation setup

    Args:
        log_name: name of log object
        log_filepath: the filepath of the log

    Returns:
        return logger object

    """
    try:

        if not log_filepath.endswith(".log"):
            common.error_logger(currentframe().f_code.co_name,
                                f"the log filepath {log_filepath} does not end with .log", None, ignore_flag=False)
        _directory = '/'.join(log_filepath.split("/")[:-1])
        directory.createdirectory(_directory)
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(log_filepath, maxBytes=10000, backupCount=10)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    except Exception as err:
        raise err

