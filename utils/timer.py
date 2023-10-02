import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def timer_decorator(func):
    """
    Returns the time a function took to execute
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(
            f"{func.__name__} took {elapsed_time:.4f} seconds to run."
        )
        return result

    return wrapper
