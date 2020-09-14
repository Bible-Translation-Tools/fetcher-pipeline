import logging
import subprocess
import sys


def fix_metadata(input_file, verbose=False):
    run_process(
        'java -jar tools/bttConverter.jar -f {} -m chunk'.format(input_file),
        verbose
    )


def split_chapter(input_file, output_dir, verbose=False):
    run_process(
        'java -jar tools/tr-chunk-browser-cli.jar -s -f {} -o {}'.format(input_file, output_dir),
        verbose
    )


def convert_to_mp3(input_file_or_dir, verbose=False):
    run_process(
        'java -jar tools/audio-compressor-cli.jar -f mp3 -i {}'.format(input_file_or_dir),
        verbose
    )


def run_process(command, verbose=False):
    process = subprocess.run(
        command,
        capture_output=True,
        universal_newlines=True,
        shell=True
    )

    if process.returncode != 0:
        logging.error("A fatal error occurred")
        logging.debug(process.stderr)
        sys.exit(1)
    else:
        if verbose:
            logging.debug(process.stdout)
