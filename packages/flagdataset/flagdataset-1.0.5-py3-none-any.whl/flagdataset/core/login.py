import os

from loguru import logger

token_path = os.path.join(os.path.expanduser("~"), ".sdk_download/token.json")


def save():
    import json
    import pathlib

    pathlib.Path(token_path).parent.mkdir(parents=True, exist_ok=True)

    ak = input("ak: ")
    sk = input("sk: ")

    with open(token_path, "w") as fd:
        data = {
            "ak": ak.strip(),
            "sk": sk.strip(),
        }
        json.dump(data, fd)  # noqa


def load():
    import json
    import pathlib

    if not pathlib.Path(token_path).exists():
        pathlib.Path(token_path).parent.mkdir(parents=True, exist_ok=True)

        ned = input("login required, y/n: ")
        if ned == "y":
            save()
        else:
            print("login required, first")

    with open(token_path, "r") as fd:
        data = json.load(fd)  # noqa
        ak = data.get("ak")
        sk = data.get("sk")

        logger.debug(f"token: ak: {ak}, sk: {sk}")
        return ak, sk
