
import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

DB_PATH = Path(__file__).parent / "research_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            created_at TEXT NOT NULL,
            search_results TEXT,
            scraped_content TEXT,
            report TEXT,
            feedback TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# Create database automatically
initialize_database()


# ============================================================
# SAVE SEARCH
# ============================================================

def save_search(
    topic: str,
    search_results: str,
    scraped_content: str,
    report: str,
    feedback: str
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO searches (
            topic,
            created_at,
            search_results,
            scraped_content,
            report,
            feedback
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            topic,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            search_results,
            scraped_content,
            report,
            feedback
        )
    )

    conn.commit()

    search_id = cursor.lastrowid

    conn.close()

    return search_id


# ============================================================
# GET ALL SEARCHES
# ============================================================

def get_search_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            created_at
        FROM searches
        ORDER BY id DESC
        """
    )

    searches = cursor.fetchall()

    conn.close()

    return searches


# ============================================================
# GET ONE SEARCH
# ============================================================

def get_search(search_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            created_at,
            search_results,
            scraped_content,
            report,
            feedback
        FROM searches
        WHERE id = ?
        """,
        (search_id,)
    )

    search = cursor.fetchone()

    conn.close()

    if not search:
        return None

    return {
        "id": search[0],
        "topic": search[1],
        "created_at": search[2],
        "search_results": search[3],
        "scraped_content": search[4],
        "report": search[5],
        "feedback": search[6]
    }


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM searches")

    conn.commit()
    conn.close()

