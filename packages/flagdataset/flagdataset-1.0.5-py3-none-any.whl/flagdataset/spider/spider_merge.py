import hashlib
import pathlib
import shutil

from loguru import logger

from .spider_path import default_download_path, default_spider_path


def range_index(file_size, part_size=1024 * 1024 * 5):
    idx = []
    for i, _ in enumerate(range(0, file_size, part_size)):
        idx.append(i)
    return idx


def check_part(name, file_size, part_size=1024 * 1024 * 5, target=None):

    if target is None:  # noqa
        target_dir = pathlib.Path(default_download_path)
    else:
        target_dir = pathlib.Path(target)

    path_target = name.split("://")[1].split("/", maxsplit=1)

    target_path = target_dir / pathlib.Path(path_target[1])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    hex_digest = hashlib.sha256(name.encode("utf-8")).hexdigest()

    tmp_path = pathlib.Path(default_spider_path) / hex_digest

    tmp_list = list(tmp_path.glob("*.tmp"))
    tmp_list.sort()

    tmp_files = sorted(tmp_list, key=lambda x: int(x.name.split("_")[0]))

    # 检查分片是否正确
    tmp_index = set(map(lambda x: int(x.name.split("_")[0]), tmp_files))
    range_idx = set(range_index(file_size, part_size))

    # want_idx = range_idx - tmp_index

    return tmp_index, range_idx


def merge_part(name, file_size, part_size=1024 * 1024 * 5, target=None) -> int:

    if target is None:  # noqa
        target_dir = pathlib.Path(default_download_path)
    else:
        target_dir = pathlib.Path(target)

    path_target = name.split("://")[1].split("/", maxsplit=1)

    target_path = target_dir / pathlib.Path(path_target[1])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    hex_digest = hashlib.sha256(name.encode("utf-8")).hexdigest()

    tmp_path = pathlib.Path(default_spider_path) / hex_digest

    tmp_list = list(tmp_path.glob("*.tmp"))
    tmp_list.sort()

    tmp_files = sorted(tmp_list, key=lambda x: int(x.name.split("_")[0]))

    # 检查分片是否正确
    tmp_index = set(map(lambda x: int(x.name.split("_")[0]), tmp_files))
    range_idx = set(range_index(file_size, part_size))

    want_idx = range_idx - tmp_index
    if want_idx:
        logger.warning(f"分片 {want_idx} 丢失: {tmp_path}")

    # TODO: 处理丢失分片，目前缺少时不合并
    if want_idx:
        return -1

    total_size = 0
    with target_path.open("ab") as target_writer:
        # print(f"{datetime.datetime.now()} merge_process")
        for m_idx, tmp_file in enumerate(tmp_files):
            merge_size = tmp_file.stat().st_size
            # print(f"merge part: {m_idx+1} {name}-{merge_size}")
            with tmp_file.open("rb") as tmp_reader:
                shutil.copyfileobj(tmp_reader, target_writer)  # noqa
                total_size += merge_size

    try:
        shutil.rmtree(tmp_path)
    except Exception as e:
        logger.error(e)

    return total_size
