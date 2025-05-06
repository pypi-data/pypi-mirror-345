from loguru import logger


def default_report_cb(x):
    logger.debug(x)


class Executor:
    def __init__(
        self,
        executor_name,
        executor_size,
        executor_pipeline,
        executor_poll,
        report_cb=None,
    ):
        self.executor_pipeline = executor_pipeline
        self.executor_poll = executor_poll

        self.executor_name = executor_name
        self.executor_size = executor_size
        self.report_cb = report_cb

    def run(self):
        pass


if __name__ == "__main__":
    for i in range(10):
        print(i)
        Executor(str(i)).run()
