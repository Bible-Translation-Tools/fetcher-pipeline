import os
import re
import shutil

from argv_parser import ArgvParser
from logger import WorkerLogging
from process_tools import ProcessTools
from temp_dir import init_temp_dir


class ChapterWorker:

    def __init__(self):
        self.__ftp_dir = None
        self.__temp_dir = init_temp_dir()

        self.__wav_regex = r'\/[\d]+\/CONTENTS\/wav\/(?:chapter|verse|chunk)'
        self.__chapter_wav_regex = r'_c[\d]+\..*$'
        self.__dir_wav_regex = r'^.*\/(.*)\/(.*)\/(.*)\/([\d]+)\/CONTENTS\/wav\/(chapter|verse|chunk)'

        argv_parser = ArgvParser()
        self.__ftp_dir = argv_parser.get_ftp_dir()

        self.__logger = WorkerLogging.logger()
        self.__process_tools = ProcessTools()

    def execute(self):
        self.__logger.info("Chapter worker started!")

        for root, dirs, files in os.walk(self.__ftp_dir):
            for file in files:
                if re.search(self.__wav_regex, root):
                    src_file = os.path.join(root, file)

                    # Process chapter files only
                    if re.search(self.__chapter_wav_regex, src_file):
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
                            verses_dir = os.path.join(target_dir, "verses")
                            os.makedirs(verses_dir, exist_ok=True)
                            target_file = os.path.join(target_dir, file)

                            self.__logger.info('Found chapter file: ' + src_file)

                            # Copy source file to temp dir
                            self.__logger.info('Copying file ' + src_file + ' to ' + target_file)
                            shutil.copy2(src_file, target_file)

                            # Try to fix wav metadata
                            self.__logger.info('Fixing metadata: ' + target_file)
                            self.__process_tools.fix_metadata(target_file)

                            # Split chapter files into verses
                            self.__logger.info(
                                'Splitting chapter ' + target_file + ' into ' + verses_dir
                            )
                            self.__process_tools.split_chapter(target_file, verses_dir)

                            # Copy original verse files
                            self.__logger.info(
                                'Copying original verse files from ' + verses_dir + ' into ' + remote_dir
                            )
                            self.__process_tools.copy_file(verses_dir, remote_dir)

                            # Convert chapter into mp3
                            self.__logger.info('Converting chapter: ' + target_file)
                            self.__process_tools.convert_to_mp3(target_file)

                            # Convert verses into mp3
                            self.__logger.info('Converting verses in ' + verses_dir)
                            self.__process_tools.convert_to_mp3(verses_dir)

                            # Copy converted chapter file
                            self.__logger.info(
                                'Copying chapter mp3 from ' + target_dir + ' into ' + remote_dir
                            )
                            self.__process_tools.copy_file(target_dir, remote_dir, grouping)

                            # Copy converted verse files
                            self.__logger.info(
                                'Copying verses mp3 from ' + verses_dir + ' into ' + remote_dir
                            )
                            self.__process_tools.copy_file(verses_dir, remote_dir)

        self.__logger.info('Deleting temporary directory: ' + self.__temp_dir)
        shutil.rmtree(self.__temp_dir)

        self.__logger.info('Chapter worker finished!')


worker = ChapterWorker()
worker.execute()
