import argparse
import logging
import re
from argparse import Namespace
from pathlib import Path

from file_utils import init_temp_dir, rm_tree, copy_file
from process_tools import fix_metadata, convert_to_mp3


class VerseWorker:

    def __init__(self, input_dir, verbose=False):
        self.__ftp_dir = Path(input_dir)
        self.__temp_dir = init_temp_dir()

        self.__verse_regex = r'_c[\d]+_v[\d]+(?:-[\d]+)?(?:_t[\d]+)?\..*$'

        self.verbose = verbose

    def execute(self):
        logging.debug("Verse worker started!")

        for src_file in self.__ftp_dir.rglob('*.wav'):
            # Process verse/chunk files only
            if not re.search(self.__verse_regex, str(src_file)):
                continue

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
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir.joinpath(src_file.name)

            logging.debug(f'Found verse file: {src_file}')

            # Copy source file to temp dir
            logging.debug(f'Copying file {src_file} to {target_file}')
            target_file.write_bytes(src_file.read_bytes())

            # Try to fix wav metadata
            logging.debug(f'Fixing metadata: {target_file}')
            fix_metadata(target_file, self.verbose)

            # Convert verse into mp3
            logging.debug(f'Converting verse: {target_file}')
            convert_to_mp3(target_file, self.verbose)

            # Copy converted verse file (mp3 and cue)
            mp3_file = target_file.with_suffix('.mp3')
            logging.debug(
                f'Copying verse mp3 {mp3_file} into {remote_dir}'
            )
            if mp3_file.exists():
                copy_file(mp3_file, remote_dir, grouping)

            cue_file = target_file.with_suffix('.cue')
            logging.debug(
                f'Copying verse cue {cue_file} into {remote_dir}'
            )
            if cue_file.exists():
                copy_file(cue_file, remote_dir, grouping)

        logging.debug(f'Deleting temporary directory {self.__temp_dir}')
        rm_tree(self.__temp_dir)

        logging.debug('Verse worker finished!')


def get_arguments() -> Namespace:
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(description='Convert verse files to mp3')
    parser.add_argument('-i', '--input-dir', help='Input directory')
    parser.add_argument("--trace", action="store_true", help="Enable tracing output")
    parser.add_argument("--verbose", action="store_true", help="Enable logs from subprocess")

    return parser.parse_args()


def main():
    """ Run verse worker """
    args = get_arguments()

    if args.trace:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)

    worker = VerseWorker(args.input_dir, args.verbose)
    worker.execute()


if __name__ == "__main__":
    main()
