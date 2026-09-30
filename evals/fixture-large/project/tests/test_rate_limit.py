from linkcrawl.net.rate_limit import HostRateLimiter, TokenBucket


class ManualClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_bucket_allows_burst_then_waits():
    clock = ManualClock()
    bucket = TokenBucket(rate=2.0, burst=2, clock=clock)
    bucket.take()
    bucket.take()
    assert bucket.wait_time() == 0.5


def test_limiter_sleeps_per_host():
    clock = ManualClock()
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        clock.now += seconds

    limiter = HostRateLimiter(rate=1.0, burst=1, clock=clock, sleep=sleep)
    limiter.acquire("https://a.example/1")
    limiter.acquire("https://b.example/1")
    limiter.acquire("https://a.example/2")
    assert sleeps == [1.0]
    assert limiter.total_wait == 1.0


def test_zero_rate_disables_limiting():
    def never(seconds):
        raise AssertionError("a disabled limiter must not sleep")

    limiter = HostRateLimiter(rate=0.0, burst=1, sleep=never)
    assert limiter.enabled is False
    for _ in range(10):
        assert limiter.acquire("https://a.example/") == 0.0


def test_crawl_delay_raises_min_interval():
    clock = ManualClock()
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        clock.now += seconds

    limiter = HostRateLimiter(rate=10.0, burst=10, clock=clock, sleep=sleep)
    limiter.set_min_interval("https://a.example/", 3.0)
    limiter.acquire("https://a.example/1")
    limiter.acquire("https://a.example/2")
    assert sleeps == [3.0]
