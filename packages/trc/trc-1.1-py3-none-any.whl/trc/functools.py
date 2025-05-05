# functools.py
# Import modules
import time

# Cache a function result
def cache(func):
    """
    Decorator to cache the result of a function.

    The cache is persistent between different calls to the function and is
    cleared when the program is restarted.

    This decorator is useful for functions that are expensive to compute and
    are called multiple times with the same arguments.

    It is a good practice to include a docstring in the cached function that
    explains that the function is cached and what arguments it takes.

    :param func: The function to be cached.
    :return: The cached version of the function.
    """
    cache_dict = {}

    def make_hashable(obj):
        """
        Make an object hashable.

        This function takes an arbitrary object and returns a hashable version
        of it. The returned object is guaranteed to be hashable, so it can be
        used as a key in a dictionary or as an element in a set.

        The returned object is an immutable version of the original object, so
        it can be safely used as a key or element in a dictionary or set.

        The returned object is also guaranteed to be the same for equal
        objects. For example, if two lists contain the same elements in the
        same order, the returned objects will be equal.

        :param obj: The object to be made hashable.
        :return: The hashable version of the object.
        """
        if isinstance(obj, (tuple, int, float, str, bool, type(None))):
            return obj
        if isinstance(obj, list):
            return tuple(make_hashable(item) for item in obj)
        if isinstance(obj, set):
            return frozenset(make_hashable(item) for item in obj)
        if isinstance(obj, dict):
            return tuple(sorted((make_hashable(k), make_hashable(v)) for k, v in obj.items()))
        return repr(obj)

    def wrapper(*args, **kwargs):
        """
        Wrapper function that caches the result of func.

        If the arguments of func (args and kwargs) are the same as a previous
        call, the cached result is returned instead of calling func again.

        :param args: The arguments to func.
        :param kwargs: The keyword arguments to func.
        :return: The result of func or the cached result.
        """
        key = (make_hashable(args),
               make_hashable(kwargs))
        if key in cache_dict:
            return cache_dict[key]
        result = func(*args, **kwargs)
        cache_dict[key] = result
        return result

    return wrapper

# Measure execution time
def timer(func):
    # Decorator
    """
    Decorator to measure the execution time of a function.

    The decorator returns a tuple (time, result) where time is the time in
    seconds needed to execute the function and result is the result of the
    function.

    :param func: The function for which the execution time should be measured.
    :return: The decorated version of the function.

    Example:
    >>> @timer
    ... def myfunc(x, y):
    ...     time.sleep(1)
    ...     return x + y
    >>> time, result = myfunc(3, 5)
    >>> print(f"Needed time: {time:.2f} seconds, result: {result}")
    Needed time: 1.00 seconds, result: 8
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        needed_time = end_time - start_time
        return needed_time, result
    return wrapper