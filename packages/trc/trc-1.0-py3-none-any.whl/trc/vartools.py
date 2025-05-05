# Import modules
import random, itertools, inspect, trc

# Remove characters from a string
@trc.cache
def clean(string: str = "Hello World!", chars: str = "") -> str:
    if not isinstance(string, str):
        raise TypeError("string must be a string")
    translation_table = str.maketrans("", "", chars)
    return string.translate(translation_table)

# Merge multiple lists or dictionaries
def merge(*args: list | dict, duplicate: bool = False, deep: bool = False) -> list | dict:
    if not args:
        raise ValueError("No arguments provided")
    first_type = type(args[0])
    if not all(isinstance(arg, first_type) for arg in args):
        return False
    if first_type is list:
        if duplicate:
            return list(itertools.chain(*args))
        return list(dict.fromkeys(itertools.chain(*args)))
    elif first_type is dict:
        result = {}
        for d in args:
            if deep:
                for key, value in d.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = merge(result[key], value, deep=True)
                    else:
                        result[key] = value
            else:
                result.update({k: v for k, v in d.items() if k not in result})
        return result
    raise TypeError(f"Unsupported type/s: {', '.join(type(arg).__name__ for arg in args)}")

# Remove duplicates
def unique(obj: list | str, preserve_order: bool = True) -> list | str:
    if preserve_order:
        return list(dict.fromkeys(obj))
    else:
        return list(set(obj))

# Flatten a nested list
def flatten(lst: list) -> list:
    if lst is not list:
        raise TypeError("lst must be a list")
    flat_list = []
    for element in lst:
        if isinstance(element, list):
            flat_list.extend(flatten(element))
        else:
            flat_list.append(element)
    return flat_list

# Generate a random string
def random_string(length: int, charset: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') -> str:
    return ''.join(random.choice(charset) for _ in range(length))

# Check if any item in a is in b
def any_in(a: list | str, b: list | str) -> bool:
    if not isinstance(a, (list, str)) or not isinstance(b, (list, str)):
        raise TypeError("a and b must be lists or strings")
    return any(item in b for item in a)

# Check if all items in a are in b
def all_in(a: list | str, b: list | str) -> bool:
    if not isinstance(a, (list, str)) or not isinstance(b, (list, str)):
        raise TypeError("a and b must be lists or strings")
    return all(item in b for item in a)

# Format duration
@trc.cache
def format_duration(seconds: int | float | str = 0) -> str:
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Reverse each objekt in a list or string
@trc.cache
def reverse(obj: list | str) -> list | str:
    if isinstance(obj, (list, tuple)):
        return type(obj)(item[::-1] if isinstance(item, (str, list, tuple)) else item for item in obj)
    elif isinstance(obj, str):
        return obj[::-1]
    return obj

# Get or set a variable
def var(name: str, value: any = None) -> any:
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals
    caller_globals = caller_frame.f_globals

    if value is not None:
        if name in caller_locals:
            caller_locals[name] = value
        else:
            caller_globals[name] = value

    if name in caller_locals:
        return caller_locals[name]
    elif name in caller_globals:
        return caller_globals[name]
    else:
        raise NameError(f"Variable '{name}' not found in local or global scope.")

# Backup given variales an return a backupvariable
def backup(*args):
    backup_dict = {}
    for arg in args:
        backup_dict[arg] = var(arg)
    return backup_dict

# Restore given variales
def restore(backup_dict):
    for key, value in backup_dict.items():
        var(key, value)