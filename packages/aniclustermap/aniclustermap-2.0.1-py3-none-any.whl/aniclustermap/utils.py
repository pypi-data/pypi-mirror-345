from __future__ import annotations

import logging
import os
import platform
import signal
import sys
import time
from functools import partial, wraps
from pathlib import Path
from typing import Callable


def add_bin_path():
    """Add binary tool path"""
    os_name = platform.system()  # 'Windows' or 'Darwin' or 'Linux'
    bin_path = Path(__file__).parent / "bin" / os_name
    sep = ";" if os_name == "Windows" else ":"
    env_path = f"{os.environ['PATH']}{sep}{bin_path}"
    os.environ["PATH"] = env_path


def logging_timeit(
    func: Callable | None = None,
    /,
    *,
    show_func_name: bool = False,
    debug: bool = False,
):
    """Elapsed time logging decorator

    e.g. `Done (elapsed time: 82.3[s]) [module.function]`

    Parameters
    ----------
    func : Callable | None, optional
        Target function
    show_func_name : bool, optional
        If True, show elapsed time message with `module.function` definition
    debug : bool, optional
        If True, use `logger.debug` (By default `logger.info`)
    """
    if func is None:
        return partial(logging_timeit, show_func_name=show_func_name, debug=debug)

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger = logging.getLogger(__name__)
        msg = f"Done (elapsed time: {elapsed_time:.2f}[s])"
        if show_func_name:
            msg = f"{msg} [{func.__module__}.{func.__name__}]"
        logger_func = logger.debug if debug else logger.info
        logger_func(msg)
        return result

    return wrapper


def exit_handler(func):
    """Exit handling decorator on exception

    The main purpose is logging on keyboard interrupt exception
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.exception("Keyboard Interrupt")
            sys.exit(signal.SIGINT)
        except Exception as e:
            logger.exception(e)
            sys.exit(1)

    return wrapper
