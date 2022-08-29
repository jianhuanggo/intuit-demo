import time
from sys import exit
from logging import Logger as Log
from functools import wraps


def error_logger(func_str: str,
                 error,
                 logger: Log = None,
                 addition_msg: str = "",
                 mode: str = "critical",
                 ignore_flag: bool = True,
                 set_trace: bool = False) -> None:
    """Display error message in a logger if there is one otherwise stdout

    Args:
        func_str: calling function, so error msg can be associated correctly
        error: exception captured
        logger: Whether error msg should be persisted in a log file
        addition_msg: A set of parameters which need to be verified
        mode: error mode, either critical, debug, error or info
        ignore_flag: It will return to the calling function if set to True otherwise program will terminate
        set_trace: This will log stack trace

    Returns:
        No return value.

    """
    def _not_found(*args, **kwargs):
        raise "error mode should be 'critical', 'debug', 'error' and 'info'"
    if logger:
            _log_mode = {"critical": logger.critical,
                         "debug": logger.debug,
                         "error": logger.error,
                         "info": logger.info}
    try:
        _log_mode.get(mode, _not_found)(f"Error in {func_str}! {addition_msg} {error}") if logger \
            else print(f"Error in {func_str}! {addition_msg} {error}")
        if logger and set_trace: logger.exception("trace")
        return exit(99) if not ignore_flag else None
    except Exception as err:
        raise err
