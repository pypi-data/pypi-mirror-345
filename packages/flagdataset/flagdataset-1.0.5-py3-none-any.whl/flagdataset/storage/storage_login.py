import base64
import datetime
import json
from functools import wraps

import requests
from loguru import logger

from ..config import settings
from .storage_retry import retry_decorator


def login_api(ak, sk):

    conf = settings.Application()

    # api = "http://120.92.19.30:30880/userAccessKey/v1/getAccessToken"

    api = f"{conf.auth_endpoint}/userAccessKey/v1/getAccessToken"
    data = {"ak": ak, "sk": sk}

    resp = requests.post(api, headers={"Content-Type": "application/json"}, json=data)

    logger.debug(f"login_api, {api}, {resp.status_code}, {resp.text}")

    assert resp.status_code == 200, resp.status_code

    assert resp.json().get("code") == 0, resp.text

    resp_data = resp.json().get("data")

    return resp_data


def expire(token):
    if not token:
        return False

    _, payload_base64, _ = token.split(".")

    payload_base64 += "=" * (-len(payload_base64) % 4)
    payload_bytes = base64.urlsafe_b64decode(payload_base64)

    # 解析JSON
    payload = json.loads(payload_bytes.decode("utf-8"))

    exp = payload.get("exp")

    now = datetime.datetime.now().timestamp()

    return now + 60 * 60 > exp


def create_login_function():
    access_token = ""

    @retry_decorator(max_retries=3, delay=5)
    @wraps(login_api)
    def _login_logic(ak, sk):
        nonlocal access_token

        if access_token and not expire(access_token):
            return access_token

        access_token = login_api(ak, sk).get("token")
        return access_token

    return _login_logic


# 登陆函数
login = create_login_function()
