from datetime import datetime
from unittest import TestCase

import jsonpickle

from palaestrai.types import SimTime


class SimTimeTest(TestCase):
    def test_serializability(self):
        ts = datetime.fromisoformat("2023-11-29T14:16:54.424160")
        s = SimTime(simtime_ticks=10, simtime_timestamp=ts)
        s_json_encoded = jsonpickle.encode(s)
        self.assertEqual(
            s_json_encoded,
            '{"py/object": "palaestrai.types.simtime.SimTime", '
            '"py/state": {"simtime_ticks": 10, "simtime_timestamp": '
            '"2023-11-29T14:16:54.424160"}}',
        )

        s_json_decoded: SimTime = jsonpickle.decode(s_json_encoded)
        self.assertEqual(ts, s_json_decoded.simtime_timestamp)
        self.assertEqual(s.simtime_timestamp, s_json_decoded.simtime_timestamp)
        self.assertEqual(s.simtime_ticks, s_json_decoded.simtime_ticks)
