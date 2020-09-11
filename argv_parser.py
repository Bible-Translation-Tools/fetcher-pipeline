import getopt
import sys

from logger import WorkerLogging


class ArgvParser:

    def __init__(self):
        self.__ftp_dir = None
        logger = WorkerLogging().logger
        usage_message = 'Usage: chapter_worker.py -f <ftp_dir>'

        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hf:', ["ftp-dir="])
        except getopt.GetoptError:
            logger.info(usage_message)
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                logger.info(usage_message)
                sys.exit()
            elif opt in ('-f', '--ftp-dir'):
                self.__ftp_dir = arg

        if self.__ftp_dir is None or len(self.__ftp_dir) == 0:
            logger.info(usage_message)
            sys.exit(2)

    def get_ftp_dir(self):
        return self.__ftp_dir
