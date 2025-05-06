from urllib.parse import urlencode

import requests
from loguru import logger

from ..config import settings
from .storage_login import login

api = "/search/v5/updateDownloadNum"


def update_download_num(status: int = 1):

    conf = settings.Application()

    data = {"datasetId": conf.dataset, "status": status}

    query = urlencode(data)
    endpoint = conf.report_endpoint + f"{api}?{query}"
    token = login(ak=conf.ak, sk=conf.sk)
    header = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.get(endpoint, headers=header)

    logger.debug(f"update_download_num, {endpoint}, {resp.status_code}, {resp.text}")
