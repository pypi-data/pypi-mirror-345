from ._seq import cycleperm


class cyclepermcaller:
    """Callable that swaps position parameters according to cyclc notation.

    Parameters:
        f (callable):
        cycle (list | tuple): List of indices to swap.

    Returns:
        callable:

    Examples:
        >>> executor = cyclepermcaller(range, cycle=[0, 1])
        >>> executor(3, 2, 6)
        range(2, 3, 6)

        >>> executor = cyclepermcaller(range, cycle=[1, 2])
        >>> executor(3, 2, 6)
        range(3, 6, 2)
    """
    def __init__(self, f, /, cycle=()):
        self.f = f
        self.cycle = cycle

    def __call__(self, *args, **kwargs):
        args = cycleperm(list(args), cycle=self.cycle)
        return self.f(*args, **kwargs)


class swapcaller(cyclepermcaller):
    """Callable that swaps positional arguments in a pair.

    Parameters:
        f (callable):
        i (int): Index of the argument to swap.
        j (int): Index of another argument to swap.

    Returns:
        callable:

    Examples:
        >>> executor = swapcaller(range)
        >>> executor(3, 2, 6)
        range(2, 3, 6)

        >>> executor = swapcaller(range, i=1, j=2)
        >>> executor(3, 2, 6)
        range(3, 6, 2)
    """
    def __init__(self, f, /, i=0, j=1):
        super().__init__(f, cycle=[i, j])


def call(f, *args, **kwargs):
    """Call a callable with positional arguments and keyword arguments.

    Parameters:
        f: Callable object.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Result of the callable.

    Examples:
        >>> call(range, 2, 3, 6)
        range(2, 3, 6)
    """
    return f(*args, **kwargs)


def merge_args(f, /):
    """Merge all positional arguments of a function to a single tuple argument

    Parameters:
        f (callable):

    Returns:
        callable:

    Examples:
        >>> merge_args(print)([0, 1.0, "Hello"])
        0 1.0 Hello
    """
    def fun(args, **kwargs):
        return f(*args, **kwargs)
    return fun


def demerge_args(f, /):
    """Replace a single tuple/list argument to many positional arguments.

    Parameters:
        f (callable):

    Returns:
        callable:

    Examples:
        >>> demerge_args(all)(True, True, True)
        True
    """
    def fun(*args, **kwargs):
        return f(args, **kwargs)
    return fun
