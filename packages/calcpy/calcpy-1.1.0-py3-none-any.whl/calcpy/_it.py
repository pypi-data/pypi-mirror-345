"""Extensions to itertools"""

try:
    from itertools import pairwise  # noqa: F401
except Exception:
    from itertools import tee

    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


def allpairwise_call(binop):
    """Return True when binary operator returns True for each pair of arguments.

    Parameters:
        binop: Binary operator
        *args: Arguments
        **kwargs: Keyword arguments

    Returns:
        bool

    Examples:
        >>> import operator
        >>> allpairwise_call(operator.lt)()
        True
        >>> allpairwise_call(operator.lt)(1)
        True
        >>> allpairwise_call(operator.lt)(1, 2, 3, 4)
        True
        >>> allpairwise_call(operator.lt)(1, 2, 2, 4)
        False
    """
    def fun(*args):
        iterable = (binop(*p) for p in pairwise(args))
        return all(iterable)
    return fun
