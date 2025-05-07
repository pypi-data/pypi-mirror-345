def power(base: float, exponent: float) -> float:
    """
    计算一个数的乘方

    Args:
        base (float): 底数
        exponent (float): 指数

    Returns:
        float: base 的 exponent 次方

    Examples:
        >>> power(2, 3)
        8.0
        >>> power(2.5, 2)
        6.25
    """
    return base ** exponent 