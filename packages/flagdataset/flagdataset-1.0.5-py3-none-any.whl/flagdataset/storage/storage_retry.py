import time

from loguru import logger


class RetryException(Exception):
    pass


def retry_decorator(max_retries=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            error = None

            while retries < max_retries:
                try:
                    rs = func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.warning(
                        f"{func.__name__} Attempt {retries} failed with error: {e}"
                    )
                    print(f"{func.__name__} Attempt {retries} failed with error: {e}")

                    error = e
                    time.sleep(delay)
                else:
                    return rs

            logger.error(
                f"{func.__name__} failed after {max_retries} retries, "
                f"with error: {error}"
            )
            raise RetryException(
                f"{func.__name__} failed after {max_retries} retries, "
                f"with error: {error}"
            )

        return wrapper

    return decorator
