class SDKDownloader:

    def __init__(self, ak: str = None, sk: str = None):
        self.ak = ak
        self.sk = sk

    @staticmethod
    def download(dataset_id: str, **kwargs):
        from .ds_download_dataset import run_downloader

        run_downloader(dataset_id, **kwargs)

    @staticmethod
    def get(dataset_id: str, path: str, **kwargs):
        from .ds_download_file import run_downloader

        assert path, "path is required"
        run_downloader(dataset_id, path, **kwargs)


def new_downloader(ak=None, sk=None, **kwargs):
    import json

    from .login import token_path

    if ak and sk:
        with open(token_path, "w") as fd:
            data = {
                "ak": ak.strip(),
                "sk": sk.strip(),
            }
            json.dump(data, fd)  # noqa

    return SDKDownloader(**kwargs)


class SDKUploader:
    pass
