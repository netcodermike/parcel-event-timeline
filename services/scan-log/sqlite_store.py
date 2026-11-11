from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3


@contextmanager
def transaction():
    path = Path(os.getenv("DB_PATH", "state/data.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
