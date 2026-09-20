# envsnap

Snapshot any dev env into one shareable file. Stop saying “works on my machine.”

```bash
pip install envsnap

# creator
cd my-app
envsnap save -o my-app.envsnap
# → send file via Telegram / Drive

# friend
envsnap open my-app.envsnap
```

- V0: local save/open + file share. Relay temp links in V0.2.
- Never stores secret values — only env key names.
- Tests: `PYTHONPATH=src python3 -m pytest -q`
