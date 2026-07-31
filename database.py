import sqlite3
import datetime
import time
from datetime import datetime, timedelta

conn = sqlite3.connect("programs.db")
cur = conn.cursor()

# cur.execute(""" CREATE TABLE program (
#             Program TEXT PRIMARY KEY,
#             time INTEGER
#         )""")

 
# cur.execute("PRAGMA foreign_keys = ON;")

# cur.execute("""
#             CREATE TABLE app_usage(
#             id INTEGER PRIMARY KEY,
#             session_id INTEGER NOT NULL,
#             app_name TEXT NOT NULL,
#             start_ts REAL NOT NULL,
#             end_ts REAL NOT NULL,
#             duration REAL NOT NULL,
#             app_web TEXT,
#             FOREIGN KEY (session_id) REFERENCES Session_time(Session_id),
#             UNIQUE (session_id, app_name, app_web)
#             );
#            """)

# row_count = cur.fetchone()[0]

# print(row_count)

# cur.execute(
#         """
          
#         DROP TABLE Settings
#         """




# cur.execute("ALTER TABLE session MODIFY COLUMN session_number INT AUTO_INCREMENT PRIMARY KEY")
# print(cur.fetchall())

# cur.execute("ALTER TABLE session ADD COLUMN session_id_number INT PRIMARY KEY")




cur.execute("Select * FROM app_usage Where session_id = 78 ")
print(cur.fetchall())

conn.commit()
conn.close()