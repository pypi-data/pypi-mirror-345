import logging
from contextlib import contextmanager
from functools import wraps
from typing import Optional


@contextmanager
def log_level_manager(logger, level):
    """
    Context manager to temporarily set the log level of a logger.

    Args:
        logger (logging.Logger): The logger for which to set the level.
        level (int): The log level to set.

    Yields:
        None
    """
    original_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(original_level)


def set_log_level(logger, level):
    """
    Decorator to temporarily set the log level of a logger during the execution of a synchronous
    function.

    Args:
        logger (logging.Logger): The logger for which to set the level.
        level (int): The log level to set.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with log_level_manager(logger, level):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def set_log_level_async(logger, level):
    """
    Decorator to temporarily set the log level of a logger during the execution of an asynchronous
    function.

    Args:
        logger (logging.Logger): The logger for which to set the level.
        level (int): The log level to set.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with log_level_manager(logger, level):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def setup_logger(
    name: str, logger: Optional[logging.Logger] = None, level=logging.INFO
):
    """
    Sets up a logger with the specified name and level. If a logger is provided, it is used;
    otherwise, a new logger is created. The logger is configured with a stream handler and a
    simple formatter if the root logger has no handlers.

    If the root logger contains handlers, the logger's level is set to the root logger's effective
    level. This is the first level set on the logger or any of its ancestors (recursively). If no
    level is set, the root logger's level, which defaults to WARNING, is used.

    Args:
        name (str): The name to use when creating a new logger.
        logger (Optional[logging.Logger]): The logger to set up. If None, a new logger is created.
        level (int): The log level to set for the logger. Defaults to logging.INFO.

    Returns:
        logging.Logger: The logger that was set up.
    """
    if logger is None:
        # Create a StreamHandler instance for the logger. This handler sends the log messages to a
        # stream (like standard output, standard error or any file-like object). The StreamHandler
        # is then set with a specific formatter, which defines the layout of the log messages. This
        # approach is preferred over using logging.basicConfig, as it allows setting the log level
        # and format specifically for this logger, without affecting the root logger. However, it's
        # important to note that just setting the level on the logger after calling getLogger() is
        # not enough. A handler must also be configured for the logger. Without a handler, logging
        # uses an internal "handler of last resort" which has a level of WARNING and outputs just
        # the message with no other formatting.
        logger = logging.getLogger(name)

        if not logging.root.handlers:
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            log_stream_handler = logging.StreamHandler()
            log_stream_handler.setFormatter(formatter)
            logger.addHandler(log_stream_handler)
        else:
            level = logging.root.getEffectiveLevel()
        logger.setLevel(level)
    return logger
