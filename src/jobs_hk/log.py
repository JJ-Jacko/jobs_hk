"""Logging utils"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime as DateTime


_formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def get_logger(
        name: str,
        console: bool = True,
        file: bool = True
):
    """
    Args:
        console: output to console 输出到控制台
        file: output to file 输出到文件
    """
    
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}_{DateTime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log"
    file_handler = logging.handlers.RotatingFileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if console:
        logger.addHandler(console_handler)
    if file:
        logger.addHandler(file_handler)
    
    return logger