def divide(a: float, b: float) -> float:
    """Divides two numbers."""

    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
