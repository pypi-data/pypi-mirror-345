from __future__ import annotations

import ast
import logging
import re
from typing import Any, Iterable, Sequence, SupportsFloat, List

import functools
import gymnasium
import numpy as np
from numpy.typing import NDArray

from palaestrai.util.dynaloader import locate
from .space import Space

LOG = logging.getLogger("palaestrai.types")


class Box(gymnasium.spaces.Box, Space):
    """A box in R^n, i.e.each coordinate is bounded.

    There are two common use cases:

    * Identical bound for each dimension::
        >>> Box(low=-1.0, high=2.0, shape=(3, 4), dtype=np.float32)
        Box(3, 4)

    * Independent bound for each dimension::
        >>> Box(low=np.array([-1.0, -2.0]), high=np.array([2.0, 4.0]), dtype=np.float32)
        Box(2,)

    """

    _BOX_RE = re.compile(r"\A\s*?Box\((.+)\)\s*\Z")
    _SHAPE_RE = re.compile(r"shape=\(((\d+, ?)|((\d+, ?)+\d+ ?)|())\)")
    _DTYPE_RE = re.compile(r"dtype=(np\.)?(\w+)")
    _LOW_BOUNDARY_RE = re.compile(
        r"low=((?P<single>[+\- einf.0-9]+)|(?P<list>\[[+\-\[\] .,0-9a-zA-Z]*\]))"
    )
    _HIGH_BOUNDARY_RE = re.compile(
        r"high=((?P<single>[+\- einf.0-9]+)|(?P<list>\[[+\-\[\] .,0-9a-zA-Z]*\]))"
    )

    def __init__(
        self,
        low: SupportsFloat | NDArray[Any] | List[Any],
        high: SupportsFloat | NDArray[Any] | List[Any],
        shape: Sequence[int] | None = None,
        dtype: type[np.floating[Any]] | type[np.integer[Any]] = np.float64,
        seed: int | np.random.Generator | None = None,
    ):
        if isinstance(low, list):
            low = np.asarray(low)
        if isinstance(high, list):
            high = np.asarray(high)
        gymnasium.spaces.Box.__init__(self, low, high, shape, dtype, seed)
        Space.__init__(self)

        # determine if the low and high values are uniform (used to speed up scale method)
        self._uniform_low_high = np.all(
            self.low.flatten() == self.low.flatten()[0]
        ) and np.all(self.high.flatten() == self.high.flatten()[0])

    def to_string(self):
        return "Box(low=%s, high=%s, shape=%s, dtype=np.%s)" % (
            self.low.tolist(),
            self.high.tolist(),
            self.shape,
            self.dtype,
        )

    @classmethod
    @functools.cache
    def from_string(cls, s):
        complete_match = Box._BOX_RE.match(s)
        if not complete_match:
            raise RuntimeError(
                "String '%s' does not match '%s'" % (s, Box._BOX_RE)
            )
        inner_str = complete_match[1]

        dtype_match = Box._DTYPE_RE.search(inner_str)
        if not dtype_match:
            raise RuntimeError(
                "No or invalid dtype in '%s' (pattern '%s')"
                % (inner_str, Box._DTYPE_RE)
            )
        dtype = locate("numpy.%s" % dtype_match[2])

        lower_boundary_match = Box._LOW_BOUNDARY_RE.search(inner_str)
        if not lower_boundary_match:
            raise RuntimeError(
                "No lower boundary in '%s' (%s)" % (s, Box._LOW_BOUNDARY_RE)
            )
        if lower_boundary_match["single"]:
            lower = float(lower_boundary_match["single"])
        else:  # list
            list_match = lower_boundary_match["list"]
            list_match = re.sub(r"([^.])-inf", '\\1"-inf"', list_match)
            lower = np.array(ast.literal_eval(list_match), dtype=dtype)

        higher_boundary_match = Box._HIGH_BOUNDARY_RE.search(inner_str)
        if not higher_boundary_match:
            raise RuntimeError(
                "No higher boundary in '%s' (%s)" % (s, Box._HIGH_BOUNDARY_RE)
            )
        if higher_boundary_match["single"]:
            higher = float(higher_boundary_match["single"])
        else:  # list
            # Make sure we can properly reference infinity; inf => np.Infinity:
            list_match = higher_boundary_match["list"]
            list_match = re.sub(r"([^.])inf", '\\1"inf"', list_match)
            higher = np.array(ast.literal_eval(list_match), dtype=dtype)

        shape = None
        if not type(higher) is np.ndarray:
            shape_match = Box._SHAPE_RE.search(inner_str)
            if not shape_match:
                raise RuntimeError(
                    "No or invalid shape in '%s' ('%s')"
                    % (inner_str, Box._SHAPE_RE)
                )
            shape = tuple(
                [
                    int(i)
                    for i in shape_match[1].replace(" ", "").split(",")
                    if i
                ]
            )

        return Box(low=lower, high=higher, shape=shape, dtype=dtype)

    def to_vector(self, data: np.ndarray, **kwargs) -> np.ndarray:
        """Flattens the data to a 1d array"""
        if not data.shape == self.shape:
            LOG.warning(
                "Box received data to flatten of shape %s while having shape %s",
                data.shape,
                self.shape,
            )
        return data.flatten()

    def reshape_to_space(self, value: Iterable, **kwargs) -> np.ndarray:
        """Reshape the data into the shape of the space with the dtype"""
        return np.reshape(value, self.shape).astype(self.dtype)  # type: ignore[call-overload]

    def scale(self, data, data_min=0, data_max=1):
        """Scale the given data linearly between box.low and box.high

        data_min and data_max represent the minimum and maximum value the data can take
        If they are given as a scalar, the method will treat them as min/max value over all dimensions,
        If they vary per dimension they have to be given in the same shape as `box.shape`
        """
        if self.shape is None:  # scalar case
            if np.isscalar(data):
                return np.interp(
                    data,
                    [data_min, data_max],
                    [self.low, self.high],
                )
            else:
                raise ValueError(
                    "Data must be scalar for box with scalar shape"
                )
        data_min = np.array(data_min)
        data_max = np.array(data_max)
        data = np.array(data)
        # make sure we have data, data_min and data_max we can work with
        assert (
            data_min.shape == self.shape
            or data_min.shape == tuple([1])
            or data_min.shape == ()
        ), f"data_min must be of shape (1), () or {self.shape}; Got {data_min.shape}"
        assert (
            data_max.shape == self.shape
            or data_max.shape == tuple([1])
            or data_max.shape == ()
        ), f"data_max must be of shape (1), () or {self.shape}; Got {data_max.shape}"
        assert (
            data.shape == self.shape
        ), f"data must be of shape {self.shape}; Got {data.shape}"

        # If we have uniform min/max and low/high values we can handle data as a flat array, which is faster
        if self._uniform_low_high and (
            data_min.shape == data_max.shape == 1
            or data_min.shape == data_max.shape == ()
        ):
            y = np.interp(
                data.flatten(),
                [data_min, data_max],
                [self.low.flatten()[0], self.high.flatten()[0]],
            )
            return y.reshape(self.shape)

        # if not we need to handle the dimensions individually
        def scale_next_dim(data, data_min, data_max, low, high):
            if len(data.shape) > 0:
                scaled = []
                for i in range(data.shape[0]):
                    scaled.append(
                        scale_next_dim(
                            data[i], data_min[i], data_max[i], low[i], high[i]
                        )
                    )
                return scaled
            else:
                return np.interp(
                    data,
                    [data_min, data_max],
                    [low, high],
                )

        return np.array(
            scale_next_dim(
                data,
                np.resize(data_min, self.shape),
                np.resize(data_max, self.shape),
                np.resize(self.low, self.shape),
                np.resize(self.high, self.shape),
            )
        )

    def __len__(self):
        return np.prod(self.shape)
