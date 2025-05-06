import datetime
import math
import time

from loguru import logger

from ..spider.spider_download import download_part
from ..spider.spider_merge import check_part, merge_part
from ..spider.spider_part import exist_part, name_part, range_part
from ..storage.storage_api import presigned_url
from . import message, worker


class Executor(worker.Executor):
    part_size = 1024 * 1024 * 5

    def run(self):
        start_time = datetime.datetime.now()
        size = self.executor_size

        length = math.ceil(size / self.part_size)
        try:
            need_download = range_part(size, part_size=self.part_size)
            results = []
            for idx, (start, end) in enumerate(need_download):
                self.executor_pipeline.put(self.executor_name)
                try:
                    task = self.executor_poll.submit(
                        self.download_part,
                        self.executor_name,
                        idx,
                        "",
                        start,
                        end,
                        size,
                    )
                    message.put(
                        f"download_part({idx+1} / {length}): {self.executor_name}, "
                        f"size: {end-start}"
                    )
                except Exception as e:
                    self.executor_pipeline.get()
                    logger.error(e)
                else:
                    logger.debug(
                        f"submit_part {self.executor_name}, "
                        f"part: {idx+1} / {length}, "
                        f"start_time: {start_time}, {self.part_size} / {size}"
                    )
                    results.append(task)
        except Exception as e:
            logger.error(e)
        else:
            try:
                self.executor_pipeline.put(self.executor_name)
                self.executor_poll.submit(self.watch, results, size, start_time)
            except Exception as e:
                self.executor_pipeline.get()
                logger.error(e)

    def watch(self, tasks, size, start_time=None):
        from ..config import settings

        conf = settings.Application()

        length = math.ceil(size / self.part_size)
        name = self.executor_name
        part_size = self.part_size
        target = conf.target

        end_idx = []
        for task in tasks:
            idx, since = task.result()
            end_idx.append(idx)
            logger.debug(
                f"download_part {name}, part: {idx+1} / {length}, "
                f"time: {datetime.datetime.now()}, size: {size}, use: {since}s"
            )
            message.put(f"download_part({idx + 1} / {length}): {self.executor_name}")

        # TODO: 优化
        for idc in range(100):
            a, b = check_part(name, size, part_size=part_size, target=target)
            if len(end_idx) == length and a == b:
                break
            print(f"merge_check, count: {idc}", name, size, a, b)
            time.sleep(10)

        try:
            merge_part(name, size, part_size, target)
        except Exception as e:
            logger.error(e)
        else:
            end_time = datetime.datetime.now()  # 文件下载完毕时间
            logger.info(
                f"merge_part {name}, download: {length}, "
                f"start_time: {start_time}, end_time: {end_time}, "
                f"use: {end_time.timestamp()-start_time.timestamp()}, "
                f"size: {size}"
            )

        try:
            self.report_cb(self.executor_name)
        except Exception as e:
            logger.error(e)

        self.executor_pipeline.get()

    def download_part(self, name, idx, _endpoint, stat, end, size):  # noqa
        try:
            endpoint = presigned_url(self.executor_name)

            start = datetime.datetime.now()
            if exist_part(name, idx, part_size=self.part_size):
                since = datetime.datetime.now().timestamp() - start.timestamp()
                return idx, since

            b_part = download_part(endpoint, stat, end)
            temp = name_part(name, idx)

            try:
                with temp.open("wb") as writer:
                    writer.write(b_part)
            except Exception as e:
                logger.error(f"write_part {e}")

        except Exception as e:
            logger.error(f"write_part {e}")
        else:
            logger.debug(f"write_part {name}, part: {idx + 1}, path: {temp.absolute()}")
        finally:
            self.executor_pipeline.get()  # 下载片段任务执行完毕

        since = datetime.datetime.now().timestamp() - start.timestamp()

        return idx, int(since)


class Spider(Executor):
    pass
