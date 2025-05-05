# vartools.py
# Import modules
import random, itertools, inspect, trc, re

# Remove characters from a string
@trc.cache
def clean(string: str = "Hello World!", mode: str = "clean", chars: str = "") -> str:
    """
    Remove characters from a string.

    Args:
        string (str, optional): The string to clean. Defaults to "Hello World!".
        mode (str, optional): The mode of cleaning. Defaults to "clean".
        chars (str, optional): The characters to remove. Defaults to "".

    Returns:
        str: The cleaned string.

    Raises:
        TypeError: If string is not a string.
        ValueError: If mode is not 'clean' or 'word'.
    """
    if mode == "clean":
        if not isinstance(string, str):
            raise TypeError("string must be a string")
        translation_table = str.maketrans("", "", chars)
        return string.translate(translation_table)
    elif mode == "word":
        pattern = r'^[^a-zA-ZßäöüÄÖÜ]+|[^a-zA-ZßäöüÄÖÜ]+$'
        return re.sub(pattern, '', string)
    else:
        raise ValueError("mode must be 'clean' or 'word'")

# Merge multiple lists or dictionaries
def merge(*args: list | dict, duplicate: bool = False, deep: bool = False) -> list | dict:
    """
    Merge multiple lists or dictionaries.

    This function merges multiple lists or dictionaries of the same type into
    a single list or dictionary. If the input arguments are lists, they will
    be concatenated, and duplicates will be removed unless the `duplicate`
    parameter is set to True. If the input arguments are dictionaries, their
    key-value pairs will be combined. If the `deep` parameter is set to True,
    nested dictionaries will be merged recursively.

    :param args: A variable number of arguments, each being a list or dictionary
                 of the same type.
    :param duplicate: If True, allows duplicate elements in the result list.
                      Applicable only when merging lists. Defaults to False.
    :param deep: If True, performs a deep merge of nested dictionaries.
                 Applicable only when merging dictionaries. Defaults to False.
    :return: A merged list or dictionary.
    :raises ValueError: If no arguments are provided.
    :raises TypeError: If the arguments are not all of the same type or if the 
                       type is unsupported.
    """

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
    """
    Remove duplicates from a list or string.

    If preserve_order is True, the order of elements is preserved.
    If preserve_order is False, the order of elements is not preserved.

    :param obj: The list or string to be processed.
    :param preserve_order: Preserve the order of elements.
    :return: A list or string without duplicates.
    :raises TypeError: If obj is not a list or string.
    """
    if preserve_order:
        return list(dict.fromkeys(obj))
    else:
        return list(set(obj))

# Flatten a nested list
def flatten(lst: list) -> list:
    """
    Flatten a nested list.

    :param lst: The list to be flattened.
    :return: A flat list containing all elements of the original list.
    :raises TypeError: If lst is not a list.
    """
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
    """
    Generate a random string of a given length from a given charset.

    :param length: The length of the string to be generated.
    :param charset: The characters to be used in the generated string.
    :return: A random string of length 'length' consisting of characters from 'charset'.
    """
    return ''.join(random.choice(charset) for _ in range(length))

# Check if any item in a is in b
def any_in(a: list | str, b: list | str) -> bool:
    """
    Check if any item in a is in b.

    :param a: The list or string to be checked.
    :param b: The list or string to be checked against.
    :return: True if any item in a is in b, False otherwise.
    :raises TypeError: If a or b is not a list or string.
    """
    
    if not isinstance(a, (list, str)) or not isinstance(b, (list, str)):
        raise TypeError("a and b must be lists or strings")
    return any(item in b for item in a)

# Check if all items in a are in b
def all_in(a: list | str, b: list | str) -> bool:
    """
    Check if all items in a are in b.

    :param a: The list or string to be checked.
    :param b: The list or string to check against.
    :return: True if all items in a are in b, False otherwise.
    """
    
    if not isinstance(a, (list, str)) or not isinstance(b, (list, str)):
        raise TypeError("a and b must be lists or strings")
    return all(item in b for item in a)

# Format duration
@trc.cache
def format_duration(seconds: int | float | str = 0) -> str:
    """
    Format a duration given in seconds into a human-readable string.

    This function takes a duration in seconds, which can be an integer,
    float, or string representation of a number, and converts it to a
    formatted string in the format "HH:MM:SS".

    :param seconds: The duration in seconds to format. Can be of type int, float, or str.
    :return: A string representing the formatted duration in "HH:MM:SS".
    :raises ValueError: If the input seconds cannot be converted to an integer.
    """

    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Reverse each objekt in a list or string
@trc.cache
def reverse(obj: list | str) -> list | str:
    """
    Reverse each object in a list or string.

    This function takes a list, tuple, or string and reverses each element within it.
    If the input is a list or tuple, each element in the list or tuple that is a string,
    list, or tuple is reversed. If the input is a string, the entire string is reversed.

    :return: The reversed list, tuple, or string.
    """


    if isinstance(obj, (list, tuple)):
        return type(obj)(item[::-1] if isinstance(item, (str, list, tuple)) else item for item in obj)
    elif isinstance(obj, str):
        return obj[::-1]
    return obj

# Get or set a variable
def var(name: str, value: any = None) -> any:
    """
    Get or set a variable in the caller's scope.

    This function allows getting or setting a variable by name in the local
    or global scope of the caller. If a value is provided, the variable is set
    to that value; otherwise, the current value of the variable is returned.

    :param name: The name of the variable to get or set.
    :param value: The value to set the variable to, or None to just get the value.
    :return: The current or new value of the variable.
    :raises NameError: If the variable is not found in the local or global scope.
    """

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
    """
    Backup given variables and return a backup variable.

    This function takes a variable number of arguments, which are the names of the
    variables to be backed up. The function then returns a dictionary where the
    keys are the variable names and the values are the current values of the
    variables.

    :param args: Variable number of argument variable names.
    :return: A dictionary containing the backed up variables.
    """
    backup_dict = {}
    for arg in args:
        backup_dict[arg] = var(arg)
    return backup_dict

# Restore given variales
def restore(backup_dict):
    """
    Restore given variables from a backup dictionary.

    This function takes a dictionary as input which contains
    the variables to be restored and their values.
    The function then sets the variables in the current scope
    to the given values.

    :param backup_dict: A dictionary containing the variables to be restored
                         and their values
    """
    for key, value in backup_dict.items():
        var(key, value)