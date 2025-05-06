from __future__ import annotations

import re
from typing import Iterable, Any, Sequence

import functools
import gymnasium
import numpy as np
from numpy.typing import NDArray
from .space import Space


class MultiBinary(gymnasium.spaces.MultiBinary, Space):
    """A binary space of *n* dimensions

    MultiBinary implements an n-dimensional space of boolean values. E.g.,
    ``MultiBinary(5)`` accepts a vector of 5 boolean values.

    Parameters
    ----------
    n : NDArray[np.integer[Any]] | Sequence[int] | int
        The dimensions of the space. If a single integer is given, the space
        is flat; an array of integers allows multiple axes.
    seed : Optional[int, np.random.Generator]
        Allows to optionally seed the space
    """

    _RE = re.compile(r"\AMultiBinary\(\s*(?P<inner>\d+)\s*\)\Z")

    def __init__(
        self,
        n: NDArray[np.integer[Any]] | Sequence[int] | int,
        seed: int | np.random.Generator | None = None,
    ):
        gymnasium.spaces.MultiBinary.__init__(self, n, seed)
        Space.__init__(self)

    def to_vector(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Represent a given binary data as a flat vector."""
        return data.flatten()

    def reshape_to_space(self, value: Iterable, **kwargs) -> np.ndarray:
        """Turn a list of objects into binary data represented by a list.

        :kwargs: dtype: The dtype of the returned array.
                 default: int
        """
        return np.fromiter(value, kwargs.get("dtype", int))

    def to_string(self):
        return "MultiBinary(%s)" % self.n

    @classmethod
    @functools.cache
    def from_string(cls, s):
        match = MultiBinary._RE.match(s)
        if not match or not match["inner"]:
            raise RuntimeError(
                "String '%s' did not match '%s'" % (s, MultiBinary._RE)
            )
        return MultiBinary(int(match["inner"]))

    def __len__(self):
        return self.n
