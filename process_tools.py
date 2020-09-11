import os
import re
import shutil
import subprocess

from logger import WorkerLogging


class ProcessTools:

    def __init__(self):
        self.__logger = WorkerLogging.logger()

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
