import datetime

import requests
from loguru import logger

from ..config import settings
from .storage_login import login
from .storage_retry import retry_decorator

# from urllib.parse import urlencode


# 对象存储(KS3)
# https://docs.ksyun.com/directories/3671?type=1


# TODO: 临时模拟使用, 正常从配置文件中获取


@retry_decorator(max_retries=3, delay=2)
def ks3_generate_url(bucket, key, expires_in=3600 * 24) -> str:  # TODO: 临时模拟使用
    conf = settings.Application()

    start = datetime.datetime.now()

    api = f"{conf.api_endpoint}/storage/presign/"
    token = login(ak=conf.ak, sk=conf.sk)
    header = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "dataset": conf.dataset,
        "bucket": bucket,
        "key": key,
        "expires": expires_in,
        "intranet": conf.intranet,
    }
    # param = urlencode(data)

    response = requests.post(f"{api}", headers=header, json=data)
    if response.status_code != 200:
        raise Exception(
            f"presign_url err,  {data}  {response.status_code} {response.text}"
        )
    endpoint = response.json()["endpoint"]

    end = datetime.datetime.now()
    since = end.timestamp() - start.timestamp()

    addr = endpoint.split("?")[0]
    logger.debug(f"presign_url: {addr}, use: {since}s")
    return endpoint


@retry_decorator(max_retries=3, delay=2)
def http_get_files(dataset_id: str, prefix: str = "", marker: str = ""):
    conf = settings.Application()

    api = f"{conf.api_endpoint}/storage/dataset/"

    token = login(ak=conf.ak, sk=conf.sk)
    header = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "id": dataset_id,
        "prefix": prefix,
        "marker": marker,
    }
    # param = urlencode(data)

    endpoint = f"{api}"
    response = requests.post(endpoint, headers=header, json=data)

    if response.status_code != 200:
        raise Exception(f"{response.status_code} {response.text}")

    try:
        jres = response.json()
    except Exception as e:
        print(f"{response.status_code} {response.text}, err: {e}")
        raise Exception(f"{response.status_code}, {response.text}")

    if jres["code"] != 0:
        raise Exception(
            f'{ jres["dataset_id"] }: { jres["msg"] }, { jres["perm_name"] }'  # noqa
        )

    data = jres.get("data")
    prefix = jres.get("prefix")
    root = jres.get("root")
    marker = jres.get("marker")
    more = jres.get("more")

    rs = (data, prefix, root, marker, more)
    return rs


def presigned_url(path: str) -> str:
    """presigned_url

    :param path: ks3://bucket/path/name.png
    :return:
    """

    parts = path.split("://")

    # storage_name = parts[0]
    storage_path = parts[1]

    bucket, key = storage_path.split("/", maxsplit=1)
    return ks3_generate_url(bucket, key)
