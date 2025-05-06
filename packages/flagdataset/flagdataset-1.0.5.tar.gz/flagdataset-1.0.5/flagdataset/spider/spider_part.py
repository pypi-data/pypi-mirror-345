import hashlib
import pathlib

from .spider_path import default_spider_path


def name_part(name, pidx):
    hex_digest = hashlib.sha256(name.encode("utf-8")).hexdigest()

    save_path = pathlib.Path(default_spider_path) / hex_digest
    pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

    return save_path / f"{pidx}_{hex_digest}.tmp"


def range_part(file_size, part_size=1024 * 1024 * 5):
    parts_range = []
    for i in range(0, file_size, part_size):
        start_pos = i
        end_pos = i + part_size - 1
        if end_pos > file_size:
            end_pos = file_size - 1
        parts_range.append((start_pos, end_pos))
    return parts_range


def exist_part(name, pidx, part_size=1024 * 1024 * 5):
    tmp_path = name_part(name, pidx)
    if tmp_path.exists():
        return tmp_path.stat().st_size == part_size
    else:
        return False


if __name__ == "__main__":
    p = range_part(1024 * 1024 * 1024)

    print(p)
