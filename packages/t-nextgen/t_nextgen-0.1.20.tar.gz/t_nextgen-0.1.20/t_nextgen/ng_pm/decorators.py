"""This module contains decorators for the NextGen application."""
import time
from functools import wraps

from t_nextgen.utils.logger import logger


def click_ok_if_only_option() -> callable:
    """This function is a decorator that wraps the click_ok_if_only_option function.

    Returns:
        callable: The wrapped function.
    """

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(self: object, *args, **kwargs) -> callable:
            if hasattr(self.desktop_app, "click_ok_if_only_option"):
                start_time = time.time()
                self.desktop_app.click_ok_if_only_option(max_calls=1, modal_exists_timeout=1, sleep=1)
                logger.debug(f"Time taken: {time.time() - start_time}")
            else:
                logger.warning("The 'click_ok_if_only_option' method is not defined.")
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
