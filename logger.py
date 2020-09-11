import logging
import os
import pathlib
import sys


class WorkerLogging:

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        home = pathlib.Path.home()
        log_dir = os.path.join(str(home), '.local/share')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'worker.log')

        log_file_handler = logging.FileHandler(log_file)
        log_file_handler.setFormatter(formatter)

        log_stdout_handler = logging.StreamHandler(sys.stdout)

        self.logger.addHandler(log_file_handler)
        self.logger.addHandler(log_stdout_handler)

        sys.excepthook = self.exception_handler

    def exception_handler(self, exc_type, exc_value, traceback):
        self.logger.error('An error occurred', exc_info=(exc_type, exc_value, traceback))
