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

# Share LAN (same wifi)
envsnap share myapp.envsnap
# Friend runs: envsnap open http://192.168.1.5:8765/<token>

# Share anywhere (different wifi, hostel, mobile data)
envsnap share myapp.envsnap --air
# On Air: 7-purple-sunset — friend runs: envsnap open 7-purple-sunset

# Receiver — friend, fresh laptop
pip install envsnap
envsnap run myapp.envsnap
# extract + Install X? [Y/n] each + launch. That's it.
```

---

## Why envsnap?

| git clone | envsnap run |
|---|---|
| code only | code + versions + system libs + run cmd |
| ModuleNotFoundError | auto-installs missing deps (Y/n each) |
| 3-day onboarding | 40 seconds |
| works on my machine | runs everywhere |

No Dockerfile to write. No YAML. No accounts. Just save / share / run.

## Install

```bash
pip install envsnap
pipx install envsnap
```

Requires Python 3.10+. Linux / Mac / Windows. Check: `envsnap -h`, `envsnap --version`

Air transfer (`--air`) prompts once to install magic-wormhole (~50MB) on first use — base stays light.

## Sender

```bash
cd my-app
envsnap save               # interactive wizard
envsnap save -o demo --yes # non-interactive (CI)
```

Type only a name — `myapp` becomes `myapp.envsnap` automatically. Skips node_modules, venv, .git, restored-app. Never stores secrets — only env key names.

## Receiver

```bash
envsnap open myapp.envsnap --yes                    # safe extract, no install
envsnap run myapp.envsnap                           # extract + auto-install + launch (magic one)
envsnap open http://192.168.1.5:8765/<token> --yes  # from LAN link
envsnap open 7-purple-sunset                         # from Air code
```

`open` = safe peek. `run` = magic (detects OS manager: apt/dnf/pacman/brew/winget/choco/scoop + 15 more, asks Y/n per dep, installs, launches).

Dead link shows a clean "Can't reach sender" message.

## Share (sender-hosted, temp, private)

```bash
envsnap share                        # auto-picks file, LAN link (port 8765)
envsnap share myapp.envsnap --port 9000  # custom port if busy
envsnap share myapp.envsnap --air    # beam anywhere via code (any wifi)
envsnap share myapp.envsnap --relay  # legacy Cloudflare tunnel (needs cloudflared)
```

Unguessable token/code. Ctrl+C kills it. We never store your code.

## Inspect (peek without extracting)

```bash
envsnap inspect myapp.envsnap
```

Shows everything neatly: Env table (OS/python/node/run/env keys), what's missing on YOUR machine + will-install list, full file tree with sizes. Read-only.

## Privacy

- .env values never stored, only key names
- Real secrets block save with skip/cancel choice; test fixtures warn only
- Links/codes are temp + token-guarded, one-shot for air

## Commands

```
envsnap                         menu (all commands)
envsnap save                    snapshot this project
envsnap open <file|url|code>    restore it (safe, no install)
envsnap run <file|url>          restore + auto-install + launch
envsnap share [file]            temp LAN link (Ctrl+C kills)
envsnap share [file] --air      beam anywhere via code
envsnap inspect <file>          full details + tree, no extract
envsnap -h / --help             help
envsnap --version               version
envsnap -v                      verbose
```

## Dev

```bash
git clone https://github.com/xCaptaiN09/envsnap
cd envsnap
pip install -e .
PYTHONPATH=src python3 -m pytest -q
```
