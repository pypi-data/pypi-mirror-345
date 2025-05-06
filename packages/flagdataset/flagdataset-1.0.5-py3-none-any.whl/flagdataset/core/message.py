import datetime
import queue
import threading

from . import db

e_stop_watch = threading.Event()
q_message = queue.Queue(maxsize=1)


def watch_proc(proc=True):

    while True:
        stop = e_stop_watch.wait(timeout=1)
        if stop:
            break
        try:
            msg = q_message.get_nowait()
        except queue.Empty:
            msg = ""

        if proc:
            all_count = db.get_all_count()
            completed_count = db.get_completed_count()
            extra = f"<{completed_count} / {all_count}> "
        else:
            extra = ""

        if msg == "":
            continue
        print(f"\r\033[2K{extra}{msg}", end="")


def watch_stop():
    e_stop_watch.set()


def put(msg):
    if q_message.full():
        return
    q_message.put(f"{datetime.datetime.now()} {msg}")
