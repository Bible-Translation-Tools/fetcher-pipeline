import os
import re
import shutil

from argv_parser import ArgvParser
from logger import WorkerLogging
from process_tools import ProcessTools
from temp_dir import init_temp_dir


class VerseWorker:

    def __init__(self):
        self.__ftp_dir = None
        self.__temp_dir = init_temp_dir()

        self.__wav_regex = r'\/[\d]+\/CONTENTS\/wav\/(?:verse|chunk)'
        self.__verse_wav_regex = r'_c[\d]+_v[\d]+(?:-[\d]+)?(?:_t[\d]+)?\..*$'
        self.__dir_wav_regex = r'^.*\/(.*)\/(.*)\/(.*)\/([\d]+)\/CONTENTS\/wav\/(verse|chunk)'

        argv_parser = ArgvParser()
        self.__ftp_dir = argv_parser.get_ftp_dir()

        self.__logger = WorkerLogging.logger()
        self.__process_tools = ProcessTools()

    def execute(self):
        self.__logger.info("Verse worker started!")

        for root, dirs, files in os.walk(self.__ftp_dir):
            for file in files:
                if re.search(self.__wav_regex, root):
                    src_file = os.path.join(root, file)

                    # Process verse/chunk files only
                    if re.search(self.__verse_wav_regex, src_file):
                        # Extract necessary path parts
                        match = re.match(self.__dir_wav_regex, src_file)
                        if match:
                            lang = match.group(1)
                            resource = match.group(2)
                            book = match.group(3)
                            chapter = match.group(4)
                            grouping = match.group(5)

                            target_dir = os.path.join(self.__temp_dir, lang, resource, book, chapter, grouping)
                            remote_dir = os.path.join(self.__ftp_dir, lang, resource, book, chapter, "CONTENTS")
                            os.makedirs(target_dir, exist_ok=True)
                            target_file = os.path.join(target_dir, file)

                            self.__logger.info('Found verse file: ' + src_file)

                            # Copy source file to temp dir
                            self.__logger.info('Copying file ' + src_file + ' to ' + target_file)
                            shutil.copy2(src_file, target_file)

                            # Try to fix wav metadata
                            self.__logger.info('Fixing metadata: ' + target_file)
                            self.__process_tools.fix_metadata(target_file)

                            # Convert verse into mp3
                            self.__logger.info('Converting verse: ' + target_file)
                            self.__process_tools.convert_to_mp3(target_file)

                            # Copy converted verse file
                            self.__logger.info(
                                'Copying verse mp3 from ' + target_dir + ' into ' + remote_dir
                            )
                            self.__process_tools.copy_file(target_dir, remote_dir, grouping)

        self.__logger.info('Deleting temporary directory: ' + self.__temp_dir)
        shutil.rmtree(self.__temp_dir)

        self.__logger.info('Verse worker finished!')


worker = VerseWorker()
worker.execute()
