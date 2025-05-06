import os
from functools import wraps
from datetime import datetime
from printf import Print, value_to_str

__log_level__ = ["data", "info", "msg", "warn", "error"]
__log_print__ = {
    "data": Print(level="data"),
    "info": Print(level="normal"),
    "msg": Print(level="system"),
    "warn": Print(level="warning"),
    "error": Print(level="error"),
}


class Log:
    str_limit = 0
    agree_level = {_l: True for _l in __log_level__}
    base_path = os.path.dirname(__file__)

    @classmethod
    def set_file_path(cls, file_path):
        cls.base_path = file_path

    @classmethod
    def open_log_level(cls, log_level):
        if log_level in __log_level__:
            cls.agree_level[log_level] = True

    @classmethod
    def close_log_level(cls, log_level):
        if log_level in cls.agree_level:
            cls.agree_level[log_level] = False

    @classmethod
    def write(cls, message=""):
        with open(cls.base_path / f"log-{datetime.now().date()}", "a+") as log_file:
            log_file.write(message)

    @classmethod
    def message(cls, _level, *_msg, sep=" ", end="\n", shell=True):
        _m = value_to_str(
            f"[{_level}]{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}>>", *_msg, sep=sep)
        if cls.str_limit and len(_m) > cls.str_limit:
            _m = f"{_m[:cls.str_limit]} ...{end}"
        else:
            _m = f"{_m}{end}"
        if cls.agree_level.get(_level, False):
            __log_print__[_level].printf(_m, output=shell)
            cls.write(_m)

    @classmethod
    def data(cls, *_msg, sep=" ", end="\n", shell=True):
        cls.message("data", *_msg, sep=sep, end=end, shell=shell)

    @classmethod
    def info(cls, *_msg, sep=" ", end="\n", shell=True):
        cls.message("info", *_msg, sep=sep, end=end, shell=shell)

    @classmethod
    def msg(cls, func, *_msg, sep=" ", end="\n", shell=True):
        if callable(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.message("msg", f"开始执行{_msg or func.__name__}", sep=sep, end=end, shell=shell)
                __r = func(*args, **kwargs)
                cls.message("msg", f"{_msg or func.__name__}执行结束", sep=sep, end=end, shell=shell)
                return __r
            return wrapper
        else:
            cls.message("msg", func, *_msg, sep=sep, end=end, shell=shell)

    @classmethod
    def warn(cls, *_msg, sep=" ", end="\n", shell=True):
        cls.message("warn", *_msg, sep=sep, end=end, shell=shell)

    @classmethod
    def error(cls, func, *_msg, sep=" ", end="\n", shell=True):
        if callable(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    cls.message("error", e, sep=sep, end=end, shell=shell)
            return wrapper
        cls.message("error", func, *_msg, sep=sep, end=end, shell=shell)
