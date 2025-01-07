r"""
Setup logging for the library.
"""
import logging
import sys

__logger = logging.getLogger(f"""praline-config.{sys.modules[__name__].__package__.split(".")[0]}""")


def trace(*args, **kwargs): ...
debug = __logger.debug
info = __logger.info
warning = __logger.warning
error = __logger.error


def enable_trace():
    r"""
    By default, trace logging is no-op.
    :return:
    """
    global trace
    trace = __logger.debug


def override_logging_functions(
    trace_logger=None,
    debug_logger=None,
    info_logger=None,
    warning_logger=None,
    error_logger=None,
):
    r"""
    Allow a library consumer to inject different logging
    functions to deeply customize logging, or to inject a
    different library to use instead of the built-in logging module.
    """
    global trace, debug, info, warning, error
    trace = trace_logger or trace
    debug = debug_logger or debug
    info = info_logger or info
    warning = warning_logger or warning
    error = error_logger or error
