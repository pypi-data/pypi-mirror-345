from __future__ import annotations

from typing import Optional, Union
from datetime import datetime


class SimTime:
    """Variable representation of a point in time in any environment

    This class represents points in time within a simulated environment. It
    allows to express two distinct scales of measurement: Ticks and actual
    datetime objects.

    *Ticks* are a certain step (‘tick’) of a simulation. They are an abstract
    measure for advancement of a simulation and can refer to anything, such as
    events executed, etc. They have to be monotonically increasing, though.

    *Timestamps* are actual :class:`datetime.datetime` objects referring to a
    certain point of simulated time.
    """

    def __init__(
        self,
        simtime_ticks: Optional[int] = None,
        simtime_timestamp: Optional[datetime] = None,
    ):
        assert simtime_ticks is None or isinstance(simtime_ticks, int), (
            f"simtime_ticks( "
            f"{str(simtime_ticks)}) is not of type Optional[int]"
        )
        assert simtime_timestamp is None or isinstance(
            simtime_timestamp, datetime
        ), (
            f"simtime_timestamp({str(simtime_timestamp)}) "
            f"is not of type Optional[datetime]"
        )

        self._simtime_ticks: Optional[int] = simtime_ticks
        self._simtime_timestamp: Optional[datetime] = simtime_timestamp

    @property
    def simtime_ticks(self) -> Optional[int]:
        return self._simtime_ticks

    @simtime_ticks.setter
    def simtime_ticks(self, simtime_ticks: Optional[int]):
        assert simtime_ticks is None or isinstance(simtime_ticks, int), (
            f"simtime_ticks( "
            f"{str(simtime_ticks)}) is not of type Optional[int]"
        )
        self._simtime_ticks = simtime_ticks

    @property
    def simtime_timestamp(self) -> Optional[datetime]:
        return self._simtime_timestamp

    @simtime_timestamp.setter
    def simtime_timestamp(
        self, simtime_timestamp: Optional[Union[str, datetime]]
    ):
        _simtime_timestamp = simtime_timestamp
        if isinstance(simtime_timestamp, str):
            _simtime_timestamp = datetime.fromisoformat(simtime_timestamp)
        assert _simtime_timestamp is None or isinstance(
            _simtime_timestamp, datetime
        ), (
            f"simtime_timestamp({str(_simtime_timestamp)}) "
            f"is not of type Optional[datetime]"
        )

        self._simtime_timestamp = _simtime_timestamp

    def __getstate__(self):
        return dict(
            simtime_ticks=self.simtime_ticks,
            simtime_timestamp=(
                self.simtime_timestamp.isoformat()
                if self.simtime_timestamp is not None
                else None
            ),
        )

    def __setstate__(self, state: dict):
        self.simtime_ticks = state["simtime_ticks"]
        self.simtime_timestamp = state["simtime_timestamp"]

    def __repr__(self):
        return (
            f"SimTime(simtime_ticks={self.simtime_ticks}, "
            f"simtime_timestamp={repr(self.simtime_timestamp)})"
        )

    def __str__(self):
        return repr(self)
