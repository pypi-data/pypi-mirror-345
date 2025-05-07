from datetime import datetime

import numpy as np

from pyaro.timeseries.Filter import TimeBoundsFilter


def test_timemax():
    bounds = TimeBoundsFilter(
        start_include=[("2023-01-01 00:00:00", "2024-01-01 00:00:00")]
    )

    envelope = bounds.envelope()
    assert envelope[0] == datetime.fromisoformat("2023-01-01 00:00:00")
    assert envelope[1] == datetime.fromisoformat("2024-01-01 00:00:00")

    dt_start = np.arange(
        np.datetime64("2023-01-30"), np.datetime64("2023-03-10"), np.timedelta64(1, "D")
    )
    dt_end = dt_start + np.timedelta64(1, "h")
    idx = bounds.contains(dt_start, dt_end)
    assert len(idx) == len(dt_start)


def test_roundtrip():
    bounds = TimeBoundsFilter(
        start_include=[("2023-01-01 00:00:03", "2024-01-01 00:10:00")]
    )

    init = bounds.init_kwargs()
    assert init["start_include"] == [("2023-01-01 00:00:03", "2024-01-01 00:10:00")]
