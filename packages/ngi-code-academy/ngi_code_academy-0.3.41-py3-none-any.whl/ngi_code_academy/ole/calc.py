def add(a: float, b: float):
    """Adds the two numbers A and B together"""

    return a + b


def factorial(n: int) -> int:
    """Finds the factorial of n"""

    if n < 2:
        return 1

    return n * factorial(n - 1)


def multiply(a: float, b: float):
    """Multiplies the two numbers A and B together"""

    return a * b
