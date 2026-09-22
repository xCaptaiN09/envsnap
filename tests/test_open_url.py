from click.testing import CliRunner

from envsnap.pack import save_snapshot
from envsnap.cli import main


def test_open_accepts_http_url(tmp_path, monkeypatch):
    import threading
    import time

    from envsnap.share import serve_file

    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    snap = save_snapshot(str(p), str(tmp_path / "a.envsnap"))
    srv, port, token = serve_file(snap, port=0)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        url = f"http://127.0.0.1:{port}/{token}"
        monkeypatch.chdir(tmp_path)
        r = CliRunner().invoke(main, ["open", url, "--yes"])
        assert r.exit_code == 0, r.output
        assert (tmp_path / "restored-app" / "app.py").exists()
    finally:
        srv.shutdown()
