from copy import copy
import operator

import numpy as np
import pandas as pd

from .matcher import _get_matcher


def _unique_sequence(values, matcher=None, dissemble=True):
    if dissemble:
        values = matcher.disassemble(values)
    results = []
    for value in values:
        for result in results:
            if matcher(result, value):
                break
        else:
            results.append(value)
    results = matcher.assemble(results)
    return results


def unique(values, *, matcher=None):
    """Drop duplications with original order kept.

    Parameters:
        values (iterable)
        matcher (Matcher)

    Returns:
        Unique values

    Example:
        >>> unique([1, 2, 2, 3, 2, 1, 2])
        [1, 2, 3]
        >>> unique((1, 2, 2, 3, 2, 1, 2))
        (1, 2, 3)
        >>> unique('Hello')
        'Helo'
    """
    if len(values) == 0 or isinstance(values, dict):
        return values
    if isinstance(values, (str, bytes, bytearray, list, tuple, set, np.ndarray, pd.Series, pd.DataFrame)):
        matcher = _get_matcher(values, matcher)
        return _unique_sequence(values, matcher=matcher)
    return pd.unique(values)


def count_unique(values, *, matcher=None):
    """Count the number of distinct elements.

    Parameters:
        values (iterable)
        matcher (Matcher)

    Returns:
        int: Number of distinct elements.

    Examples:
        >>> count_unique([1, 2, 2, 3, 2, 1, 2])
        3
        >>> count_unique('Hello')
        4
    """
    result = len(unique(values, matcher=matcher))
    return result


def min_repetend_len(values, *, allow_frac=True, matcher=None):
    """Get minimum length of repetends.

    Parameters:
        values (list): List of values as a sequence.
        allow_frac (bool): Whether to allow partial repetend at the end of sequence.
        matcher: A object to be used to determine whether two values are the same.

    Returns:
        int: The minimum length of repetends.

    Examples:
        >>> min_repetend_len([1, 1, 1, 1])
        1
        >>> min_repetend_len([1, 2, 1, 2])
        2
        >>> min_repetend_len([1, 2, 1, 3])
        4
        >>> min_repetend_len([1, 2, 1, 3, 1, 2, 1, 3])
        4
        >>> min_repetend_len([1, 2, 1, 2, 1, 2, 1], allow_frac=False)
        7
    """
    length = len(values)
    matcher = matcher or operator.eq
    for l in range(1, length):  # noqa: E741
        if (not allow_frac) and (length % l > 0):
            continue
        for i in range(length-l):
            if not matcher(values[i], values[i+l]):
                break
        else:
            return l
    return length


def cycleperm(values, /, cycle):
    """Permutate a list according to cycle notation.

    Parameters:
        values (list): Sequence to permutate.
        cycle (list): Permutation rule in cyclc notation.

    Returns:
        list: Permutated sequence.

    Examples:
        Permutate a list of strings.

        >>> cycleperm(["a", "b", "c", "d", "e", "f", "g"], cycle=[1, 2, 4])
        ['a', 'c', 'e', 'd', 'b', 'f', 'g']

        Permutate a list of integers.

        >>> cycleperm(list(range(6)), cycle=[0, 1, 2])
        [1, 2, 0, 3, 4, 5]
    """
    results = copy(values)
    for i, v in enumerate(cycle):
        results[v] = values[cycle[(i+1) % len(cycle)]]
    return results


def swap(values, /, i=0, j=1):
    """Swap two elements in a list.

    Parameters:
        values (list): Sequence to permutate.
        i (int): Index of the first element to swap.
        j (int): Index of the second element to swap.

    Returns:
        list: Swapped sequence.

    Examples:
        Swap two elements for a list of strings.

        >>> swap(["a", "b", "c", "d", "e", "f", "g"], i=1, j=2)
        ['a', 'c', 'b', 'd', 'e', 'f', 'g']

        Swap two elements for a list of integers.

        >>> swap(list(range(6)), i=1, j=2)
        [0, 2, 1, 3, 4, 5]
    """
    return cycleperm(values, cycle=[i, j])
