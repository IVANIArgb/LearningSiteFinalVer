import logging
import logging.handlers
from pathlib import Path


def configure_logging(app) -> None:
    """Configure basic logging for the application."""
    log_dir = Path(app.config.get("PROJECT_ROOT", Path.cwd())) / "backend" / "logs"
    log_file = log_dir / "app.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(console_handler)

    # File handler (best-effort). In read-only environments (like Docker with RO mount),
    # gracefully skip file logging and keep console only.
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(console_formatter)
        root_logger.addHandler(file_handler)
    except OSError:
        # Fall back to console-only logging when filesystem is not writable
        pass




