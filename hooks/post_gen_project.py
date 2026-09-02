"""Strip files the selected options do not use, then make the scaffold commit.
Delete-only by design; all in-file variation lives in Jinja conditionals inside the template."""

import shutil
import subprocess
from pathlib import Path

DATABASE = "{{ cookiecutter.database }}"
SLUG = "{{ cookiecutter.project_slug }}"

# everything that only makes sense with a database; tests/test_bake.py asserts the same list
DB_ONLY = (
    "alembic.ini",
    "migrations",
    "app/db.py",
    "app/models.py",
    "app/schemas.py",
    "app/routers/items.py",
    "tests/conftest.py",
    "tests/test_items.py",
)


def remove(relative: str) -> None:
    path = Path(relative)
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True, text=True)


def scaffold_commit() -> None:
    """One signed-off commit on main; a missing or misconfigured git is a warning, not a failure."""
    try:
        git("init", "-b", "main")
        git("add", "-A")
        git("commit", "--signoff", "-m", "chore: scaffold %s" % SLUG)
    except FileNotFoundError:
        print("WARNING: git not found; initialise the repository by hand")
    except subprocess.CalledProcessError as exc:
        print("WARNING: `git %s` failed; finish repository setup by hand:\n  %s" % (exc.cmd[1], exc.stderr.strip()))


if DATABASE == "none":
    for relative in DB_ONLY:
        remove(relative)

scaffold_commit()
print("Generated %s; see README.md 'One-time setup' for next steps." % SLUG)
