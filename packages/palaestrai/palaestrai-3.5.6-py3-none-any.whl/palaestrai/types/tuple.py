from __future__ import annotations

import re
import typing
from typing import Iterable

import functools
import gymnasium
import numpy as np

from .space import Space


class Tuple(gymnasium.spaces.Tuple, Space):  # type: ignore
    """A tuple (i.e., product) of simpler spaces

    Example usage:
    self.observation_space = spaces.Tuple(Discrete(2), Discrete(3))
    """

    _TUPLE_RE = re.compile(r"\A\s*?Tuple\((.+)\)\s*\Z")
    _INNER_PIECE_RE = re.compile(
        r"(?P<inner_rest>,\s*" r"(?P<piece>[A-Za-z]+\(.*\)))\s*\Z"
    )

    def __init__(
        self,
        spaces,
        seed: int | typing.Sequence[int] | np.random.Generator | None = None,
    ):
        gymnasium.spaces.Tuple.__init__(self, spaces, seed)
        Space.__init__(self)

    def to_vector(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Flatten data using the contained spaces"""
        return np.array(
            [s.to_vector(data[idx]) for idx, s in enumerate(self.spaces)]  # type: ignore[attr-defined]
        )

    def reshape_to_space(self, value: Iterable, **kwargs) -> np.ndarray:
        """Reshape value using the contained spaces"""
        as_list = np.array(value)
        return np.array(
            [
                s.reshape_to_space(as_list[idx])  # type: ignore[attr-defined]
                for idx, s in enumerate(self.spaces)
            ]
        )

    def to_string(self):
        return "Tuple(" + ", ".join([str(s) for s in self.spaces]) + ")"

    @classmethod
    @functools.cache
    def from_string(cls, s):
        complete_match = Tuple._TUPLE_RE.match(s)
        if not complete_match:
            raise RuntimeError(
                "String '%s' does not match '%s'" % (s, Tuple._TUPLE_RE)
            )
        inner_str = complete_match[1]

        spaces = []
        while len(inner_str) > 0:
            match = Tuple._INNER_PIECE_RE.search(inner_str)
            if match is None:
                try:
                    spaces.append(Space.from_string(inner_str))
                except:
                    pass  # We simply ignore garbage.
                break
            else:
                head, _, tail = inner_str.rpartition(match["inner_rest"])
                inner_str = head + tail
                spaces.append(Space.from_string(match["piece"]))
        spaces.reverse()

        return Tuple(*spaces)
