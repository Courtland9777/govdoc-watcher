import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def configure_logging(level: str) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    fh = RotatingFileHandler('/logs/govdoc-watcher.log', maxBytes=1_000_000, backupCount=5)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
