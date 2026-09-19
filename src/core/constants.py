from pathlib import Path

# Root of the cloned repo (resolved from this file's location, so the repo can
# live anywhere on disk, not only at ~/.config).
path_repo = Path(__file__).resolve().parents[2]

# Repo-local paths (sources shipped with the repository).
path_resources = path_repo / "resources"
path_config_files = path_resources / "config_files"
path_scripts = path_repo / "scripts"
path_logs = path_repo / "logs"

# Config privada (gitignoreada): datos del trabajo que no se versionan.
path_private = path_repo / "private"

# Artefactos generados en runtime (no versionados, fuera del repo).
path_cache = Path.home() / ".cache" / "dotfiles"

# System destination for program dotfiles.
path_home = Path.home()
path_dotfiles = path_home / ".config"

path_screenshots = path_home / "images" / "screenshots"
