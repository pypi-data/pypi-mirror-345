import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class LoggerHandler:
    def __init__(self, logger):
        self.logger = logger
        self.level_dict = {
            "i": (self.logger.info, "INFO"),
            "e": (self.logger.error, "ERROR"),
            "d": (self.logger.debug, "DEBUG"),
            "w": (self.logger.warning, "WARNING"),
            "c": (self.logger.critical, "CRITICAL")
        }

    def info(self, msg: str):
        msg = f"{' ' * 10}{msg}"
        self.logger.info(msg)

    def error(self, msg: str):
        msg = f"{' ' * 10}{msg}"
        self.logger.error(msg)

    def debug(self, msg: str):
        msg = f"{' ' * 10}{msg}"
        self.logger.debug(msg)

    def warning(self, msg: str):
        msg = f"{' ' * 10}{msg}"
        self.logger.warning(msg)

    def critical(self, msg: str):
        msg = f"{' ' * 10}{msg}"
        self.logger.critical(msg)


def setup_logger(name: str, log_dir: str = "logs") -> LoggerHandler:
    Path(log_dir).mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 文件日志 (按天切割)
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        when="midnight",
        backupCount=7
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return LoggerHandler(logger)


BASE_LOGGER = setup_logger(f"global_WorkFlow_StepAction")