from fspacker.settings import get_settings
from fspacker.trackers import perf_tracker
from fspacker.trackers import PerformanceTracker


def test_perf_tracker(caplog):
    get_settings().mode.debug = True

    @perf_tracker
    def fabonacci(n: int) -> int:
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return b

    assert 144 == fabonacci(10)
    PerformanceTracker.finalize()

    assert "统计" in caplog.text
    assert "总运行时间:" in caplog.text


def test_perf_tracker_no_debug(caplog):
    get_settings().mode.debug = False

    @perf_tracker
    def fabonacci(n: int) -> int:
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return b

    assert 144 == fabonacci(10)
    assert "总运行时间:" not in caplog.text
