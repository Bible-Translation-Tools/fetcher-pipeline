import argparse
import logging
import re
from argparse import Namespace
from pathlib import Path
from typing import Tuple, List

from process_tools import fix_metadata, split_chapter, convert_to_mp3
from file_utils import init_temp_dir, rm_tree, copy_dir, check_file_exists, copy_file


class ChapterWorker:

    def __init__(self, input_dir, verbose=False):
        self.__ftp_dir = Path(input_dir)
        self.__temp_dir = init_temp_dir()

        self.__chapter_regex = r'_c[\d]+\..*$'

        self.verbose = verbose

    def execute(self):
        """ Execute worker """

        logging.debug("Chapter worker started!")

        for src_file in self.__ftp_dir.rglob('*.wav'):
            # Process chapter files only
            if not re.search(self.__chapter_regex, str(src_file)):
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
            verses_dir = target_dir.joinpath("verses")
            verses_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir.joinpath(src_file.name)

            logging.debug(f'Found chapter file: {src_file}')

            # Copy source file to temp dir
            logging.debug(f'Copying file {src_file} to {target_file}')
            target_file.write_bytes(src_file.read_bytes())

            # Try to fix wav metadata
            logging.debug(f'Fixing metadata: {target_file}')
            fix_metadata(target_file, self.verbose)

            # Split chapter files into verses
            logging.debug(f'Splitting chapter {target_file} into {verses_dir}')
            split_chapter(target_file, verses_dir, self.verbose)

            # Copy original verse files
            logging.debug(
                f'Copying original verse files from {verses_dir} into {remote_dir}'
            )
            copy_dir(verses_dir, remote_dir)

            # Convert chapter into mp3
            self.convert_chapter(target_file, remote_dir, grouping)

            # Convert verses into mp3
            self.convert_verses(verses_dir, remote_dir)

        logging.debug(f'Deleting temporary directory {self.__temp_dir}')
        rm_tree(self.__temp_dir)

        logging.debug('Chapter worker finished!')

    def convert_chapter(self, chapter_file: Path, remote_dir: Path, grouping: str):
        """ Convert chapter wav file and copy to remote directory"""

        # Check if filed exist remotely
        chapter_mp3_exists = check_file_exists(chapter_file, remote_dir, 'mp3', grouping)
        chapter_cue_exists = check_file_exists(chapter_file, remote_dir, 'cue', grouping)

        if not chapter_mp3_exists and not chapter_cue_exists:
            logging.debug(f'Converting chapter: {chapter_file}')
            convert_to_mp3(chapter_file, self.verbose)

            # Copy converted chapter files
            mp3_file = chapter_file.with_suffix('.mp3')
            if mp3_file.exists():
                logging.debug(
                    f'Copying chapter mp3 {mp3_file} into {remote_dir}'
                )
                copy_file(mp3_file, remote_dir, grouping)

            cue_file = chapter_file.with_suffix('.cue')
            if cue_file.exists():
                logging.debug(
                    f'Copying chapter cue {cue_file} into {remote_dir}'
                )
                copy_file(cue_file, remote_dir, grouping)
        else:
            logging.debug('Files exist. Skipping...')

    def convert_verses(self, verses_dir: Path, remote_dir: Path):
        """ Convert verse wav file and copy to remote directory """

        for f in verses_dir.iterdir():
            if f.is_dir():
                continue

            mp3_exists = check_file_exists(f, remote_dir, 'mp3')
            cue_exists = check_file_exists(f, remote_dir, 'cue')

            if mp3_exists or cue_exists:
                logging.debug('Files exist. Skipping...')
                continue

            logging.debug(f'Converting file: {f}')
            convert_to_mp3(f, self.verbose)

            # Copy converted verse files
            mp3_file = f.with_suffix('.mp3')
            if mp3_file.exists():
                logging.debug(
                    f'Copying verse mp3 {mp3_file} into {remote_dir}'
                )
                copy_file(mp3_file, remote_dir)

            cue_file = f.with_suffix('.cue')
            if cue_file.exists():
                logging.debug(
                    f'Copying verse cue {mp3_file} into {remote_dir}'
                )
                copy_file(cue_file, remote_dir)


def get_arguments() -> Tuple[Namespace, List[str]]:
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(description='Split and convert chapter files to mp3')
    parser.add_argument('-i', '--input-dir', help='Input directory')
    parser.add_argument("--trace", action="store_true", help="Enable tracing output")
    parser.add_argument("--verbose", action="store_true", help="Enable logs from subprocess")

    return parser.parse_known_args()


def main():
    """ Run chapter worker """

    args, unknown = get_arguments()

    if args.trace:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)

    worker = ChapterWorker(args.input_dir, args.verbose)
    worker.execute()


if __name__ == "__main__":
    main()
