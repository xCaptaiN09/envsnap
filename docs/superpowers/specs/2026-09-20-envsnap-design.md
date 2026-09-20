# EnvSnap Design Spec — 2026-09-20

## Goal
One-command snapshot + restore of a dev project's runnable env. Beginner: `save` / `open` / `share`.

## Commands (only 3)
- `envsnap save [-o file.envsnap]` — scan + pack local file. Interactive by default.
- `envsnap open <file|link>` — verify + install + prompt secrets + run.
- `envsnap share [file]` — temp sender-hosted link, auto direct→relay, close=dead.
- Bare `envsnap` — interactive menu.

## .envsnap format (tar.gz)
- `manifest.json` — os, arch, python/node versions, apt list, db info, run cmds, env-template keys only
- `code.tar.gz` — project code minus node_modules, venv, .git, __pycache__ via .envsnapignore
- `requirements.txt` / `package-lock` copy, `apt.txt`, `db.sql.gz` (opt-in), `setup.sh` (generated)
- Secrets: never store values. Only `KEY=<ask>` template. Block on `AKIA|sk-|ghp_|BEGIN PRIVATE`.

## Detectors (V0)
- os.py: /etc/os-release, uname -m, apt/dpkg, which gcc/ffmpeg
- python.py: version, pip freeze, poetry.lock, venv name
- node.py: node -v, package.json scripts, lockfile
- db.py: ports 5432/6379/27017, pg_dump schema only by default
- run.py: entrypoints app.py/server.js/main.py + package.json/Procfile/Makefile/README → run cmd

## Sharing (approved 3-path, 1 UX)
1. File: Telegram/Drive/pendrive
2. Direct P2P temp link (same wifi/LAN)
3. Relay via Cloudflare tunnel when NAT blocks
- UX: `share` auto-picks 2→3, shows one link + QR, unguessable token, close=dead, no central storage.

## TypeSafe (code owns workflow, 3 narrow judgments)
- Choice `projtype`: python-only | node-only | fullstack-python-node → picks detector set
- Noul `has_secret`: yes-prob → block + scrub
- Score `risk`: safe | needs-check | dangerous → gate auto-run
- Ask together in one `system_one` call. Thresholds in code. Key server-side only.

## UX rules
- pip install envsnap only. Rich colors, checkmarks, progress, plain English errors + [Auto-fix?]
- Autonomous: detect, skip junk, scrub, gen setup.sh/Dockerfile, install, seed DB, run, open browser
- Native restore default. `--docker` fallback on OS/arch mismatch.

## V0 scope (locked)
- Local save/open file only + sender-hosted share. No central DB. No login.
- Runtimes: Python + Node + apt + Postgres-schema. No full DB data by default.
- Tests: pytest, TDD red-green, `pytest -q` must pass before claim.

## Out of scope V0
- Permanent links, private teams, deploy-to-cloud, VSCode ext, diff cmd → V1.
