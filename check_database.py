import sqlite3
import pandas as pd

# Database check karein
conn = sqlite3.connect('data.db')

# Tables check karein
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("📊 Database Tables:")
print(tables)

# Patients data check karein
patients = pd.read_sql("SELECT * FROM patients", conn)
print(f"\n👥 Patients Records: {len(patients)}")
print(patients)

conn.close()