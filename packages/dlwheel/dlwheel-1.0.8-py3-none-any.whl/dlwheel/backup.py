import zipfile
from pathlib import Path

import yaml
from pathspec import GitIgnoreSpec


class BackupSystem:

    def __init__(self, cfg):
        self.cfg = cfg
        log_path = cfg.path.log if cfg.path and cfg.path.log else f"log"
        self.backup_dir = Path(log_path) / cfg.name

    def run(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._create_backup_zip()

    def _load_gitignore(self) -> GitIgnoreSpec:
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            return GitIgnoreSpec([])
        with gitignore_path.open("r") as f:
            return GitIgnoreSpec.from_lines(f)

    def _should_ignore(self, path: Path, spec: GitIgnoreSpec) -> bool:
        git_style_path = path.relative_to(Path.cwd()).as_posix()
        if path.is_dir():
            git_style_path += "/"
        return spec.match_file(git_style_path)

    def _create_backup_zip(self):
        ignore_spec = self._load_gitignore()
        backup_abs = self.backup_dir.resolve()
        zip_path = self.backup_dir / "backup.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in Path.cwd().rglob("*"):
                item_abs = item.resolve()
                if item_abs == backup_abs or backup_abs in item_abs.parents:
                    continue
                if self._should_ignore(item, ignore_spec):
                    continue
                if item.is_dir():
                    continue
                arcname = item.relative_to(Path.cwd())
                zipf.write(item, arcname)

            config_content = yaml.dump(self.cfg.to_dict())
            zipf.writestr(str(self.cfg.config), config_content)
