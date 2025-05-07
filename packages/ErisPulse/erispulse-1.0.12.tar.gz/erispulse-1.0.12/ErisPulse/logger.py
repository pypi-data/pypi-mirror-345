import logging
import inspect
from .envManager import env

_logger = logging.getLogger("RyhBot")
_log_level = env.get("LOG_LEVEL", "DEBUG")
if _log_level is None:
    _log_level = logging.DEBUG
_logger.setLevel(_log_level)

if not _logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(console_handler)

def _get_caller():
    frame = inspect.currentframe().f_back.f_back
    module = inspect.getmodule(frame)
    module_name = module.__name__
    if module_name == "__main__":
        module_name = "Main"
    if module_name.endswith(".Core"):
        module_name = module_name[:-5]
    return module_name

def debug(msg, *args, **kwargs):
    caller_module = _get_caller()
    _logger.debug(f"[{caller_module}] {msg}", *args, **kwargs)


def info(msg, *args, **kwargs):
    caller_module = _get_caller()
    _logger.info(f"[{caller_module}] {msg}", *args, **kwargs)


def warning(msg, *args, **kwargs):
    caller_module = _get_caller()
    _logger.warning(f"[{caller_module}] {msg}", *args, **kwargs)


def error(msg, *args, **kwargs):
    caller_module = _get_caller()
    _logger.error(f"[{caller_module}] {msg}", *args, **kwargs)


def critical(msg, *args, **kwargs):
    caller_module = _get_caller()
    _logger.critical(f"[{caller_module}] {msg}", *args, **kwargs)