from envsnap.beam import ensure_wormhole, is_code


def test_is_code():
    assert is_code("7-purple-sunset") is True
    assert is_code("myapp.envsnap") is False
    assert is_code("http://x/y") is False


def test_ensure_present_noop():
    # wormhole installed in dev env — should not raise
    ensure_wormhole()
