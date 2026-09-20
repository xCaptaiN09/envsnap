### Task 1: Scaffold + CLI skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/envsnap/__init__.py`
- Create: `src/envsnap/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: none
- Produces: `cli.main()` group with save/open/share; `__version__="0.1.0"`

- [ ] Step 1: Write failing test `tests/test_cli.py`:

```python
from click.testing import CliRunner
from envsnap.cli import main
def test_cli_help_lists_save_open_share():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "save" in r.output
    assert "open" in r.output
    assert "share" in r.output
```

- [ ] Step 2: Run `PYTHONPATH=src pytest tests/test_cli.py -v`, expect FAIL (no module).
- [ ] Step 3: Implement pyproject + __init__ + cli.py (click group, 3 stub cmds).
- [ ] Step 4: Run `PYTHONPATH=src pytest tests/test_cli.py -v`, expect PASS.
- [ ] Step 5: Commit `feat: cli skeleton`.

### Task 2: Detectors + scrub

**Files:**
- Create: `src/envsnap/detect.py`
- Test: `tests/test_detect.py`

**Interfaces:**
- Consumes: none
- Produces: `detect_project(root)->dict`, `scrub_value(v)->bool`

- [ ] Step 1: Write failing test:

```python
from envsnap.detect import detect_project, scrub_value
def test_detect_demo(tmp_path):
    (tmp_path/"app.py").write_text("print('hi')")
    d = detect_project(str(tmp_path))
    assert "python" in d and "run" in d
def test_scrub():
    assert scrub_value("AKIA1234567890ABCDEF") is True
    assert scrub_value("hello") is False
```

- [ ] Step 2: Run pytest, expect FAIL.
- [ ] Step 3: Implement detect.py (platform, sys.version, package.json dev script, SECRET_RE).
Also: read `.envsnapignore` if present (one glob per line) + scan `.env` keys into env_template (keys only, values never stored), block secret values via scrub_value.
- [ ] Step 4: Run `PYTHONPATH=src pytest tests/test_detect.py -q`, expect PASS.
- [ ] Step 5: Commit `feat: detectors`.

### Task 3: save pack

**Files:**
- Create: `src/envsnap/pack.py`
- Test: `tests/test_pack.py`

**Interfaces:**
- Consumes: `detect_project(root)->dict`
- Produces: `save_snapshot(root,out)->str` tar.gz with manifest.json + code.tar.gz

- [ ] Step 1: Write failing test:

```python
import tarfile
from envsnap.pack import save_snapshot
def test_save(tmp_path):
    p = tmp_path/"p"; p.mkdir()
    (p/"app.py").write_text("print(1)")
    out = str(tmp_path/"a.envsnap")
    save_snapshot(str(p), out)
    assert "manifest.json" in tarfile.open(out).getnames()
```

- [ ] Step 2: Run pytest, expect FAIL.
- [ ] Step 3: Implement pack.py (SKIP node_modules/.venv/.git/__pycache__ + .envsnapignore globs; refuse to pack if any file value matches scrub_value unless --allow-secrets explicitly passed and still never store .env values).
- [ ] Step 4: Run pytest, expect PASS.
- [ ] Step 5: Commit `feat: save pack`.

### Task 4: open restore

**Files:**
- Create: `src/envsnap/restore.py`
- Test: `tests/test_restore.py`

**Interfaces:**
- Consumes: .envsnap file
- Produces: `inspect_snapshot(path)->dict`, `restore_dry(path,dest)->dict`

- [ ] Step 1: Write failing test:

```python
from envsnap.pack import save_snapshot
from envsnap.restore import inspect_snapshot, restore_dry
def test_open(tmp_path):
    p = tmp_path/"p"; p.mkdir(); (p/"app.py").write_text("print(1)")
    s = save_snapshot(str(p), str(tmp_path/"a.envsnap"))
    assert "python" in inspect_snapshot(s)
    assert restore_dry(s, str(tmp_path/"out"))["ok"] is True
```

- [ ] Step 2: Run pytest, expect FAIL.
- [ ] Step 3: Implement restore.py (read manifest, extract code.tar.gz).
- [ ] Step 4: Run `PYTHONPATH=src pytest -q`, expect PASS all.
- [ ] Step 5: Commit `feat: open restore`.

### Task 5: AI classify + wire CLI

**Files:**
- Create: `src/envsnap/ai.py`
- Modify: `src/envsnap/cli.py`
- Test: `tests/test_ai.py`

**Interfaces:**
- Consumes: save_snapshot, inspect_snapshot
- Produces: `classify(text)->dict` projtype/secret_prob/risk; save -o + open PATH work; share prints V0 stub

Thresholds (enforced in ai.py): SECRET_BLOCK=0.7, RISK_DANGEROUS blocks auto-run.

- [ ] Step 1: Write failing test:

```python
from envsnap.ai import classify
def test_classify():
    r = classify("python app.py + npm run dev")
    assert r["projtype"] in ("python-only","node-only","fullstack-python-node")
```

- [ ] Step 2: Run pytest, expect FAIL.
- [ ] Step 3: Implement ai.py (offline heuristic + TypeSafe if key set, try/except).
- [ ] Step 4: Run `PYTHONPATH=src pytest -q`, expect PASS.
- [ ] Step 5: Commit `feat: ai + cli wire`.

- [ ] Step 1: Write failing test:

```python
from click.testing import CliRunner
from envsnap.cli import main
def test_share_stub(tmp_path):
    r = CliRunner().invoke(main, ["share", str(tmp_path/"a.envsnap")])
    assert r.exit_code == 0
    assert "V0" in r.output or "relay in V0.2" in r.output
```

- [ ] Step 2: Run pytest, expect FAIL.
- [ ] Step 3: Implement share stub in cli.py (no relay yet).
- [ ] Step 4: Run `PYTHONPATH=src pytest -q`, expect PASS.
- [ ] Step 5: Commit `feat: share V0 stub`.

### Task 6: E2E verify

- [ ] Step 1: Run `PYTHONPATH=src pytest -q`, expect 0 failures.
- [ ] Step 2: Live E2E save then inspect on /tmp/envdemo.
- [ ] Step 3: Commit `feat: V0 e2e`.

## Self-Review
- Spec coverage: save/open Tasks 1/3/4/5, share file+direct V0 (relay V0.2).
- Types consistent: detect->dict, save(str,str)->str, inspect(str)->dict.
