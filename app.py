import argparse
import logging
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Tuple, List

from chapter_worker import ChapterWorker
from tr_worker import TrWorker
from verse_worker import VerseWorker


class App:

    def __init__(self, input_dir, verbose=False, hour=0, minute=0):
        self.__ftp_dir = Path(input_dir)
        self.verbose = verbose
        self.hour = hour
        self.minute = minute

        self.sleep_timer = 60

    def start(self):
        """ Start app """

        chapter_worker = ChapterWorker(self.__ftp_dir, self.verbose)
        verse_worker = VerseWorker(self.__ftp_dir, self.verbose)
        tr_worker = TrWorker(self.__ftp_dir, self.verbose)

        while True:
            now = datetime.now()
            midnight = now.replace(hour=self.hour, minute=self.minute, second=0)
            seconds_since_midnight = (now - midnight).total_seconds()

            logging.debug(seconds_since_midnight)

            if 0 <= seconds_since_midnight < self.sleep_timer:
                chapter_worker.execute()
                verse_worker.execute()
                tr_worker.execute()

            sleep(self.sleep_timer)


def get_arguments() -> Tuple[Namespace, List[str]]:
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(description='Split and convert chapter files to mp3')
    parser.add_argument('-i', '--input-dir', help='Input directory')
    parser.add_argument("-t", "--trace", action="store_true", help="Enable tracing output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable logs from subprocess")
    parser.add_argument("-hr", "--hour", type=int, default=0, help="Hour, when to execute workers")
    parser.add_argument("-mn", "--minute", type=int, default=0, help="Minute, when to execute workers")

    return parser.parse_known_args()


def main():
    """ Launch application """

    args, unknown = get_arguments()

    if args.trace:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)

    app = App(args.input_dir, args.verbose, args.hour, args.minute)
    app.start()


if __name__ == "__main__":
    main()
