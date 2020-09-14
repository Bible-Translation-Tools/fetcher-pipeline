import logging
import re
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4


def init_temp_dir() -> Path:
    path = Path(gettempdir(), str(uuid4()))
    path.mkdir(parents=True, exist_ok=True)
    return path


def rm_tree(path):
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def copy_dir(src_dir: Path, target_dir: Path, grouping='verse', quality='hi', media=None):
    for src_file in src_dir.glob('*.*'):
        copy_file(src_file, target_dir, grouping, quality, media)


def copy_file(src_file: Path, target_dir: Path, grouping='verse', quality='hi', media=None):
    path_without_extension = src_file.stem
    path_without_extension = re.sub(r'_t[\d]+$', '', path_without_extension)
    extension = src_file.suffix

    if extension == '.mp3':
        t_dir = target_dir.joinpath(extension[1:], quality, grouping)
    elif extension == '.tr':
        if media is not None:
            if media == 'mp3':
                t_dir = target_dir.joinpath(extension[1:], media, quality, grouping)
            else:
                t_dir = target_dir.joinpath(extension[1:], media, grouping)
        else:
            raise Exception("Media is not defined for TR container")
    else:
        t_dir = target_dir.joinpath(extension[1:], grouping)

    t_file = t_dir.joinpath(path_without_extension + extension)

    logging.debug('Copying file: {} to {}'.format(src_file, t_file))

    if not t_file.exists():
        t_dir.mkdir(parents=True, exist_ok=True)
        t_file.write_bytes(src_file.read_bytes())
        logging.debug('Copied successfully!')
    else:
        logging.debug('File exists, skipping...')
