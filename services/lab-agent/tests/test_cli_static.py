from pathlib import Path

from lab_agent.cli import resolve_static_dir


def make_repo(tmp_path: Path) -> Path:
    (tmp_path / "apps" / "robot-console").mkdir(parents=True)
    return tmp_path


def test_default_static_dir_resolves_against_the_repo_root_from_a_subdirectory(tmp_path):
    root = make_repo(tmp_path)
    deep = root / "services" / "lab-agent"
    deep.mkdir(parents=True)
    got = resolve_static_dir("apps/robot-console/dist", [deep])
    assert got == root / "apps" / "robot-console" / "dist"
    assert got.is_absolute()


def test_the_next_start_dir_is_tried_when_the_first_is_outside_the_repo(tmp_path):
    root = make_repo(tmp_path / "repo")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    got = resolve_static_dir("apps/robot-console/dist", [elsewhere, root / "apps"])
    assert got == root / "apps" / "robot-console" / "dist"


def test_an_absolute_path_is_kept_and_an_unfound_repo_gives_an_absolute_path(tmp_path):
    assert resolve_static_dir(str(tmp_path / "x"), [tmp_path]) == tmp_path / "x"
    got = resolve_static_dir("apps/robot-console/dist", [tmp_path])
    assert got.is_absolute() and got.parts[-3:] == ("apps", "robot-console", "dist")
