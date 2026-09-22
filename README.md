# 📦 envsnap

**Stop saying "works on my machine."**

One command to snapshot your entire dev environment. One command for anyone to run it *exactly* the same.

```bash
pip install envsnap

# Sender — you, where it works
cd my-cool-app
envsnap save
# Snapshot name [my-cool-app]: myapp
# Saved -> myapp.envsnap — send it or run share

# Share — pick one
envsnap share myapp.envsnap
# Friend runs: envsnap open http://192.168.1.5:8765/<token>
# (keep terminal open — Ctrl+C kills the link, nothing stored anywhere)

# Receiver — friend, fresh laptop
pip install envsnap
envsnap open myapp.envsnap --yes
# Restored -> restored-app/ — next: cd restored-app && ./setup.sh
```

---

## Why envsnap?

| git clone | envsnap open |
|---|---|
| code only | code + versions + system libs + run cmd |
| ModuleNotFoundError | auto setup.sh installs it |
| 3-day onboarding | 40 seconds |
| works on my machine | runs everywhere |

No Dockerfile to write. No YAML. No accounts. Just save / open / share.

## Install

```bash
pip install envsnap
pipx install envsnap
```

Requires Python 3.10+. Linux / Mac / Windows. Check: `envsnap -h`, `envsnap --version`

## Sender

```bash
cd my-app
envsnap save               # interactive wizard
envsnap save -o demo --yes # non-interactive (CI)
```

Type only a name — `myapp` becomes `myapp.envsnap` automatically. Skips node_modules, venv, .git. Never stores secrets — only env key names.

## Receiver

```bash
envsnap open myapp.envsnap --yes                 # from file
envsnap open http://192.168.1.5:8765/<token> --yes  # from live link
```

Verifies, asks env keys privately, extracts to restored-app/ + writes setup.sh. Dead link shows a clean "Can't reach sender" message.

## Share (sender-hosted, temp, private)

```bash
envsnap share                      # auto-picks the .envsnap file
envsnap share myapp.envsnap --relay  # far-away NAT (needs cloudflared)
```

Direct P2P on LAN, relay via Cloudflare when blocked. Unguessable token. Ctrl+C kills it. We never store your code.

## Privacy

- .env values never stored, only key names
- Real secrets block save with skip/cancel choice; test fixtures warn only
- Links are temp + token-guarded

## Commands

```
envsnap                 interactive menu
envsnap save            snapshot this project
envsnap open <file|url> restore it
envsnap share [file]    temp link (Ctrl+C kills)
envsnap -h / --help     help
envsnap --version       version
envsnap -v              verbose
```

## Dev

```bash
git clone https://github.com/xCaptaiN09/envsnap
cd envsnap
pip install -e .
PYTHONPATH=src python3 -m pytest -q
```
