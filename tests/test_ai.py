from envsnap.ai import classify


def test_classify():
    r = classify("python app.py + npm run dev")
    assert r["projtype"] in ("python-only", "node-only", "fullstack-python-node")
