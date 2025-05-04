from typing import Self

from fracted import tools
from fracted.types import Point, TransformationLike


class Transformation:
    """A class for better work with point transformations.

    An instance of this class is created with some function. This function is
    called when the instance is called. This class allows you to use '@' operator
    to compose two or more transformations.

    Attributes
    ----------
    func : TransformationLike
        This function is called when Transformation instance is called.
    """

    func: TransformationLike

    def __init__(self, func: TransformationLike) -> None:
        self.func = func

    def __call__(self, point: Point) -> Point:
        return self.func(point)

    def __matmul__(self, other: TransformationLike) -> Self:
        """Compose two transformations using the matrix multiplication operator (`@`).

        Parameters
        ----------
        other : TransformationLike
            The transformation to apply before this one.

        Returns
        -------
        Self
            A new transformation equivalent to applying `other` followed by this one.
        """
        return type(self)(tools.compose_funcs(other, self.func))

    def __rmatmul__(self, other: TransformationLike) -> Self:
        """Compose two transformations using the matrix multiplication operator (`@`).

        Parameters
        ----------
        other : TransformationLike
            The transformation to apply after this one.

        Returns
        -------
        Self
            A new transformation equivalent to applying this one followed by other.
        """
        return type(self)(tools.compose_funcs(self.func, other))

    def __imatmul__(self, other: TransformationLike) -> Self:
        """Append another transformation to be applied after this one.

        Parameters
        ----------
        other : TransformationLike
            The transformation to apply after this one.

        Returns
        -------
        Self
            The updated transformation - still the same instance.
        """
        self.func = tools.compose_funcs(self.func, other)
        return self

    def append_before(self, other: TransformationLike) -> None:
        """Append another transformation to be applied before this one.

        Parameters
        ----------
        other : TransformationLike
            The transformation to apply before this one.
        """
        self.func = tools.compose_funcs(other, self.func)
