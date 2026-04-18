import sqlite3

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT,
        ai_response TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_lead(name, email, message, ai_response, status):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO leads (name, email, message, ai_response, status)
    VALUES (?, ?, ?, ?, ?)
    """, (name, email, message, ai_response, status))

    conn.commit()
    conn.close()


def get_all_leads():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leads ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data