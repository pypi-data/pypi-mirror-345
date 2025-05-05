# systemtools.py
# Import packages
import psutil

# Get memory usage in % or GB (installed) or GB used memory or GB free memory as float
def memory_usage(type: str = "percent") -> float:
    """
    Get memory usage in % or GB (installed) or GB used memory or GB free memory as float.

    Args:
        type (str, optional): "percent" (default), "gb", "gb_used", "gb_free". Defaults to "percent".

    Returns:
        float: Memory usage.
    """
    if type == "percent":
        return psutil.virtual_memory().percent
    elif type == "gb":
        return psutil.virtual_memory().total / (1024 * 1024 * 1024)
    elif type == "gb_used":
        return psutil.virtual_memory().used / (1024 * 1024 * 1024)
    elif type == "gb_free":
        return psutil.virtual_memory().free / (1024 * 1024 * 1024)
    return False