from xeet.pr import pr_warn, pr_error, pr_header, pr_ok
import logging
import datetime
import inspect
import os
import sys


__logger = None


class VrdLogger(object):
    def __init__(self, log_file: str, log_level: int, logger_name=None) -> None:
        if logger_name is None:
            logger_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self._logger = logging.getLogger(logger_name)
        self._raw_formatter = logging.Formatter('%(message)s')
        self._default_formatter = logging.Formatter('%(asctime)s %(levelname).1s %(message)s',
                                                    "%H:%M:%S")
        self._file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self._file_handler.setFormatter(self._default_formatter)
        self._file_handler.setLevel(log_level)
        self._logger.addHandler(self._file_handler)
        self._logger.setLevel(log_level)
        self.raw_format = False

    def set_raw_format(self) -> None:
        self.raw_format = True
        self._file_handler.setFormatter(self._raw_formatter)

    def set_default_format(self) -> None:
        self.raw_format = False
        self._file_handler.setFormatter(self._default_formatter)

    def is_enabled_for(self, level: int) -> bool:
        return self._logger.isEnabledFor(level)

    @staticmethod
    def _frame_str(depth: int) -> str:
        try:
            # +2 to account for the frame of this function and the caller. Above that is the
            # caller's responsibility to pass the correct depth using the log_depth decorator
            frame = inspect.stack()[2 + depth]
        except IndexError:
            return "<unknown> "
        return f"[{os.path.basename(frame.filename)[:-3]}.{frame.function}:{frame.lineno}]"

    def log(self, verbosity: int, *args, depth: int) -> None:
        if not self._logger.isEnabledFor(verbosity):
            return
        if self.raw_format:
            self._logger.log(verbosity, args[0], *args[1:])
        else:
            msg = self._frame_str(depth).ljust(33, ".") + " ".join([str(x) for x in args])
            self._logger.log(verbosity, msg)


#  Not thread safe. As it change the format of the logger to raw format which
#  might affect other threads
def log_blank(count=1) -> None:
    if __logger is None:
        return
    __logger.set_raw_format()
    for _ in range(0, count):
        __logger.log(logging.INFO, "", depth=1)
    __logger.set_default_format()


def init_logging(title, log_file_path, verbose: bool) -> None:
    global __logger
    assert __logger is None

    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError as e:
            pr_warn(f"Error creating log directory - {e.strerror}")
            pr_warn("Logging is disabled")
            return
    if os.path.exists(log_file_path) and not os.path.isfile(log_file_path):
        pr_warn(f"Log file path '{log_file_path}' is not a file")
        pr_warn("Logging is disabled")
        return
    try:
        verbosity = logging.DEBUG if verbose else logging.INFO
        __logger = VrdLogger(log_file_path, verbosity, logger_name="xeet")
    except OSError as e:
        pr_warn(f"Error initializing log file - {e.strerror}")
        pr_warn("Logging is disabled")
        return
    log_blank(2)
    date_str = datetime.datetime.now().strftime("%I:%M:%S on %B %d, %Y")
    header_title = f"{title}, {date_str}"
    wrap_line = "=" * len(header_title)
    __logger.set_raw_format()
    log_info(f"{wrap_line}\n{header_title}\n{wrap_line}", pr=False)
    __logger.set_default_format()
    log_info(f"log file path is '{log_file_path}'", pr=False)
    return log_file_path


#  Return true if logging is enabled. If the optional level arguemt is used, will return true if
#  logging is enabled to this parricular log level
def logging_enabled(level: int = logging.NOTSET) -> bool:
    global __logger
    if not __logger:
        return False
    if level == logging.NOTSET:
        return True
    return __logger.is_enabled_for(level)


def log_depth(start_depth: int):
    def decorator(func):
        def _inner(*args, **kwargs):
            #  +1 to account for the decorator itself
            depth = kwargs.pop("depth", 0) + start_depth + 1
            func(*args, **kwargs, depth=depth)
        return _inner
    return decorator


def _create_log_func(log_level, default_pr_func):
    @log_depth(1)
    def log_func(*args, **kwargs):
        pr_func = kwargs.pop("pr", default_pr_func)
        pr_prefix = kwargs.pop("pr_prefix", None)
        pr_suffix = kwargs.pop("pr_suffix", None)
        pr_cond = kwargs.pop("pr_cond", True)
        if __logger:
            __logger.log(log_level, *args, **kwargs)
        if pr_func and pr_cond:
            kwargs.pop("depth", None)
            if pr_prefix is not None:
                pr_func(pr_prefix, end="")
            pr_func(*args, **kwargs)
            if pr_suffix is not None:
                pr_func(pr_suffix, end="")
    return log_func


log_verbose = _create_log_func(logging.DEBUG, None)
log_info = _create_log_func(logging.INFO, None)
log_warn = _create_log_func(logging.WARN, pr_warn)
log_error = _create_log_func(logging.ERROR, pr_error)
log_ok = _create_log_func(logging.INFO, pr_ok)
log_header = _create_log_func(logging.INFO, pr_header)


@log_depth(1)
def log_general(*args, severity=logging.INFO, **kwargs):
    if severity == logging.DEBUG:
        log_verbose(*args, **kwargs)
    elif severity == logging.INFO:
        log_info(*args, **kwargs)
    elif severity == logging.WARN:
        log_warn(*args, **kwargs)
    elif severity == logging.ERROR:
        log_error(*args, **kwargs)
