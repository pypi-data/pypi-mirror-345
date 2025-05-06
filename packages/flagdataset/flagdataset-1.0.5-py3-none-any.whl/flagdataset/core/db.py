import datetime
import hashlib
import os
import pathlib
import sqlite3
import threading

from loguru import logger
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

user_path = os.path.expanduser("~")
default_db_path = os.path.join(user_path, ".sdk_download/downloads.db")
db_name = pathlib.Path(default_db_path)

lock = threading.Lock()

engine = create_engine(
    f"sqlite:///{default_db_path}",
    echo=False,
    pool_size=300,
    max_overflow=1000,
    connect_args={"check_same_thread": False},
)


Base = declarative_base()


# 定义一个用户模型
class DownloadFiles(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    download_name = Column(String, nullable=True)
    download_hash = Column(String, unique=True, nullable=True)
    download_status = Column(String, nullable=True)
    download_checked = Column(String, nullable=True)
    download_size = Column(String, nullable=True)
    download_time = Column(String, nullable=True)


def create_table():
    Base.metadata.create_all(engine, checkfirst=True)


def db():
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def insert_file_info(name, size, status="created"):
    # 默认 download_checked: "0", download_checked: "1" 已下载

    with lock:
        session = db()

        download_hash = hashlib.sha256(name.encode()).hexdigest()
        download_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 如果存在就不处理
        tmp = (
            session.query(DownloadFiles).filter_by(download_hash=download_hash).first()
        )
        if tmp:
            return

        temp = DownloadFiles(
            download_name=name,
            download_hash=download_hash,
            download_status=status,
            download_checked="0",
            download_size=size,
            download_time=download_time,
        )

        session.add(temp)
        try:
            session.commit()
        except Exception as e:  # noqa
            session.rollback()
        finally:
            session.close()


def checked_need_download(name):
    download_hash = hashlib.sha256(name.encode()).hexdigest()

    with lock:
        session = db()
        try:
            session.query(DownloadFiles).filter_by(download_hash=download_hash).update(
                {"download_checked": "1"}
            )  # 还没下载
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
        finally:
            session.close()


def checked_completed_download(name):
    """checked_completed_download
    文件更新为完成, download_checked 更新为之前下载
    """

    download_hash = hashlib.sha256(name.encode()).hexdigest()

    with lock:
        session = db()

        try:
            session.query(DownloadFiles).filter_by(download_hash=download_hash).update(
                {"download_checked": "2", "download_status": "completed"}
            )  # 之前已经下载
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
        finally:
            session.close()


def loading_file(name: str):
    # 更新为下载中

    download_hash = hashlib.sha256(name.encode()).hexdigest()
    with lock:
        session = db()
        try:
            session.query(DownloadFiles).filter_by(download_hash=download_hash).update(
                {"download_status": "loading"}
            )  # 还没下载
            session.commit()
        except Exception as e:  # noqa
            session.rollback()
            raise e
        finally:
            session.close()


def completed_file(name: str):
    download_hash = hashlib.sha256(name.encode()).hexdigest()

    with lock:
        session = db()
        try:
            session.query(DownloadFiles).filter_by(download_hash=download_hash).update(
                {"download_status": "completed"}
            )  # 完成下载
            session.commit()
        except Exception:  # noqa
            session.rollback()
        finally:
            session.close()


def reset_created_file():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute(
            """UPDATE files SET download_status = ? WHERE download_status = ?""",  # noqa
            ("created", "loading"),
        )
    except sqlite3.Error as e:
        print(e)
        conn.rollback()
    else:
        conn.commit()
    finally:
        conn.close()


def get_all_count():
    """文件数量"""

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("""SELECT COUNT(*) AS file_count FROM files""")  # noqa
    rs = c.fetchone()
    return rs[0]


def get_completed_count():
    """完成下载的数量"""

    with lock:
        session = db()
        try:
            count = (
                session.query(DownloadFiles)
                .filter_by(download_status="completed")
                .count()
            )
        except Exception as e:  # noqa
            raise e
        finally:
            session.close()

        return count


def get_uncompleted_stat():
    """完成下载的数量"""

    with lock:
        session = db()
        try:
            queryset = (
                session.query(DownloadFiles)
                .filter(DownloadFiles.download_status != "completed")
                .all()
            )
        except Exception as e:  # noqa
            raise e
        finally:
            session.close()

        for item in queryset:
            print(item.download_name, item.download_status, item.download_checked)


def get_loading_count():
    """下载中数量"""

    with lock:
        session = db()
        try:
            count = (
                session.query(DownloadFiles)
                .filter_by(download_status="loading")
                .count()
            )
        except Exception as e:  # noqa
            raise e
        finally:
            session.close()

        return count


def get_created_count():
    """创建数量"""
    with lock:
        session = db()
        try:
            count = (
                session.query(DownloadFiles)
                .filter_by(download_status="created", download_checked="1")
                .count()
            )
        except Exception as e:
            raise e
        finally:
            session.close()

        return count


# 获取需要下载的文件信息
def get_uncompleted_files():
    with lock:
        session = db()
        try:
            tmp = (
                session.query(DownloadFiles)
                .filter_by(download_status="created")
                .filter_by(download_checked="1")
                .first()
            )
        except Exception as e:
            raise e
        finally:
            session.close()

        if not tmp:
            return []

        return [
            [
                tmp.download_name,
                tmp.download_size,
                tmp.download_status,
                tmp.download_checked,
            ]
        ]


def get_all_files():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        "SELECT download_name, download_size, download_status, download_checked FROM files"  # noqa
    )  # noqa
    rs = c.fetchall()
    conn.close()
    return rs


def remove():
    try:
        os.remove(db_name)
    except FileNotFoundError:
        pass


if __name__ == "__main__":

    uncompleted_files = get_uncompleted_files()
    print(uncompleted_files)
