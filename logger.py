import logging
import os
import pathlib
import sys


class WorkerLogging:

    __instance = None

    @staticmethod
    def logger():
        if WorkerLogging.__instance is None:
            WorkerLogging()
        return WorkerLogging.__instance

    def __init__(self):
        if WorkerLogging.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            WorkerLogging.__instance = self

        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        home = pathlib.Path.home()
        log_dir = os.path.join(str(home), '.local/share')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'worker.log')

        log_file_handler = logging.FileHandler(log_file)
        log_file_handler.setFormatter(formatter)

        log_stdout_handler = logging.StreamHandler(sys.stdout)

        self.__logger.addHandler(log_file_handler)
        self.__logger.addHandler(log_stdout_handler)

        sys.excepthook = self.exception_handler

    def exception_handler(self, exc_type, exc_value, traceback):
        self.__logger.error('An error occurred', exc_info=(exc_type, exc_value, traceback))

    def info(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.__logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.__logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.__logger.exception(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.__logger.critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.__logger.log(level, msg, *args, **kwargs)
