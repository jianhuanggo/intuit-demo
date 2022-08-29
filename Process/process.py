import time
from typing import Dict, Optional, List, Tuple, Callable, Any
from logging import Logger as Log
from inspect import currentframe
from Common import common
from collections import defaultdict, deque
from Jobs.Example import example
from retry import retry
from Util import util, file


def _fileb(filepath: str) -> bytes:
    """Register commonly used variable

    Args:
        filepath: the absolute path of the file

    Returns:
        return the content of the file

    """
    try:
        if file.is_file_exist(filepath):
            with open(filepath, "rb") as bfile:
                return bfile.read()
        else:
            common.error_logger(currentframe().f_code.co_name,
                                f"{filepath} does not exist",
                                logger=None,
                                mode="error", ignore_flag=False)
    except Exception as err:
        raise err


_CORE_FUNC = {"$$fileb://": _fileb,
              "$$unique_string": util.get_random_string,
              "$$json_loads://": file.json_loads,
              "$$dynamodb_put_item_disk": example.dynamodb_put_item_disk
              }


@retry(tries=3, delay=2, jitter=1)
def _sdk_execution(func: Callable, logger: Log = None, **func_kwargs):
    """Execute the aws sdk function using input_parameter

    Args:
        func: can be any function, but mostly aws sdk function
        logger: logger is None, then msg will be print on the standout
        func_kwargs: input parameters

    Returns:
        No return value.

    """
    try:
        _result = func(**func_kwargs)
        time.sleep(2)
        return _result
    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _process_validate(func_dict: Dict, task: Dict, require_fields: List, logger: Log = None) -> bool:
    """Execute the aws sdk function using input_parameter

    Args:
        func_dict: contains a list of function to be validated against
        task: contains information about a resource
        require_fields: fields need to be present in order for validation to be passed
        logger: logger

    Returns:
        True if pass validation else False

    """
    try:
        for _field in require_fields:
            if _field not in task:
                common.error_logger(currentframe().f_code.co_name, f"field {_field} is missing from {task}",
                                    logger=logger,
                                    mode="error", ignore_flag=False)

            if not task.get(_field):
                common.error_logger(currentframe().f_code.co_name, f"field {_field} in task {task} is empty",
                                    logger=logger,
                                    mode="error", ignore_flag=False)

        if func_dict.get(task.get("___sdk_func_name___", None), None):
            return True
        else:
            common.error_logger(currentframe().f_code.co_name, f"func {task.get('___sdk_func_name___')} does not exist in func_dict",
                                logger=logger,
                                mode="error", ignore_flag=False)

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _reference_func(content: str, tag: str, variable_store: Dict, func_dict: Dict, logger: Log = None) -> str:
    """This function applies the logic based on the given tag.  When reference tag is given, it will look up the value
    in the variable store.  When function reference tag is given, it will try to match the tag with function stored in func_dict

    Args:
        content: contains a list of function to be validated against
        tag: whether reference or func_reference
        variable_store: stores a dictionary of variables which its value can be look upon
        func_dict: stores a dictionary of functions which its value can be look upon
        logger: logger

    Returns:
        referenced value

    """

    def _str_proc(prev: str, current: Any) -> str:
        if not current:
            return prev + ""
        if isinstance(current, (str, float, int)):
            return prev + str(current)
        else:
            return current

    try:
        _result = ""
        # if reference tag is given
        if tag == "reference":
            if "..." in content:
                _var_lookup = content.split("...")
                _var_lookup_key = _var_lookup[0]
                _var_lookup_col = _var_lookup[1]
                if _key_exist := variable_store.get(_var_lookup_key, None):
                    if _col_exist := _key_exist.get(_var_lookup_col, None):
                        return _str_proc(_result, _key_exist.get(_var_lookup_col, None))
                    else:
                        common.error_logger(currentframe().f_code.co_name,
                                            f"key: {_key_exist}, col: {_col_exist} does not exist in variable store",
                                            logger=logger,
                                            mode="error", ignore_flag=False)
                else:
                    common.error_logger(currentframe().f_code.co_name,
                                        f"key: {_key_exist} does not exist in variable store",
                                        logger=logger,
                                        mode="error", ignore_flag=False)

        # if func tag is given
        elif tag == "func_reference":
            for _ind, _func in func_dict.items():
                if content.startswith(_ind):
                    if len(content) == len(_ind):
                        return _str_proc(_result, _func())
                    else:
                        return _str_proc(_result, _func(content[len(_ind):]))

        return _result
    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _resolve_reference(content: str, variable_store: Dict, func_dict: Dict, logger: Log = None):
    """parse the string which may include multiple tags, if reference tag is detected, invoke _reference_func

    Args:
        content: contains a list of function to be validated against
        variable_store: stores a dictionary of variables which its value can be look upon
        func_dict: stores a dictionary of functions which its value can be look upon
        logger: logger

    Returns:
        referenced value otherwise original string

    """
    try:
        def _dist(string, tags):
            _min = [float("inf"), ""]
            for _t in tags:
                n = string.find(_t)
                if n != -1 and n < _min[0]:
                    _min = [n, _t]
            return _min

        if not isinstance(content, str): return content
        _content = content

        _stack = deque([])
        _tags = {"<func_end>": "<func_start>",
                 "<end>": "<start>"}

        while len(_content) > 0:

            _next, _tag = _dist(_content, list(_tags.keys()) + list(_tags.values()))

            _start_flag = False
            if _next == float("inf"):
                _stack.append(_content.strip())
                break
            elif _tag in _tags.values():
                if _content[:_next]:
                    _stack.append(_content[:_next].strip())
                _stack.append(_tag)
                _content = _content[_next + len(_tag):]

            else:
                if _tags.get(_tag) not in _stack:
                    common.error_logger(currentframe().f_code.co_name,
                                        f"Error: there is no matching {_tags.get(_tag)} for {_tag}",
                                        logger=logger,
                                        mode="error", ignore_flag=False)

                _info = _content[:_next].strip()
                while _stack and _stack[-1] != _tags.get(_tag):
                    x = _stack.pop()
                    if x in _tags.values():
                        common.error_logger(currentframe().f_code.co_name,
                                            f"Error: expecting tag {_tags.get(_tag)} and got {x} instead",
                                            logger=logger,
                                            mode="error", ignore_flag=False)
                    _info = x + _info
                _stack.pop()
                if _tag == "<func_end>":
                    _info = _reference_func(_info.strip(), "func_reference", variable_store, func_dict)
                elif _tag == "<end>":
                    _info = _reference_func(_info.strip(), "reference", variable_store, func_dict)
                if isinstance(_info, str):
                    _stack.append(_info.strip())
                else:
                    return _info
                _content = _content[_next + len(_tag):]
        return ''.join(_stack)

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _traverse(text: Any, variable_store: Dict, func_dict: Dict, logger: Log = None) -> Any:
    """recursively traverse thru data structure and when encounter str object, invoke _resolve_reference method to resolve any reference may have included

    Args:
        text: an object
        variable_store: stores a dictionary of variables which its value can be look upon
        func_dict: stores a dictionary of functions which its value can be look upon
        logger: logger

    Returns:
        return metadata objects

    """
    try:
        if text:
            if isinstance(text, str):
                return _resolve_reference(text, variable_store, func_dict)
            elif isinstance(text, Dict):
                for _index, _value in text.items():
                    text[_index] = _traverse(_value, variable_store, func_dict)
            elif isinstance(text, (List, Tuple)):
                _temp = []
                for _item in text:
                    _temp.append(_traverse(_item, variable_store, func_dict))
                return _temp
            else:
                return text
        return text
    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _process(func_dict: Dict,
             task: Dict,
             variable_store: Dict,
             save_variable: Optional[List],
             field_addition: Optional[List],
             logger: Log = None) -> Dict:
    """prepare variables for invoke sdk call and gather results and structure them for future usage

    Args:
        func_dict: a dictionary of functions in most cases, sdk functions
        variable_store: stores a list of variables which its value can be look upon
        save_variable: a list of variables we need to save for future use from result set of sdk call
        field_addition: a list of variables we need to save for future from input parameters
        logger: logger

    Returns:
        return saved variables

    """
    _variable_store = variable_store

    try:
        _sdk_input_param = {}
        for _param_ind, _param_val in task.get("___sdk_func_param___", {}).items():
            _sdk_input_param = {**_sdk_input_param, **{_param_ind: _traverse(_param_val,
                                                                             variable_store,
                                                                             {**_CORE_FUNC, **func_dict},
                                                                             logger)}}

        common.error_logger(currentframe().f_code.co_name,
                            f"func_dict: {func_dict},  task: {task}, variable_store: {variable_store}, "
                            f"save_variable: {save_variable}, field_addition: {field_addition}",
                            logger=logger,
                            mode="debug")

        _result = _sdk_execution(func_dict.get(task.get("___sdk_func_name___")), logger, **_sdk_input_param)

        # process input parameters which should be saved future use
        for _field in field_addition:
            if _field not in _sdk_input_param:
                common.error_logger(currentframe().f_code.co_name, f"field {_field} in the add_field list does not exist in input_parameter",
                                    logger=logger, ignore_flag=False)
            _variable_store[task["task_unique_identifier"]] = \
                {**_variable_store.get(task["task_unique_identifier"], {}), **{_field: _sdk_input_param[_field]}}

        # process fields which returning from sdk and should be saved future use
        for each_variable in save_variable:
            if isinstance(each_variable, Dict):
                _scan_key = list(each_variable.keys())[0]
                _result_key = list(each_variable.values())[0]
            elif isinstance(each_variable, str):
                _scan_key = each_variable
                _result_key = each_variable
            else:
                common.error_logger(currentframe().f_code.co_name,
                                    f"save_field {each_variable} should be either in dictionary or str format",
                                    logger=logger,
                                    mode="error",
                                    ignore_flag=False)
            _variable_val_list = util.get_value_by_key(_result, _scan_key)
            if len(_variable_val_list) == 0:
                _variable_val = ""
            elif len(_variable_val_list) == 1:
                _variable_val = _variable_val_list[0]
            else:
                _variable_val = _variable_val_list

            _variable_store[task["task_unique_identifier"]] = {**_variable_store.get(task["task_unique_identifier"], {}), **{_result_key: _variable_val}}
            common.error_logger(currentframe().f_code.co_name,
                                f"all accumulated variables after finishing process this task: {_variable_store}",
                                logger=logger,
                                mode="debug")

        return _variable_store

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def process(func_dict: Dict, task: Dict, task_order: Optional[List], variable_store: Dict, logger: Log = None) -> Tuple[Dict, List]:
    """A wrapper function for _process.  chef each element into their appropriate place and then pass them to _process function to ensure ordering

    Args:
        func_dict: a dictionary of functions in most cases, sdk functions
        task: contains information about a resource
        task_order: the execution order of a task
        variable_store: stores a list of variables which its value can be look upon
        logger: logger

    Returns:
        return saved variables

    """

    _destroy_stmt = []
    try:
        for _task in task_order:
            _task_detail = task.get(_task, {})
            if not _task_detail:
                if _task in variable_store:
                    continue
                else:
                    common.error_logger(currentframe().f_code.co_name,
                                        f"task details for {_task} is not found",
                                        logger=logger,
                                        mode="error",
                                        ignore_flag=False)

            if not _process_validate(func_dict, _task_detail, ["___resource___", "___sdk_func_name___", "___sdk_func_param___"], logger):
                raise

            # get post process into a separate data structure
            _post_process = []
            _task_unique_identifier = _task_detail.get("task_unique_identifier")

            if "___post_process___" in _task_detail:
                _post_process = _task_detail.get("___post_process___", [])
                del _task_detail["___post_process___"]

            # get removal process into a separate data structure
            _destroy_resource = []
            if "___destroy_resource___" in _task_detail:
                _destroy_resource = _task_detail.get("___destroy_resource___", [])
                del _task_detail["___destroy_resource___"]

            # invoke sdk
            variable_store = _process(func_dict,
                                      _task_detail,
                                      variable_store,
                                      _task_detail.get("___save_fields___", []),
                                      _task_detail.get("___add_fields___", []),
                                      logger)
            # invoke post task
            for _post_task in _post_process:
                _post_task["task_unique_identifier"] = _task_unique_identifier
                variable_store = _process(func_dict,
                                          _post_task,
                                          variable_store,
                                          _post_task.get("___save_fields___", []),
                                          _post_task.get("___add_fields___", []),
                                          logger)

            # invoke removal logic to resources removal steps for future use
            _sdk_destroy_input_param = {}
            for _destroy_task in _destroy_resource:
                _destroy_task["task_unique_identifier"] = _task_unique_identifier
                for _param_ind, _param_val in _destroy_task.get("___sdk_func_param___", {}).items():
                    _sdk_destroy_input_param = {**_sdk_destroy_input_param,
                                                **{_param_ind: _traverse(_param_val, variable_store, {**_CORE_FUNC, **func_dict})}}
                _destroy_task["___resource___"] = _task_unique_identifier
                _destroy_task["___sdk_func_param___"] = _sdk_destroy_input_param
                _destroy_stmt.append(_destroy_task)

            _unqiue_task_id = _task_detail.get('___resource___')
            if _unqiue_task_id != "GENERAL":
                print(f"task {_unqiue_task_id} is completed")

        return variable_store, _destroy_stmt

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _get_task_unique_identifier(task: Dict, logger: Log = None) -> str:
    """A helper function to find the surrogate key for each resource in task

    Args:
        task: contains information about a resource
        logger: logger

    Returns:
        return surrogate key

    """
    try:
        for _ind, _val in task.items():
            if _ind.startswith("___") and _ind.endswith("___"):
                _var_name = util.partition_find(_ind, "___", "___", )
                if _var_name == "resource":
                    return _val

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def _get_task_detail(task_unique_identifier: str, task: Dict, task_dependency: Dict, logger: Log = None) -> Tuple[Dict, Dict]:
    """A helper function to detect reference exists and build a dependency graph

    Args:
        task_unique_identifier: task surrogate key
        task: contains information about a resource
        task_dependency: holds dependency info
        logger: logger

    Returns:
        return task details and task dependency

    """
    _sdk_content = {}
    _task_dependency = task_dependency

    try:

        for _ind, _val in task.items():
            if _ind.startswith("___") and _ind.endswith("___"):
                _var_name = util.partition_find(_ind, "___", "___", )
                if _var_name == "sdk_func_param":
                    for _param_ind, _param_val in _val.items():
                        _var_name = util.partition_find(_param_ind, "___", "___", )
                        if isinstance(_param_val, str) and util.get_variable(_param_val):
                            _items = util.get_variable(_param_val)
                            for _item in _items:
                                _var_lookup = _item.strip().split("...")
                                _var_lookup_key = _var_lookup[0]
                                _task_dependency[task_unique_identifier].add(_var_lookup[0])

                        _sdk_content[_ind] = {**_sdk_content.get(_ind, {}), **{_param_ind: _param_val}}
                else:
                    _sdk_content[_ind] = _val
        return {**_sdk_content, **{"task_unique_identifier": task_unique_identifier}}, _task_dependency

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def preprocessing(func_dict: Dict, tasks: List, variable_store: Dict, logger: Log = None) -> Tuple[Dict, List]:
    """Use topological sort algorithm to build a dependency list for tasks within input file

    Args:
        func_dict: a dictionary of functions in most cases, sdk functions
        tasks: stores a list of tasks
        variable_store: stores a list of variables which its value can be look upon
        logger: logger

    Returns:
        return values from process

    """
    _variable_store = variable_store
    _task_dependency = defaultdict(set)
    _task_detail = defaultdict(dict)
    _task_detail["GENERAL"] = {"___resource___": "GENERAL",
                               "___sdk_func_name___": "create_common_variable",
                               "___sdk_func_param___": {"dummy": "to pass validation"},
                               "___save_fields___": ["account_number", "account_region", "lambda_function_name", "domain_name"],
                               "task_unique_identifier": "GENERAL"
                               }
    func_dict["create_common_variable"] = create_common_variable
    _flag = defaultdict(int)
    _result = []

    def _dfs(node):
        if _flag[node] == 0:
            _flag[node] = 1

            for _next in _task_id.get(node, []):
                if _flag[_next] == 0:
                    _dfs(_next)

                if _flag[_next] == 1:
                    return False

            _result.append(node)
            _flag[node] = 2
            return True

    try:

        for _task in tasks:
            _sdk_content = {}
            _task_unique_identifier = _get_task_unique_identifier(_task, logger)
            _task_dependency[_task_unique_identifier].add("GENERAL")
            _task_detail[_task_unique_identifier], _task_id = _get_task_detail(_task_unique_identifier,
                                                                               _task,
                                                                               _task_dependency,
                                                                               logger)

        for _ind in _task_dependency.keys():
            if _flag[_ind] == 0:
                if not _dfs(_ind):
                    common.error_logger(currentframe().f_code.co_name,
                                        f"there is a circular dependency",
                                        logger=logger,
                                        mode="debug", ignore_flag=False)

        common.error_logger(currentframe().f_code.co_name,
                            f"dependency: {_result},  detail taskt: {_task_detail}",
                            logger=logger,
                            mode="debug")

        return process(func_dict, _task_detail, _result, variable_store, logger)

    except Exception as err:
        common.error_logger(currentframe().f_code.co_name,
                            err,
                            logger=logger,
                            mode="error", ignore_flag=False)


def create_common_variable(*args, **kwargs) -> Dict:
    """Register commonly used variable

    Args:

    Returns:
        return variable dictionary

    """

    _result = {"GENERAL":   {"account_number": "765928778661",
                             "account_region": "us-east-1",
                             "lambda_function_name": "demo",
                             "domain_name": "albworks.com"
                             }
               }

    return _result
