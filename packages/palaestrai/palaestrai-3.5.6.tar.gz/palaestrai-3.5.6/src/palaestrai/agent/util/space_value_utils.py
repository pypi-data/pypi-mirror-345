from __future__ import annotations

import logging
import traceback
from typing import Any, Union, Optional, List

import numpy as np

from palaestrai.types import Space

LOG = logging.getLogger(__name__)


def _space_contains(space: Space, value: Any):
    """
    This method take some allowances from how palaestrai types are used and how
    gymnasium expects formats of value of as space to be contained.

    In palaestrai plain python types, like ints or floats are allowed. For
    the space containing check they are wrapped into np.ndarrays by
    inferring their type dynamically.

    Besides this, also values already wrapped into np.ndarrays are allowed.
    In this case their type is given by the dtype attrib.

    Parameters
    ----------
    space: Space
        The space in which the value should be checked to be contained in
    value: Any
        The value that should be checked to be contained in the space

    Returns
    -------
    bool
        Indicator of the given value is contained in the given space
    """
    if isinstance(value, list):
        try:
            # This no longer works for inferring dtype=objects from sequences
            # See: https://numpy.org/neps/nep-0034-infer-dtype-is-object.html
            wrapped_value = np.asarray(value)
        except ValueError:
            LOG.warning(
                "Could not coerce dtype and cast value to numpy "
                "array with that type! Now trying with "
                "numpy array casting with generic object dtype."
            )
            wrapped_value = np.asarray(value, dtype=object)
    else:
        used_dtype = type(value)
        if hasattr(value, "dtype"):
            used_dtype = value.dtype
        wrapped_value = np.array(value, dtype=used_dtype)

    return space.contains(wrapped_value)


def check_value_is_none(value: Any) -> bool:
    if value is None:
        LOG.debug(
            "The stored and thus the returned value is None. Normally, "
            "the value should be set for the information objects!",
            stack_info=True,
        )
        return True
    return False


def assert_value_in_space(
    space: Space,
    value: Any,
    error: Optional[Union[TypeError, Exception]] = None,
    uid: Optional[str] = None,
):
    if not check_value_is_none(value):
        try:
            contains = _space_contains(space, value)
        except Exception:
            LOG.exception("Unexpected error during space check:")
            raise
        else:
            if not contains:
                if isinstance(error, TypeError) or isinstance(
                    error, Exception
                ):
                    raise error
                else:
                    error_msg = (
                        f'Value "{str(value)}" not contained '
                        f'in space "{str(space)}"'
                    )
                    if uid is not None:
                        error_msg += f", for uid: {uid}"

                    raise TypeError(error_msg)
