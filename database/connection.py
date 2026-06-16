from pathlib import Path
import sqlite3
import shutil

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "quiz.db"
STARTER_DB_PATH = DATA_DIR / "starter_quiz.db"

def ensure_database_exists():
    if DB_PATH.exists():
       return

    if not STARTER_DB_PATH.exists():
        raise FileNotFoundError(f"starter database not found: {STARTER_DB_PATH}")


    shutil.copy2(STARTER_DB_PATH, DB_PATH)

def get_connection():
    ensure_database_exists()
    return sqlite3.connect(DB_PATH)

def execute_commit(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(e)
    finally:
        conn.close()

def fetchone(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        result = cur.fetchone()
        return result
    finally:
        conn.close()

def fetchall(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        data = cur.fetchall()
        return data
    finally:
        conn.close()
