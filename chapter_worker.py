import argparse
import logging
import re
from argparse import Namespace
from pathlib import Path

from process_tools import fix_metadata, split_chapter, convert_to_mp3
from file_utils import init_temp_dir, rm_tree, copy_dir


class ChapterWorker:

    def __init__(self, input_dir, verbose=False):
        self.__ftp_dir = Path(input_dir)
        self.__temp_dir = init_temp_dir()

        self.__chapter_regex = r'_c[\d]+\..*$'

        self.verbose = verbose

    def execute(self):
        logging.debug("Chapter worker started!")

        for src_file in self.__ftp_dir.rglob('*.wav'):

            # Process chapter files only
            if re.search(self.__chapter_regex, str(src_file)):
                # Extract necessary path parts
                root_parts = self.__ftp_dir.parts
                parts = src_file.parts[len(root_parts):]

                lang = parts[0]
                resource = parts[1]
                book = parts[2]
                chapter = parts[3]
                grouping = parts[6]

                target_dir = self.__temp_dir.joinpath(lang, resource, book, chapter, grouping)
                remote_dir = self.__ftp_dir.joinpath(lang, resource, book, chapter, "CONTENTS")
                verses_dir = target_dir.joinpath("verses")
                verses_dir.mkdir(parents=True, exist_ok=True)
                target_file = target_dir.joinpath(src_file.name)

                logging.debug('Found chapter file: {}'.format(src_file))

                # Copy source file to temp dir
                logging.debug('Copying file {} to {}'.format(src_file, target_file))
                target_file.write_bytes(src_file.read_bytes())

                # Try to fix wav metadata
                logging.debug('Fixing metadata: {}'.format(target_file))
                fix_metadata(target_file, self.verbose)

                # Split chapter files into verses
                logging.debug('Splitting chapter {} into {}'.format(target_file, verses_dir))
                split_chapter(target_file, verses_dir, self.verbose)

                # Copy original verse files
                logging.debug(
                    'Copying original verse files from {} into {}'.format(verses_dir, remote_dir)
                )
                copy_dir(verses_dir, remote_dir)

                # Convert chapter into mp3
                logging.debug('Converting chapter: {}'.format(target_file))
                convert_to_mp3(target_file, self.verbose)

                # Convert verses into mp3
                logging.debug('Converting verses in {}'.format(verses_dir))
                convert_to_mp3(verses_dir, self.verbose)

                # Copy converted chapter file
                logging.debug(
                    'Copying chapter mp3 from {} into {}'.format(target_dir, remote_dir)
                )
                copy_dir(target_dir, remote_dir, grouping)

                # Copy converted verse files
                logging.debug(
                    'Copying verses mp3 from {} into {}'.format(verses_dir, remote_dir)
                )
                copy_dir(verses_dir, remote_dir)

        logging.debug('Deleting temporary directory: {}'.format(self.__temp_dir))
        rm_tree(self.__temp_dir)

        logging.debug('Chapter worker finished!')


def get_arguments() -> Namespace:
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(description='Split and convert chapter files to mp3')
    parser.add_argument('-i', '--input-dir', help='Input directory')
    parser.add_argument("--trace", action="store_true", help="Enable tracing output")
    parser.add_argument("--verbose", action="store_true", help="Enable logs from subprocess")

    return parser.parse_args()


def main():
    """ Run chapter worker """
    args = get_arguments()

    if args.trace:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)

    worker = ChapterWorker(args.input_dir, args.verbose)
    worker.execute()


if __name__ == "__main__":
    main()
