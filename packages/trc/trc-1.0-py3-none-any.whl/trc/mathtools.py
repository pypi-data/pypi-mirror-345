# Import packages
import math, trc

# Get n-th prime
@trc.cache
def nprime(n: int = 1) -> int:
    # Sieve of Eratosthenes
    @trc.cache
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
@trc.cache
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

# Pythagorean theorem
@trc.cache
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

# Get the n-th Fibonacci number
@trc.cache
def fibonacci(n: int = 1) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Check if the given number is a Fibonacci number and return bool
@trc.cache
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