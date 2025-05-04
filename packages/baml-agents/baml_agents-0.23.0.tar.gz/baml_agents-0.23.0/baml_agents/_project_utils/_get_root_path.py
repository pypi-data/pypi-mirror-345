import pathlib


def get_root_path():
    root_path = next(
        (
            str(p)
            for p in [
                pathlib.Path.cwd().resolve(),
                *list(pathlib.Path.cwd().resolve().parents),
            ]
            if (p / "pyproject.toml").is_file()
        ),
        None,
    )
    if root_path is None:
        raise FileNotFoundError(
            "Could not find pyproject.toml in current or parent directories"
        )
    return root_path

