import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE chat_messages
ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
""")

conn.commit()
conn.close()

print("timestamp column added!")