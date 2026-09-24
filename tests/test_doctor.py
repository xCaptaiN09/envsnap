from envsnap import doctor
from envsnap.doctor import MGRS, detect_manager


def test_manager_table_complete():
    names = [m for _, m in MGRS]
    for want in ("apt", "dnf", "pacman", "apk", "brew", "winget", "choco", "scoop"):
        assert want in names


def test_detect_returns_str_or_none():
    assert detect_manager() is None or isinstance(detect_manager(), str)


def test_plan_missing_lists_items():
    plan = doctor.plan_missing({"python": "3.10.0", "node": "v18.0.0", "pip_packages": ["fastapi==0.1"]})
    assert any("python" in p["name"].lower() or "node" in p["name"].lower() for p in plan)
