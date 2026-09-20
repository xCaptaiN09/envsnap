"""TypeSafe classify — offline heuristic + live judgments if key set."""
SECRET_BLOCK = 0.7

VALID = ("python-only", "node-only", "fullstack-python-node")


def _heuristic(text: str) -> dict:
    t = (text or "").lower()
    has_py = "python" in t or "app.py" in t
    has_no = "npm" in t or "node" in t or "package.json" in t
    if has_py and has_no:
        proj = "fullstack-python-node"
    elif has_no:
        proj = "node-only"
    else:
        proj = "python-only"
    return {"projtype": proj, "secret_prob": 0.0, "risk": "safe"}


def classify(text: str) -> dict:
    try:
        import os

        if os.getenv("TYPESAFE_API_KEY"):
            from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

            with TypeSafeClient() as c:
                r = c.system_one(
                    state={"text": text},
                    questions={
                        "p": Choice(
                            instructions="Project type?",
                            criteria={
                                "python-only": None,
                                "node-only": None,
                                "fullstack-python-node": None,
                            },
                        ),
                        "s": Noul(instructions="Contains real secret?"),
                        "k": Score(
                            instructions="Risk?",
                            criteria=["safe", "needs-check", "dangerous"],
                        ),
                    },
                )
                return {
                    "projtype": r.choices["p"].choice,
                    "secret_prob": float(r.nouls["s"].noul),
                    "risk": r.scores["k"].score,
                }
    except Exception:
        pass
    return _heuristic(text)
