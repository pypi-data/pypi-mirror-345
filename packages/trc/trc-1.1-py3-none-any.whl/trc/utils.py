# utils.py
# Import packages
import trc

# Helper function for GCD of two numbers
@trc.cache
def gcd_two(a: int, b: int) -> int:
    """
    Compute the greatest common divisor of two integers using the Euclidean algorithm.
    :param a: First integer.
    :param b: Second integer.
    :return: GCD of a and b.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a