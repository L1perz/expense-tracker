"""Обновление существующей базы не должно терять записи и права доступа."""

import os
import subprocess
import sys
from pathlib import Path


def test_split_apps_preserves_data_permissions_and_can_roll_back(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "tests" / "migration_probe.py")],
        cwd=root,
        env={
            **os.environ,
            "DJANGO_DB_PATH": str(tmp_path / "upgrade.sqlite3"),
            "DJANGO_DEBUG_TOOLBAR": "0",
            "PYTHONUTF8": "1",
        },
        capture_output=True,
        text=True,
        encoding="utf8",
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"rollback": "ok"' in result.stdout
