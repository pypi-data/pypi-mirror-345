from __future__ import annotations
from typing import Any, List

import pickle
from pyzstd import compress, decompress


def serialize(request: Any) -> bytes:
    pick = pickle.dumps(request)
    return compress(pick)  # Makes sure no conversion makes problems.


def deserialize(response: List[bytes]) -> Any:
    if len(response) == 0:
        return None
    decompressed = decompress(response[0])
    return pickle.loads(decompressed)
