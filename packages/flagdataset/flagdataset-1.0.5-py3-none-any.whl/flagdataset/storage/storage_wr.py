import requests

from .storage_retry import retry_decorator


@retry_decorator(max_retries=3, delay=5)
def read_meta(endpoint: str, meta_get=lambda x: int(x.get("Content-Length", 0))):
    response = requests.head(endpoint, headers={"accept-encoding": None})
    extra = meta_get(response.headers)
    ok = False
    if response.status_code == 200:
        ok = True
    return ok, extra


@retry_decorator(max_retries=3, delay=5)
def read_bytes(endpoint: str, start_pos, end_pos) -> bytes:

    headers = {
        "Range": f"bytes={int(start_pos)}-{int(end_pos)}",
    }
    resp_content = requests.get(endpoint, headers=headers, timeout=15)
    if resp_content.status_code > 400:
        raise Exception(
            f"Error_read_bytes: {resp_content.status_code} {headers}: {endpoint}"
        )

    return resp_content.content
