def divide(a: float, b: float) -> float:
    """
    Divide two numbers.

    Parameters:
    a (float): The numerator.
    b (float): The denominator.

    Returns:
    float: The result of the division.

    Raises:
    ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b
