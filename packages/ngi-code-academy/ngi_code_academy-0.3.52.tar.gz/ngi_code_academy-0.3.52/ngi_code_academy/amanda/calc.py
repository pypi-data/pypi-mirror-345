def add(a: float, b: float):
    """Adds the two numbers A and B together"""

    return a + b


def factorial(n: int) -> int:
    """Finds the factorial of n"""

    if n < 2:
        return 1

    return n * factorial(n - 1)


def minus(a: float, b: float):
    """Subtracts the number B from A"""

    return a - b
