import sqlite3
from quiz_app.database.connection import get_connection, fetchall, fetchone, execute_commit
from quiz_app.logger import logger

def insert_user(user_id, real_name, user_name, role, lang, created_at):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")

        cur.execute("""
        INSERT INTO users (id, real_name, user_name, role, created_at)
        VALUES (?, ?, ?, ?, ?)""", (user_id, real_name, user_name, role, created_at))

        cur.execute("""
        INSERT INTO user_profiles (user_id, overall_score, language)
        VALUES (?, ?, ?)""", (user_id, 0, lang))

        conn.commit()

    except sqlite3.Error:
        logger.error(f"User {user_id} ({real_name}) could not registered")
        conn.rollback()
    finally:
        conn.close()

def fetch_all_users():

    return fetchall("""
    SELECT id,
    real_name,
    user_name,
    created_at
    FROM users""")

def fetch_user_by_id(user_id):

    return fetchone("""
    SELECT id, 
    real_name,
    user_name,
    created_at
    FROM users
    WHERE id = ?""", (user_id,))

def update_deactivate_user(user_id):

    execute_commit("""
    UPDATE users
    SET active = 0
    WHERE id = ?""", (user_id,))

def update_activate_user(user_id):
    execute_commit("""
    UPDATE users
    SET active = 1
    WHERE id = ?""", (user_id,))

def fetch_users_active():

    return fetchall("""
    SELECT id, active
    FROM users""")

def fetch_user_active_by_id(user_id):

    return fetchone("""
    SELECT active
    FROM users
    WHERE id = ?""", (user_id,))


def update_user_language(lang, user_id):

    execute_commit("""
    UPDATE user_profiles
    SET language = ?
    WHERE user_id = ?""", (lang, user_id))

def fetch_user_language(user_id):
    return fetchone("""
    SELECT language
    FROM user_profiles
    WHERE user_id = ?""", (user_id,))

def update_user_won(user_id):

    execute_commit("""
    UPDATE user_profiles
    SET won = won + 1
    WHERE user_id = ?""", (user_id,))

def fetch_user_profile_by_id(user_id):
    return fetchone("""
    SELECT u.id,
    u.real_name,
    u.user_name,
    up.best_score,
    up.overall_score,
    up.played,
    up.won,
    u.active
    FROM users u
    INNER JOIN user_profiles up
    ON u.id = up.user_id
    WHERE u.id = ?""", (user_id,))

def fetch_user_profiles():
    return fetchall("""
    SELECT u.id,
    u.real_name,
    u.user_name,
    up.best_score,
    up.overall_score,
    up.played,
    up.won,
    u.active
    FROM users u
    INNER JOIN user_profiles up
    ON u.id = up.user_id""")

def fetch_user_played(user_id):
    return fetchone("""
    SELECT played
    FROM user_profiles
    WHERE user_id = ?""", (user_id,))

def fetch_users_by_rating():

    return fetchall("""
    SELECT u.id, 
    u.real_name,
    u.user_name, 
    up.played,
    up.overall_score,
    up.won
    FROM users u
    INNER JOIN user_profiles up
    ON u.id = up.user_id
    ORDER BY up.overall_score DESC,
    up.won DESC, up.played ASC""")