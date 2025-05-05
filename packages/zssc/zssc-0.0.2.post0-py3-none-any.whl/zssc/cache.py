import json
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar, Union

T = TypeVar("T")


def cache(
    func: Union[Callable[..., T], None] = None,
    *,
    cache_path: str,
) -> Callable[..., T]:
    """Wrap a function to cache its result.

    Args:
        cache_path (str): The path to the cache file.
        func (Union[Callable[..., T], None], optional): The function to wrap. Defaults to None.

    Returns:
        Callable[..., T]: The wrapped function.

    Usage:
        ```python
        # 1. As function
        cached_f = cache(func, cache_path="tmp/res.json")
        out = cached_f(*args, **kwargs)

        # 2. As decorator
        @cache(cache_path="tmp/res.json")
        def func(...): ...
        ```
    """
    assert cache_path.endswith(".json"), "`cache_path` must end with .json"

    if func is None:  # * decorator syntax
        return lambda f: cache(f, cache_path=cache_path)

    @wraps(func)
    def wrapper(*args, **kwargs):
        path = Path(cache_path)
        if path.exists():
            with path.open("r") as f:
                return json.load(f)
        else:
            result = func(*args, **kwargs)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return result

    return wrapper
