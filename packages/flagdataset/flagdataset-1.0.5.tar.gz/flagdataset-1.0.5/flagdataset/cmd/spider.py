import argparse

parser = argparse.ArgumentParser(description="flagdataset")

# 添加参数
parser.add_argument("option", help="option: login, download or get")
parser.add_argument("-d", "--dataset-id", type=str, help="dataset-id: dataset id")
parser.add_argument("-p", "--path", type=str, help="path: /path/to/source/folder")
parser.add_argument("-t", "--target", type=str, help="target: /path/to/local/folder")
parser.add_argument(
    "-i", "--intranet", default="public", type=str, help="intranet: public or private"
)
parser.add_argument("--level", default="INFO", type=str, help="debug level")
parser.add_argument(
    "--host", default="http://internal-data.baai.ac.cn", type=str, help="host"
)


# 解析参数
args = parser.parse_args()


def download():
    from .. import new_downloader

    app = new_downloader()

    if args.dataset_id:
        app.download(
            args.dataset_id,
            path=args.path,
            target=args.target,
            intranet=args.intranet,
            level=args.level,
            host=args.host,
        )


def get():
    from .. import new_downloader

    path = args.path.strip('"').strip("'")

    app = new_downloader()

    if args.dataset_id and args.path:
        app.get(
            args.dataset_id,
            path=path,
            target=args.target,
            intranet=args.intranet,
            level=args.level,
            host=args.host,
        )


def login():
    from ..core.login import save

    save()
    pass


cmdargs = {
    "download": download,
    "login": login,
    "get": get,
}


def runcmd_option():
    runcmd = cmdargs.get(args.option)
    runcmd()
