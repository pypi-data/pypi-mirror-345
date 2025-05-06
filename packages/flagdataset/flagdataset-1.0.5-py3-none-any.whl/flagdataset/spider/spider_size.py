import os
import pathlib


def getsize(name: str, size_report: int):
    from ..config import settings

    conf = settings.Application()

    path_target = name.split("://")[1].split("/", maxsplit=1)

    file_path = (pathlib.Path(conf.target) / path_target[1]).__str__()

    try:
        size_os = os.path.getsize(file_path)
    except OSError:
        size_os = 0

    if size_os == size_report:
        return size_os

    if os.path.isfile(file_path):
        os.remove(file_path)

    return 0
