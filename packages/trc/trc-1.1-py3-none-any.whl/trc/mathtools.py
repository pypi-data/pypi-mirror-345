# mathtools.py
# Import packages
import math, trc
from .utils import gcd_two

# Get n-th prime
@trc.cache
def nprime(n: int = 1) -> int:
    # Sieve of Eratosthenes
    """
    Find the n-th prime number using the Sieve of Eratosthenes algorithm.

    This function uses an internal cached implementation of the Sieve of Eratosthenes
    to generate a list of prime numbers up to a dynamically calculated limit.
    The limit is initially estimated based on the input n and is increased 
    if the number of primes found is insufficient. The function returns the 
    n-th prime number.

    :param n: The position of the prime number to find (1-based index).
    :return: The n-th prime number.
    :raises ValueError: If n is less than 1.
    """

    @trc.cache
    def sieve_of_eratosthenes(limit):
        """
        Generate a list of all prime numbers up to a given limit using the Sieve of Eratosthenes algorithm.

        This function takes an integer limit as input and returns a list of all prime numbers
        up to and including that limit. The Sieve of Eratosthenes algorithm is used to generate
        the list of primes in a single pass.

        :param limit: The upper limit of the range of prime numbers to generate (inclusive).
        :return: A list of all prime numbers in the range [2, limit].
        """
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
@trc.cache
def isprime(n: int = 1) -> bool:
    """
    Check if a number is prime.

    This function takes an integer as input and returns True if the number is prime, False otherwise.
    The function uses a simple algorithm to check for primality: it checks divisibility by 2 and 3, and
    then checks divisibility by all numbers of the form 6k ± 1 up to the square root of the input number.

    :param n: The number to check for primality.
    :return: True if n is prime, False otherwise.
    :raises ValueError: If n is not a positive integer.
    """
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

# Pythagorean theorem
@trc.cache
def pythagorean(a: float | int = None, b: float | int = None, c: float | int = None):
    """
    Calculate the third side of a right triangle using the Pythagorean theorem.

    The function takes three arguments, a, b and c, which represent the sides of the triangle.
    Exactly two of these arguments must be provided, and the function will return the remaining side.
    The arguments must be non-negative numbers.

    For example, if you call pythagorean(3, 4), the function will return 5.
    If you call pythagorean(5, None, 3), the function will return 4.
    If you call pythagorean(None, 4, 5), the function will return 3.

    :param a: One side of the triangle
    :param b: Another side of the triangle
    :param c: The hypotenuse of the triangle
    :return: The third side of the triangle
    :raises ValueError: If the arguments are invalid
    """
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

# Get the n-th Fibonacci number
@trc.cache
def fibonacci(n: int = 1) -> int:
    """
    Return the n-th Fibonacci number.

    This function computes the n-th Fibonacci number using a recursive approach.
    The Fibonacci sequence is defined as follows:
    - F(0) = 0
    - F(1) = 1
    - F(n) = F(n-1) + F(n-2) for n > 1

    The function uses caching to optimize repeated calculations of the same
    Fibonacci numbers.

    :param n: The position in the Fibonacci sequence (0-based index).
    :return: The n-th Fibonacci number.
    :raises ValueError: If n is not a non-negative integer.
    """

    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Check if the given number is a Fibonacci number and return bool
@trc.cache
def checkfib(x: int = 1, return_nearest: bool = False) -> bool | int:
    """
    Check if the given number is a Fibonacci number and return bool.

    This function checks if the given number is a Fibonacci number.
    If return_nearest is True, the function returns a tuple (bool, int) where
    bool is True if x is a Fibonacci number and int is the nearest Fibonacci number
    to x. If return_nearest is False (default), the function only returns bool.

    :param x: The number to check.
    :param return_nearest: If True, return the nearest Fibonacci number in addition to the bool.
    :return: bool or tuple (bool, int)
    :raises ValueError: If x is not a non-negative integer.
    """
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

# Factorize a number into its prime factors
@trc.cache
def factorize(n: int) -> list:
    """
    Factorize a number into its prime factors.

    :param n: The number to factorize.
    :return: A list of prime factors of n.
    """
    factors = []
    i = 2
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 1
    if n > 1:
        factors.append(n)
    return factors

# Greatest Common Divisor (GCD) for multiple numbers
@trc.cache
def gcd(*args: int) -> int:
    """
    Compute the greatest common divisor of multiple integers.
    The GCD is the largest number that divides all input numbers without a remainder.

    :param args: Variable number of integers (at least two).
    :return: Greatest common divisor of all input numbers.
    :raises ValueError: If fewer than two numbers are provided, or if any input is not a positive integer.
    :raises TypeError: If any input is not an integer.
    """
    if len(args) < 2:
        raise ValueError("At least two numbers are required")
    if not all(isinstance(x, int) for x in args):
        raise TypeError("All inputs must be integers")
    if not all(x > 0 for x in args):
        raise ValueError("All inputs must be positive integers")
    
    result = args[0]
    for num in args[1:]:
        result = gcd_two(result, num)
    return result

# Least Common Multiple (LCM) for multiple numbers
@trc.cache
def lcm(*args: int) -> int:
    """
    Compute the least common multiple of multiple integers.
    The LCM is the smallest number that is a multiple of all input numbers.

    :param args: Variable number of integers (at least two).
    :return: Least common multiple of all input numbers.
    :raises ValueError: If fewer than two numbers are provided, or if any input is not a positive integer.
    :raises TypeError: If any input is not an integer.
    """
    if len(args) < 2:
        raise ValueError("At least two numbers are required")
    if not all(isinstance(x, int) for x in args):
        raise TypeError("All inputs must be integers")
    if not all(x > 0 for x in args):
        raise ValueError("All inputs must be positive integers")
    
    def lcm_two(a: int, b: int) -> int:
        return abs(a * b) // gcd_two(a, b)
    
    result = args[0]
    for num in args[1:]:
        result = lcm_two(result, num)
    return result