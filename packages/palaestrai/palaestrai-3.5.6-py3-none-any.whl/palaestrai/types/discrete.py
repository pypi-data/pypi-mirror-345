from __future__ import annotations

import re
from typing import Any

import functools
import gymnasium
import numpy as np

from .space import Space


class Discrete(gymnasium.spaces.Discrete, Space):
    """A discrete space in :math:`\\{ start, start + 1, \dots, start + n-1 \\}`.

    Example::

        >>> Discrete(2)

    """

    _RE = re.compile(r"\A\s*?Discrete\((\d+)\)\s*\Z")

    def __init__(
        self,
        n: int | np.integer[Any],
        seed: int | np.random.Generator | None = None,
        start: int | np.integer[Any] = 0,
    ):
        gymnasium.spaces.Discrete.__init__(self, n, seed, start)
        Space.__init__(self)

    def to_vector(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Flatten the discrete data to a ndarray of size self.n"""
        assert (
            data.shape == (1,) or data.shape == 1 or data.shape == ()
        ), f"Expected shape (1,) or 1 or (); Got {data.shape} instead"
        transformed = np.zeros(self.n)
        transformed[data.item()] = 1
        return np.array(transformed)

    def reshape_to_space(self, value: Any, **kwargs) -> np.ndarray:
        """Reshape the flat representation of data into a single number

        :kwargs: dtype: The dtype of the returned array.
                        default: float
        """
        if np.isscalar(value) or np.ndim(value) == 0:
            return np.array(value)
        as_array = np.fromiter(value, kwargs.get("dtype", float), self.n)
        assert (
            len(as_array) == self.n
        ), f"Expected {self.n} data points; Got {len(as_array)} instead"
        return np.array(as_array.argmax())

    def to_string(self):
        return self.__repr__()

    @classmethod
    @functools.cache
    def from_string(cls, s):
        match = Discrete._RE.match(s)
        if not match or not match[1]:
            raise RuntimeError(
                "String '%s' did not match '%s'" % (s, Discrete._RE)
            )
        return Discrete(int(match[1]))

    def __len__(self):
        return self.n
