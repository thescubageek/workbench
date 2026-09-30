from linkcrawl.core.result import LinkStatus, ResultSource, broken_result, ok_result
from linkcrawl.store.cache import CACHE_FORMAT_VERSION, ResultCache
from linkcrawl.store.json_store import JsonStore, MemoryStore

URL = "https://example.com/page"


def test_fresh_entry_is_returned_from_cache(clock):
    cache = ResultCache(MemoryStore(), ttl_seconds=60, clock=clock)
    cache.put(ok_result(URL, 200, checked_at=clock.now()))
    clock.advance(59)
    cached = cache.get(URL)
    assert cached is not None
    assert cached.source is ResultSource.CACHE


def test_entry_expires_at_ttl(clock):
    cache = ResultCache(MemoryStore(), ttl_seconds=60, clock=clock)
    cache.put(ok_result(URL, 200, checked_at=clock.now()))
    clock.advance(60)
    assert cache.get(URL) is None
    assert cache.expired == 1


def test_broken_results_are_not_cached(clock):
    cache = ResultCache(MemoryStore(), ttl_seconds=60, clock=clock)
    assert cache.put(broken_result(URL, "HTTP 404", 404)) is False
    assert cache.get(URL) is None


def test_zero_ttl_disables_cache(clock):
    cache = ResultCache(MemoryStore(), ttl_seconds=0, clock=clock)
    assert cache.put(ok_result(URL, 200)) is False
    assert cache.enabled is False


def test_recheck_within_ttl_skips_network(make_components, clock):
    components = make_components(routes={URL: (200, {}, b"")}, respect_robots=False,
                                 cache_ttl=300)
    first = components.checker.check(URL)
    clock.advance(100)
    second = components.checker.check(URL)
    assert first.source is ResultSource.NETWORK
    assert second.source is ResultSource.CACHE
    assert second.status is LinkStatus.OK
    assert components.opener.count(URL) == 1


def test_recheck_after_ttl_goes_to_network(make_components, clock):
    components = make_components(routes={URL: (200, {}, b"")}, respect_robots=False,
                                 cache_ttl=300)
    components.checker.check(URL)
    clock.advance(301)
    assert components.checker.check(URL).source is ResultSource.NETWORK
    assert components.opener.count(URL) == 2


def test_flush_writes_versioned_file(tmp_path, clock):
    path = tmp_path / "cache.json"
    cache = ResultCache(JsonStore(str(path)), ttl_seconds=60, clock=clock)
    cache.put(ok_result(URL, 200, checked_at=clock.now()))
    cache.flush()
    data = JsonStore(str(path)).load()
    assert data["version"] == CACHE_FORMAT_VERSION
    reloaded = ResultCache(JsonStore(str(path)), ttl_seconds=60, clock=clock)
    assert reloaded.get(URL) is not None
