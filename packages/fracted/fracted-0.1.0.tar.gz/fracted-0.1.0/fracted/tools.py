"""Contains simple and sometimes useful functions.
"""

from typing import Callable, ParamSpec, TypeVar

T = TypeVar("T")
U = TypeVar("U")
P = ParamSpec("P")


def compose_funcs(f1: Callable[P, T], f2: Callable[[T], U]) -> Callable[P, U]:
    """Composes two Callables into one function.

    If the output function is called, `f2` is called on output from `f1`
    and output from `f2` is returned.

    Parameters
    ----------
    f1 : Callable[P, T]
        The first function. It will be called on output function's arguments.
    f2 : Callable[[T], U]
        The second function. It will be called on output of `f1` and output
        of `f2` is returned.

    Returns
    -------
    Callable[P, U]
        Function composed from `f1` and `f2`.
    """

    def composed(*args: P.args, **kwargs: P.kwargs) -> U:
        return f2(f1(*args, **kwargs))

    return composed


def append_func_before(
    f1: Callable[P, T]
) -> Callable[[Callable[[T], U]], Callable[P, U]]:
    """Appends `f1` to a function to be called before the function.

    Use of this decorator is same as
    `decorated_function = compose_funcs(f1, decorated_function)`

    Parameters
    ----------
    f1 : Callable[P, T]
        A `Callable` to be called before the decorated function.

    Returns
    -------
    Callable[[Callable[[T], U]], Callable[P, U]]
        A decorator that appends `f1` to te decorated function.

    See Also
    --------
    compose_funcs : Composes two Callables into one function.
    """

    def decorator(f2: Callable[[T], U]) -> Callable[P, U]:
        return compose_funcs(f1, f2)

    return decorator


def append_func_after(
    f2: Callable[[T], U]
) -> Callable[[Callable[P, T]], Callable[P, U]]:
    """Appends `f2` to a function to be called after the function.

    Use of this decorator is same as
    `decorated_function = compose_funcs(decorated_function, f2)`

    Parameters
    ----------
    f2 : Callable[P, T]
        A `Callable` to be called after the decorated function.

    Returns
    -------
    Callable[[Callable[[T], U]], Callable[P, U]]
        A decorator that appends `f2` to te decorated function.

    See Also
    --------
    compose_funcs : Composes two Callables into one function.
    """

    def decorator(f1: Callable[P, T]) -> Callable[P, U]:
        return compose_funcs(f1, f2)

    return decorator
