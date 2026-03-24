import sqlite3

conn = sqlite3.connect("healthgenie.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

conn.commit()
conn.close()

print("is_admin column added!")