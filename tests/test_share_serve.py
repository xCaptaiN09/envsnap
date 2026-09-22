import threading
import urllib.request

from envsnap.pack import save_snapshot
from envsnap.share import serve_file


def test_share_serves_file(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    snap = save_snapshot(str(p), str(tmp_path / "a.envsnap"))
    srv, port, token = serve_file(snap, port=0)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        url = f"http://127.0.0.1:{port}/{token}"
        with urllib.request.urlopen(url, timeout=5) as r:
            assert r.status == 200
            assert len(r.read()) > 100
        # wrong token → 404
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/wrong", timeout=5)
            assert False, "should 404"
        except urllib.error.HTTPError as e:
            assert e.code == 404
    finally:
        srv.shutdown()
