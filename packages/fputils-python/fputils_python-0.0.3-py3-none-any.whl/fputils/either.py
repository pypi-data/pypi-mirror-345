from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable

"""Provides the Either monad for managing the flow of computation in a functional manner.
"""


class Either[A, B](metaclass=ABCMeta):
    """Generic Either monad to represent a value that can be one of two types."""

    def _get_value(self) -> A | B:
        return self.__value

    def _set_value(self, value: A | B):
        self.__value = value

    _value = property(_get_value, _set_value)

    @abstractmethod
    def is_left(self) -> bool:
        return NotImplemented

    @abstractmethod
    def is_right(self) -> bool:
        return NotImplemented

    def contains(self, value: B) -> bool:
        """
        Returns:
            True if Right and its value is equal to the given value, False otherwise.
        """
        return False if self.is_left() else self._value == value

    def exists(self, predicate: Callable[[B], bool]) -> bool:
        """
        Returns:
            False if Left or returns the result of the given predicate against the Right value.
        """
        return False if self.is_left() else predicate(self._value)

    def filter_or_else(self, predicate: Callable[[B], bool], other: A) -> Either[A, B]:
        """
        Returns:
            self if this is a Left,
            Left(other) if this is a Right and the given predicate does not hold for the Right value,
            or self if this is a Right and the given predicate does hold for the Right value.
        """
        return Left(other) if self.is_right() and not predicate(self._value) else self

    def flatmap[B1](self, f: Callable[[B], Either[A, B1]]) -> Either[A, B1]:
        """Binds the given function against Right.
        Returns:
            self if this is a Left,
            f(self._value) if this is a Right.
        """
        return Left(self._value) if self.is_left() else f(self._value)

    def flatten[B1](self) -> Either[A, B1]:
        """
        Returns:
            The right value if this is a Right and the right value is an Either,
            self if this is a Left,

        raises:
            AssertionError: if this is a Right and the right value is not an Either.
        """
        assert isinstance(self._value, Either)
        return self.flatmap(lambda _: self._value)

    def fold[C](self, fa: Callable[[A], C], fb: Callable[[B], C]) -> C:
        """
        Returns:
            fa(self._value) if this is a Left,
            fb(self._value) if this is a Right.
        """
        return fa(self._value) if self.is_left() else fb(self._value)

    def forall(self, f: Callable[[B], bool]) -> bool:
        """
        Returns:
            True if this is a Left,
            True if this is a Right and the given predicate holds for the Right value,
            False otherwise.
        """
        return True if self.is_left() else f(self._value)

    def foreach(self, f: Callable[[B], None]) -> None:
        """
        Applies the given function against the Right value if this is a Right.
        No-Op if this is a Left.
        """
        if self.is_right():
            f(self._value)

    def get_or_else(self, other: B) -> B:
        """
        Returns:
            self._value if this is a Right,
            the given argument if this is a Left.
        """
        return self._value if self.is_right() else other

    def map(self, f: Callable[[B], B]) -> Either[A, B]:
        """Applies the given function against the Right value if this is a Right.
        Returns:
            self if this is a Left,
            Right(f(self._value)) if this is a Right.
        """
        return self.flatmap(lambda x: Right(f(x)))

    def or_else(self, other: Either) -> Either[A, B]:
        """
        Returns:
            self if this is a Right,
            the given argument if this is a Left.
        """
        return self if self.is_right() else other

    def swap(self) -> Either[B, A]:
        """
        Returns:
            this as a Left if this is a Right,
            this as a Right if this is a Left.
        """
        return Left(self._value) if self.is_right() else Right(self._value)

    def to_list(self) -> list[B]:
        """
        Returns:
            An empty list if this is a Left,
            a list containing the Right value if this is a Right.
        """
        return [] if self.is_left() else [self._value]


class Left[A, B](Either[A, B]):
    def __init__(self, value: A):
        self._value = value

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False


class Right[A, B](Either[A, B]):
    def __init__(self, value: B):
        self._value = value

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True
