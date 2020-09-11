import os
import re
import shutil
import subprocess

from argv_parser import ArgvParser
from logger import WorkerLogging
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
                            self.fix_metadata(target_file)

                            # Split chapter files into verses
                            self.__logger.info(
                                'Splitting chapter ' + target_file + ' into ' + verses_dir
                            )
                            self.split_chapter(target_file, verses_dir)

                            # Copy original verse files
                            self.__logger.info(
                                'Copying original verse files from ' + verses_dir + ' into ' + remote_dir
                            )
                            self.copy_file(verses_dir, remote_dir)

                            # Convert chapter into mp3
                            self.__logger.info('Converting chapter: ' + target_file)
                            self.convert_to_mp3(target_file)

                            # Convert verses into mp3
                            self.__logger.info('Converting verses in ' + verses_dir)
                            self.convert_to_mp3(verses_dir)

                            # Copy converted chapter file
                            self.__logger.info(
                                'Copying chapter mp3 from ' + target_dir + ' into ' + remote_dir
                            )
                            self.copy_file(target_dir, remote_dir, grouping)

                            # Copy converted verse files
                            self.__logger.info(
                                'Copying verses mp3 from ' + verses_dir + ' into ' + remote_dir
                            )
                            self.copy_file(verses_dir, remote_dir)

        self.__logger.info('Deleting temporary directory: ' + self.__temp_dir)
        shutil.rmtree(self.__temp_dir)

        self.__logger.info('Chapter worker finished!')

    def fix_metadata(self, input_file):
        self.run_process(
            'java -jar tools/bttConverter.jar -f ' + input_file + ' -m chunk'
        )

    def split_chapter(self, input_file, output_dir):
        self.run_process(
            'java -jar tools/tr-chunk-browser-cli.jar -s -f ' + input_file + ' -o ' + output_dir
        )

    def convert_to_mp3(self, input_file_or_dir):
        self.run_process(
            'java -jar tools/audio-compressor-cli.jar -f mp3 -i ' + input_file_or_dir
        )

    def run_process(self, command):
        process = subprocess.run(
            command,
            capture_output=True,
            universal_newlines=True,
            shell=True
        )

        if len(process.stdout) > 0:
            self.__logger.info(process.stdout)
        if len(process.stderr) > 0:
            self.__logger.error(process.stderr)

    def copy_file(self, src_dir, target_dir, grouping='verse'):
        for path in os.listdir(src_dir):
            if path == 'verses':
                continue

            src_file = os.path.join(src_dir, path)

            self.__logger.info('Copying file: ' + src_file)

            path_without_extension = os.path.splitext(path)[0]
            extension = os.path.splitext(path)[1]
            path_without_extension = re.sub(r'_t[\d]+$', '', path_without_extension)

            if extension == '.mp3':
                t_dir = os.path.join(target_dir, extension[1:], 'hi', grouping)
            else:
                t_dir = os.path.join(target_dir, extension[1:], grouping)

            t_file = os.path.join(t_dir, path_without_extension + extension)
            if not os.path.exists(t_file):
                os.makedirs(t_dir, exist_ok=True)
                shutil.copy2(src_file, t_file)
                self.__logger.info('Copied to: ' + t_file)
            else:
                self.__logger.info('File exists, skipping...')


worker = ChapterWorker()
worker.execute()
