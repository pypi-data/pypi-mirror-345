from ..storage import storage_wr


class DownloadException(Exception):
    pass


def download_part(part_endpoint, stat_pos, end_pos):
    part_bytes = storage_wr.read_bytes(part_endpoint, stat_pos, end_pos)

    # TODO: 检查文件是否完整
    if len(part_bytes) != end_pos - stat_pos + 1:
        raise DownloadException(
            f"Error_download_part: {part_endpoint} {stat_pos} {end_pos} {len(part_bytes)}"  # noqa
        )

    return part_bytes
