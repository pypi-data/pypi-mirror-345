import datetime
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from loguru import logger

from ..config import settings
from ..storage import storage_api
from . import db, login, message
from .spider import Spider

check_worker_size = 2000
check_worker_queue = Queue(maxsize=check_worker_size)
check_worker_pool = ThreadPoolExecutor()

check_maxsize = 5000
check_queue = Queue(maxsize=check_maxsize)

download_worker_size = os.cpu_count() * 100
download_worker_queue = Queue(maxsize=download_worker_size)
download_worker_pool = ThreadPoolExecutor(os.cpu_count() * 2)


e_stop_scan = threading.Event()
e_stop_check = threading.Event()
e_stop_process = threading.Event()
e_stop_download_submit = threading.Event()


def scan_files(pk=None, prefix=""):

    if prefix and prefix != "":
        prefix = prefix.rstrip("/") + "/"
    try:
        data, start_prefix, root, marker, more = storage_api.http_get_files(
            dataset_id=pk, prefix=prefix
        )
    except Exception as e:
        logger.error(e)
        return

    print("\nroot:", root.strip("/"))

    for path, size in data:
        check_queue.put((start_prefix + path, size))
        db.insert_file_info(start_prefix + path, size)

    marker_point = marker  # noqa
    while True:
        data, start_prefix, root, marker, more = storage_api.http_get_files(
            dataset_id=pk, prefix=prefix, marker=marker_point
        )
        for path, size in data:  # noqa
            check_queue.put((start_prefix + path, size))
            db.insert_file_info(start_prefix + path, size)
        if not more:
            break
        marker_point = marker


def __check_download(name, size):
    from ..spider import spider_size

    download_size = spider_size.getsize(name, size)

    if download_size != size:
        db.checked_need_download(name)
        logger.info(f"download_queue, {name} download_size: {download_size} / {size}")
    else:
        db.checked_completed_download(name)
        logger.info(f"download_check, {name} download_size: {download_size} / {size}")

    qsize = check_worker_queue.qsize()
    message.put(f"download_check({qsize} / {check_worker_size}), {name} ")


def download_check():
    while True:
        check_qsize = check_queue.qsize()
        if check_qsize == 0:
            stop = e_stop_scan.wait(timeout=1)
            if stop:
                break
        name, size = check_queue.get()
        # submit
        check_worker_queue.put(0)
        task = check_worker_pool.submit(__check_download, name, size)
        task.add_done_callback(lambda x: check_worker_queue.get())

    time.sleep(5)
    while True:
        check_qsize = check_queue.qsize()
        if check_qsize == 0:
            break
        name, size = check_queue.get()
        check_worker_queue.put(0)
        task = check_worker_pool.submit(__check_download, name, size)
        task.add_done_callback(lambda x: check_worker_queue.get())

    # 检查所有的文件是否已经提交下载
    while True:
        time.sleep(1)
        try:
            # download_status = "created", download_checked = "1"
            need_download = db.get_created_count()
        except Exception as e:
            logger.error(e)
            continue
        if need_download == 0:
            try:
                db.get_uncompleted_files()
            except Exception as e:
                logger.error(e)
                continue
            else:
                break


def download_part():

    while True:
        try:
            files = db.get_uncompleted_files()
        except Exception as e:
            # 数据查询错误从新查询
            logger.error(e)
            continue

        if len(files) == 0:
            time.sleep(1)
            created_count = db.get_created_count()
            if created_count != 0:
                continue
            else:
                if e_stop_check.wait(timeout=1):
                    break
                else:
                    time.sleep(1)
                    continue

        for uncompleted in files:
            name = uncompleted[0]
            size = int(uncompleted[1])

            try:
                db.loading_file(name)  # 标记文件文下载中
            except Exception as e:
                time.sleep(1)
                logger.error(e)
                continue

            spider = Spider(
                name,
                size,
                report_cb=db.completed_file,
                executor_poll=download_worker_pool,
                executor_pipeline=download_worker_queue,
            )
            spider.run()
            qsize = download_worker_queue.qsize()
            message.put(
                f"download_submit({qsize} / {download_worker_size}), {name}, "
                f"size: {size}"
            )

    # 文件下载任务提交完成
    e_stop_download_submit.set()


def run_downloader(dataset_id, **kwargs):

    from . import logger

    p_watch = threading.Thread(target=message.watch_proc)
    p_watch.start()
    print(f"\n{datetime.datetime.now()} 开始下载")

    ak, sk = login.load()  # noqa
    kwargs.setdefault("dataset", dataset_id)
    kwargs.setdefault("ak", ak)
    kwargs.setdefault("sk", sk)
    kwargs.setdefault("intranet", "public")
    kwargs.setdefault("host", "http://internal-data.baai.ac.cn")
    kwargs.setdefault("level", "INFO")
    kwargs.setdefault("path", "")

    config = settings.Application(**kwargs)

    print(f"{config}")

    logger.init()

    db.remove()
    db.create_table()
    db.reset_created_file()

    # 获取文件
    p_scan = threading.Thread(target=scan_files, args=(config.dataset, config.path))
    p_scan.start()

    # 提交检查
    p_check = threading.Thread(target=download_check)
    p_check.start()

    # 提交下载文件
    p_download = threading.Thread(target=download_part)
    p_download.start()

    # 扫描完成
    p_scan.join()
    e_stop_scan.set()
    print("\n获取文件线程池处理完毕")

    # 检查完成
    p_check.join()
    check_worker_pool.shutdown(wait=True)
    e_stop_check.set()
    print("\n检查线程池处理完毕")

    e_stop_download_submit.wait()
    download_worker_pool.shutdown(wait=True)
    print("\n下载线程池处理完毕")

    message.watch_stop()

    completed_count = db.get_completed_count()
    all_count = db.get_all_count()
    percent = completed_count / all_count * 100
    process = "=" * int(percent / 2)
    process = process.ljust(50, " ")
    print(
        f"<{completed_count} / {all_count}>",
        f"{datetime.datetime.now()} " "summary",
        "[" + process + "]",
        f"{percent:.2f}%",
    )
