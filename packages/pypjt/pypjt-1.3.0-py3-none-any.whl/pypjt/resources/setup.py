from pathlib import Path

from setuptools import setup

PROJECT_DIR = Path(__file__).resolve().parent


def get_requires() -> dict[str, list[str]]:
    requirements_dir = PROJECT_DIR / "requirements"

    base = []
    for line in (requirements_dir / "base.txt").read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if line and not line.startswith("-r"):
            base.append(line)

    prod = []
    for line in (requirements_dir / "prod.txt").read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if line and not line.startswith("-r") and line not in base:
            prod.append(line)

    dev = []
    for line in (requirements_dir / "dev.txt").read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if line and not line.startswith("-r") and line not in base and line not in prod:
            dev.append(line)

    return {"base": base, "prod": prod, "dev": dev}


requires = get_requires()

setup(
    install_requires=requires["base"],
    extras_require={
        "dev": requires["dev"],
        "prod": requires["prod"],
    },
)
