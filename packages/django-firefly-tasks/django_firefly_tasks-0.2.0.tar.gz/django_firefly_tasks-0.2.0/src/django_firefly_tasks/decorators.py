import functools

from ._private.consts import DEFAULT_QUEUE, MAX_RETRIES, RETRY_DELAY
from ._private.utils import get_func_path, is_async, serialize_object
from .exceptions import AsyncFuncNotSupportedException, SyncFuncNotSupportedException
from .models import Status, TaskModel


def task(queue: str = DEFAULT_QUEUE, max_retries: int = MAX_RETRIES, retry_delay: int = RETRY_DELAY):
    """
    Creates task to consume.

    :param str queue: the queue in which the task will be placed
    :param int max_retries: max retries on fail
    :param int retry_delay: delay in seconds between restarts
    """

    def decorator(func):
        def schedule(*args, **kwargs):
            if is_async(func):
                raise AsyncFuncNotSupportedException

            func_name = get_func_path(func)
            serialized_params = serialize_object({"args": args, "kwargs": kwargs})

            return TaskModel.objects.create(
                func_name=func_name,
                raw_params=serialized_params,
                queue=queue,
                status=Status.CREATED,
                retry_delay=retry_delay,
                max_retries=max_retries,
            )

        func.schedule = schedule

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def atask(queue: str = DEFAULT_QUEUE, max_retries: int = MAX_RETRIES, retry_delay: int = RETRY_DELAY):
    """
    Creates async task to consume.

    :param str queue: the queue in which the task will be placed
    :param int max_retries: max retries on fail
    :param int retry_delay: delay in seconds between restarts
    """

    def decorator(func):
        def schedule(*args, **kwargs):
            if not is_async(func):
                raise SyncFuncNotSupportedException

            func_name = get_func_path(func)
            serialized_params = serialize_object({"args": args, "kwargs": kwargs})

            return TaskModel.objects.create(
                func_name=func_name,
                raw_params=serialized_params,
                queue=queue,
                status=Status.CREATED,
                retry_delay=retry_delay,
                max_retries=max_retries,
            )

        func.schedule = schedule

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
