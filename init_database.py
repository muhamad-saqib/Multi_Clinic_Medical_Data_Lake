import sqlite3

def create_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clinic TEXT NOT NULL,
        patient_hash TEXT,
        age INTEGER,
        sex TEXT,
        visit_date TEXT,
        diagnosis_code TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    print('Database and table successfully created...')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()