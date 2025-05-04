from copy import copy
from collections import defaultdict
import functools

from .matcher import _get_matcher
from ._it import pairwise
from ._seq import _unique_sequence
from ._op import _concat, concat


def union(*args, matcher=None):
    """Union of multiple parameters.

    This function can merge multiple ``dict``'s into one ``dict``. If two
    ``dict``'s ``d1`` and ``d2`` have the same key ``k``, ``union(d1, d2)``
    will use the value of ``d1[k]`` rather than ``d2[k]``, which differs from
    ``d1 | d2`` who takes ``d2[k]``.

    Parameters:
        *args
        matcher (Matcher)

    Examples:
        >>> union([1, 2, 3], [3, 2], [2, 4], [])
        [1, 2, 3, 4]
        >>> union((1, 2, 3), (3, 2), (2, 4), ())
        (1, 2, 3, 4)

        The following example considers a list and moves some of its elements to the front.

        >>> a = [1, 2, 3, 4, 5]  # the list
        >>> f = [3, 4]  # some elements that need to appear first
        >>> union(f, a)
        [3, 4, 1, 2, 5]

        Union of multiple ``dict``'s:

        >>> union({'a': 1, 'b': 2}, {'c': 13, 'a': 11}, {})
        {'a': 1, 'b': 2, 'c': 13}

        Use a matcher:

        >>> from calcpy.matcher import from_callable
        >>> matcher = from_callable(len)  # compare the length of each element
        >>> union(["alpha", "beta"], ["gamma", "delta"], ["pi", "omega"], matcher=matcher)
        ['alpha', 'beta', 'pi']

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.union
    """
    matcher = _get_matcher(args[0], matcher=matcher)
    concated = _concat(*args, matcher=matcher, assemble=False)
    return _unique_sequence(concated, matcher=matcher, dissemble=False)


def isdisjoint(*args, matcher=None):
    """Check if the parameters are disjoint.

    Parameters:
        *args
        matcher (Matcher)

    Returns:
        bool:

    Examples:
        >>> isdisjoint([1, 2, 3], [2, 3, 4], [3, 4])
        False
        >>> isdisjoint([1, 2, 3], [4, 5, 6], [7, 8, 9])
        True

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.isdisjoint
    """
    matcher = _get_matcher(args[0], matcher=matcher)
    concated = concat(*args, matcher=matcher)
    unioned = union(*args, matcher=matcher)
    return len(concated) == len(unioned)


def _wrapper2(fun, matcher):
    def f(loper, roper):
        loper = matcher.disassemble(loper)
        roper = matcher.disassemble(roper)
        results = fun(loper, roper, matcher)
        return matcher.assemble(results)
    return f


def _wrapper(fun):
    """Extend binary function to multi-ary function."""
    def f(*args, matcher=None):
        if len(args) == 0:
            return args
        matcher = _get_matcher(args[0], matcher=matcher)
        return functools.reduce(_wrapper2(fun, matcher), args)
    return f


def _wrapper_1dict(fun):
    """Support the case when the first parameter is a dict."""
    def f(*args, matcher=None):
        op = _wrapper(fun)
        if len(args) >= 1 and isinstance(args[0], (dict, defaultdict)):
            arg = args[0]
            arglist = list(arg)
            params = list(args)
            params[0] = arglist
            keys = op(*params, matcher=matcher)
            results = copy(arg)
            for key in arglist:
                if key not in keys:
                    results.pop(key)
            return results
        return op(*args, matcher=matcher)
    return f


def _intersection2(loper, roper, matcher):
    results = []
    for l in loper:  # noqa: E741
        for r in roper:
            if matcher(l, r):
                results.append(l)
                break
    return results


def _difference2(loper, roper, matcher):
    results = []
    for l in loper:  # noqa: E741
        for r in roper:
            if matcher(l, r):
                break
        else:
            results.append(l)
    return results


def _symmetric_difference2(loper, roper, matcher):
    return concat(_difference2(loper, roper, matcher=matcher), _difference2(roper, loper, matcher=matcher))


def _issubset2(loper, roper, matcher):
    for l in loper:  # noqa: E741
        for r in roper:
            if matcher(l, r):
                break
        else:
            return False
    return True


def _issuperset2(loper, roper, matcher):
    for r in roper:
        for l in loper:  # noqa: E741
            if matcher(l, r):
                break
        else:
            return False
    return True


intersection = _wrapper_1dict(_intersection2)
intersection.__doc__ = \
    """Intersect of multiple parameters.

    The first argument can be a ``dict``, while the following positions can not
    be a ``dict``. If the first argument is a ``dict``, it means to limit the keys
    of the first arugment within the list specified by the intersection of
    follow-up position arguments (if any).

    Parameters:
        *args
        matcher (Matcher)

    Examples:
        >>> intersection('abcd', 'edc')
        'cd'

        The case when the first argument is a ``dict``.

        >>> intersection({'a': 1, 'b': 2, 'c': 3})
        {'a': 1, 'b': 2, 'c': 3}
        >>> intersection({'a': 1, 'b': 2, 'c': 3}, ['a', 'c'])
        {'a': 1, 'c': 3}

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.intersection
    """

difference = _wrapper_1dict(_difference2)
difference.__doc__ = \
    """Exclude follow-up parameters from the first one.

    The first argument can be a ``dict``, while the following positions can not
    be a ``dict``. If the first argument is a ``dict``, it means to exclude all
    elements in the follow-up arguments out of the key of the first position
    argument.

    Parameters:
        *args
        matcher (Matcher)

    Examples:
        >>> difference('abcd', 'cat', 'bed')
        ''

        The case when the first argument is a ``dict``.

        >>> difference({'a': 1, 'b': 2, 'c': 3})
        {'a': 1, 'b': 2, 'c': 3}
        >>> difference({'a': 1, 'b': 2, 'c': 3}, ['b'])
        {'a': 1, 'c': 3}

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.difference
    """

symmetric_difference = _wrapper(_symmetric_difference2)
symmetric_difference.__doc__ = \
    """Pick elements that appear in odd number of parameters.

    Parameters:
        *args
        matcher (Matcher)

    Examples:
        >>> symmetric_difference([1, 2, 3], [2, 3, 4], [3, 4])
        [1, 3]
        >>> symmetric_difference('hello', 'he', 'okay')
        'llkay'

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.symmetric_difference
    """


def _allpairwise_wrapper(fun):
    """Wrapper for better function signatures."""
    def f(*args, matcher=None):
        if len(args) <= 1:
            return True
        matcher = _get_matcher(args[0], matcher=matcher)
        return all(fun(*p, matcher=matcher) for p in pairwise(args))
    return f


issubset = _allpairwise_wrapper(_issubset2)
issubset.__doc__ = \
    """Check if the parameter is a subset of the follow-up parameter.

    Parameters:
        *args
        matcher (Matcher)

    Returns:
        bool:

    Examples:
        >>> issubset([1, 2, 3], [1, 2, 3, 4, 5])
        True
        >>> issubset([], [1, 2, 3], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        True
        >>> issubset([1, 2, 3], [1, 5, 6])
        False

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.issubset
    """

issuperset = _allpairwise_wrapper(_issuperset2)
issuperset.__doc__ = \
    """Check if the parameter is a superset of the follow-up parameter.

    Parameters:
        *args
        matcher (Matcher)

    Returns:
        bool:

    Examples:
        >>> issuperset([1, 2, 3, 4, 5], [1, 2, 3])
        True
        >>> issuperset([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3], [])
        True
        >>> issuperset([1, 2, 3], [4, 5, 6])
        False

    See also:
        https://docs.python.org/3/library/stdtypes.html#frozenset.issuperset
    """
