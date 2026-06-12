import logging
import shutil
from pathlib import Path

from app.services.config import RuleConfig

logger = logging.getLogger("risk_log_rotation")


def rotate_log_if_needed(log_file: Path) -> None:
    if not log_file.exists():
        return

    cfg = RuleConfig.get().get_log()
    max_size_mb = cfg.get("max_file_size_mb", 50)
    max_backups = cfg.get("max_backup_count", 5)

    file_size_mb = log_file.stat().st_size / (1024 * 1024)
    if file_size_mb < max_size_mb:
        return

    for i in range(max_backups - 1, 0, -1):
        src = Path(f"{log_file}.{i}")
        dst = Path(f"{log_file}.{i + 1}")
        if src.exists():
            shutil.move(str(src), str(dst))

    backup_path = Path(f"{log_file}.1")
    shutil.move(str(log_file), str(backup_path))
    logger.info("决策日志已轮转: %s → %s (大小: %.1fMB)", log_file, backup_path, file_size_mb)

    for i in range(max_backups + 1, max_backups + 10):
        old = Path(f"{log_file}.{i}")
        if old.exists():
            old.unlink()
        else:
            break