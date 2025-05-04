# import modules
import time, random, requests, psutil, math, json, itertools
from PIL import Image
from io import BytesIO

# Remove characters from a string
def clean(string: str = "Hello World!", chars: str = "") -> str:
    if not isinstance(string, str):
        return ""
    translation_table = str.maketrans("", "", chars)
    return string.translate(translation_table)

# Merge multiple lists or dictionaries
def merge(*args: list | dict, duplicate: bool = False, deep: bool = False) -> list | dict:
    if not args:
        return False
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
    return False

# Measure execution time
def timer(func):
    # Decorator
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        needed_time = end_time - start_time
        return needed_time, result
    return wrapper

# Remove duplicates
def unique(obj: list | str, preserve_order: bool = True) -> list | str:
    if preserve_order:
        return list(dict.fromkeys(obj))
    else:
        return list(set(obj))

# Flatten a nested list
def flatten(lst: list) -> list:
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

# Download a file
def download(url: str, path: str) -> None:
    try:
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(f"Error downloading file: {e}")

# Check if any item in a is in b
def any_in(a: list | str, b: list | str) -> bool:
    return any(item in b for item in a)

# Check if all items in a are in b
def all_in(a: list | str, b: list | str) -> bool:
    return all(item in b for item in a)

# Download an image
def download_image(url: str) -> Image:
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image: {e}")

# Format duration
def format_duration(seconds: int | float | str = 0) -> str:
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Get memory usage
def memory_usage():
    process = psutil.Process()
    return process.memory_info().rss

# Check if connected to the internet
def isnetwork() -> bool:
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Get n-th prime
def nprime(n: int = 1) -> int:
    # Sieve of Eratosthenes
    def sieve_of_eratosthenes(limit):
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for start in range(2, int(limit ** 0.5) + 1):
            if sieve[start]:
                for i in range(start * start, limit + 1, start):
                    sieve[i] = False
        return [num for num, is_prime in enumerate(sieve) if is_prime]
    limit = int(n * math.log(n) * 1.2)
    while True:
        primes = sieve_of_eratosthenes(limit)
        if len(primes) >= n:
            return primes[n - 1]
        limit *= 2

# Check if a number is prime
def isprime(n: int = 1) -> bool:
    if n <= 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Reverse each objekt in a list or string
def reverse(obj: list | str) -> list | str:
    if isinstance(obj, (list, tuple)):
        return type(obj)(item[::-1] if isinstance(item, (str, list, tuple)) else item for item in obj)
    elif isinstance(obj, str):
        return obj[::-1]
    return obj

# Pythagorean theorem
def pythagorean(a: float | int = None, b: float | int = None, c: float | int = None):
    if sum(x is not None for x in (a, b, c)) != 2:
        raise ValueError("Exactly two arguments must be provided")
    if any(x is not None and (not isinstance(x, (int, float)) or x < 0) for x in (a, b, c)):
        raise ValueError("Arguments must be non-negative numbers")
    if c is None:
        return math.sqrt(a**2 + b**2)
    if a is None:
        if c <= b:
            raise ValueError("Hypotenuse must be greater than leg")
        return math.sqrt(c**2 - b**2)
    if b is None:
        if c <= a:
            raise ValueError("Hypotenuse must be greater than leg")
        return math.sqrt(c**2 - a**2)
    raise ValueError("Invalid combination of arguments")

# Load a JSON file into a dictionary
def json_to_dict(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Get the n-th Fibonacci number
def fibonacci(n: int = 1) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Check if the given number is a Fibonacci number and return bool
def checkfib(x: int = 1, return_nearest: bool = False) -> bool | int:
    if not isinstance(x, int) or x < 0:
        return (False, 0) if return_nearest else False
    def is_perfect_square(n: int) -> bool:
        sqrt_n = int(math.sqrt(n))
        return sqrt_n * sqrt_n == n
    is_fib = is_perfect_square(5 * x * x + 4) or is_perfect_square(5 * x * x - 4)
    if not return_nearest:
        return is_fib
    # Find nearest Fibonacci number
    a, b = 0, 1
    while b < x:
        a, b = b, a + b
    nearest = b if abs(b - x) < abs(a - x) else a
    return is_fib, nearest

def var(name: str, value: any):
    globals()[name] = value
    return globals()[name]