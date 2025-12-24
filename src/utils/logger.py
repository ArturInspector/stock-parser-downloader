import logging
import sys
from pathlib import Path

def setup_logger():
    logger = logging.getLogger("StockParser")
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    file_path = Path("app.log")
    fh = logging.FileHandler(file_path, encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

logger = setup_logger()
