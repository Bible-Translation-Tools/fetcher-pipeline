import os
from tempfile import gettempdir
from uuid import uuid4


def init_temp_dir():
    path = os.path.join(gettempdir(), str(uuid4()))
    os.makedirs(path, exist_ok=True)
    return path
