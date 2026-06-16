import sqlite3
from quiz_app.database.connection import get_connection, fetchone, fetchall, execute_commit
from quiz_app.logger import logger

def create_session_record(user_id, started_at):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO game_sessions (user_id, score, started_at)
            VALUES (?, ?, ?)""", (user_id, 0, started_at))

        conn.commit()

        return cur.lastrowid
    except sqlite3.Error:
        logger.error(f"Failed to create session for user {user_id}")
        conn.rollback()
    finally:
        conn.close()

def insert_current_state(session_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO current_state (session_id, current_score, help_change_quest, help_50_50, finished)
        VALUES (?, ?, ?, ?, ?)""", (session_id, 0, 1, 2, 0))

        session_id = fetchone("""
        SELECT session_id
        FROM current_state cs
        INNER JOIN game_sessions gs
        ON cs.session_id = gs.id
        WHERE gs.user_id = ?
        AND cs.finished = 0""", (user_id,))

        if session_id:
            cur.execute("""
            UPDATE current_state
            SET finished = 1
            WHERE session_id = ?""", (session_id[0],))

        conn.commit()
    except sqlite3.Error:
        logger.error(f"Failed to create current state for user {user_id}")
        conn.rollback()
    finally:
        conn.close()

def update_current_score(session_id, current_score):
    execute_commit("""
    UPDATE current_state
    SET current_score = ?
    WHERE session_id = ?""", (current_score, session_id))

def update_current_question(session_id, question_id):
    execute_commit("""
    UPDATE current_state
    SET question_id = ?
    WHERE session_id = ?""", (question_id, session_id))

def fetch_current_question_id(session_id):
    return fetchone("""
    SELECT question_id
    FROM current_state
    WHERE session_id = ?""", (session_id,))

def fetch_current_score(session_id):
    return fetchone("""
    SELECT current_score
    FROM current_state
    WHERE session_id = ?""", (session_id,))

def fetch_current_help_change_quest(session_id):
    return fetchone("""
    SELECT help_change_quest
    FROM current_state
    WHERE session_id = ?""", (session_id,))

def fetch_current_help_50_50(session_id):
    return fetchone("""
    SELECT help_50_50
    FROM current_state
    WHERE session_id = ?""", (session_id,))

def fetch_current_state_by_user_id(user_id):
    return fetchone("""
    SELECT session_id,
    finished
    FROM current_state cs
    INNER JOIN game_sessions gs
    ON cs.session_id = gs.id
    WHERE gs.user_id = ?
    AND finished = 0""", (user_id,))

def fetch_active_current_states():
    return fetchall("""
    SELECT gs.id,
    u.id,
    u.real_name,
    u.user_name
    FROM current_state cs
    INNER JOIN game_sessions gs
    ON cs.session_id = gs.id
    INNER JOIN users u
    ON u.id = gs.user_id
    WHERE cs.finished = 0""")

def fetch_current_finished(session_id):
    return fetchone("""
    SELECT finished
    FROM current_state
    WHERE session_id = ?""", (session_id,))

def update_help_change_quest(session_id):
    execute_commit("""
    UPDATE current_state
    SET help_change_quest = help_change_quest - ?
    WHERE session_id = ?""", (1, session_id))

def update_help_50_50(session_id):
    execute_commit("""
    UPDATE current_state
    SET help_50_50 = help_50_50 - ?
    WHERE session_id = ?""", (1, session_id))

def finish_session_record(session_id, user_id, final_score, finished_at, spent, won=0):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")

        cur.execute("""
            UPDATE game_sessions
            SET score = ?, 
                finished_at = ?, 
                spent_time = ?
            WHERE id = ?;""", (final_score, finished_at, spent, session_id))

        cur.execute("""
            UPDATE user_profiles
            SET played = played + 1
            WHERE user_id = ?""", (user_id,))

        cur.execute("""
            UPDATE user_profiles
            SET best_score = ?
            WHERE user_id = ?
            AND best_score < ?""", (final_score, user_id, final_score))

        cur.execute("""
            UPDATE user_profiles
            SET overall_score = overall_score + ?
            WHERE user_id = ?""", (final_score, user_id))

        cur.execute("""
            UPDATE user_profiles
            SET won = won + ?
            WHERE user_id = ?""", (won, user_id))

        cur.execute("""
            UPDATE current_state
            SET finished = 1
            WHERE session_id = ?""", (session_id,))

        conn.commit()
    except sqlite3.Error:
        logger.error(f"Failed while finish session for user {user_id}")
        conn.rollback()

        cur.execute("""
        DELETE FROM game_sessions
        WHERE id = ?""", (session_id,))

        conn.commit()
    finally:
        conn.close()

def fetch_active_state_by_session_id(session_id):
    return fetchone("""
    SELECT session_id
    FROM current_state
    WHERE session_id = ?
    AND finished = 0""", (session_id,))

def fetch_session_history():

    return fetchall("""
    SELECT gs.id, 
    u.real_name, 
    u.user_name,
    gs.score, 
    gs.started_at, 
    gs.spent_time
    FROM game_sessions gs
    INNER JOIN users u
    ON u.id = gs.user_id
    WHERE gs.finished_at IS NOT NULL
    ORDER BY gs.id DESC
    LIMIT 10;""")

def insert_answers_history(session_id, question_id,
                        selected_variant_id, answered_at, is_correct):

    execute_commit("""
    INSERT INTO answers_history (session_id, 
    question_id, selected_variant_id, 
    answered_at, is_correct)
    VALUES (?, ?, ?, ?, ?)""", (session_id, question_id,
                                selected_variant_id, answered_at, is_correct))

def fetch_answers_history():

    return fetchall("""
    SELECT gs.id, 
    u.real_name,
    ah.question_id,
    ah.selected_variant_id, 
    ah.answered_at,
    ah.is_correct
    FROM users u
    INNER JOIN game_sessions gs
    ON u.id = gs.user_id
    INNER JOIN answers_history ah
    ON gs.id = ah.session_id""")

def fetch_answers_by_user_id(user_id):

    return fetchall("""
    SELECT gs.id,
    u.real_name,
    u.user_name,
    ah.question_id,
    ah.selected_variant_id,
    av.answer_title,
    ah.answered_at,
    ah.is_correct
    FROM users u
    INNER JOIN game_sessions gs
    ON u.id = gs.user_id
    INNER JOIN answers_history ah
    ON gs.id = ah.session_id
    INNER JOIN answer_variants av
    ON av.id = ah.selected_variant_id
    WHERE u.id = ?
    AND gs.id IN (
        SELECT id
        FROM game_sessions
        ORDER BY id DESC
        LIMIT 15
        )
    ORDER BY gs.id ASC, ah.question_id ASC""", (user_id,))

def fetch_answers_by_session_id(session_id):
    return fetchall("""
    SELECT ah.question_id,
    av.answer_title,
    ah.is_correct
    FROM answers_history ah
    INNER JOIN answer_variants av
    ON ah.selected_variant_id = av.id
    WHERE ah.session_id = ?""", (session_id,))
