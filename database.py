import sqlite3

conn = sqlite3.connect("programs.db")
cur = conn.cursor()

# cur.execute(""" CREATE TABLE program (
#             Program TEXT PRIMARY KEY,
#             time INTEGER
#         )""")

 
# cur.execute("PRAGMA foreign_keys = ON;")
# cur.execute("""
#             CREATE TABLE subprogram(
#             Program TEXT,
#             title TEXT,
#             time INTEGER,
#             PRIMARY KEY (Program, title),
#             FOREIGN KEY (Program) REFERENCES program(Program)
#             );
#             """)

# cur.execute("ALTER TABLE Session ADD COLUMN session_title TEXT")
# ?
# row_count = cur.fetchone()[0]

# print(row_count)

#Add, ID, title, notes or video (IDK HOW)

# cur.execute(
#         """
          
#         DROP TABLE Settings
#         """




# cur.execute("ALTER TABLE session MODIFY COLUMN session_number INT AUTO_INCREMENT PRIMARY KEY")
# print(cur.fetchall())

# cur.execute("ALTER TABLE session ADD COLUMN session_id_number INT PRIMARY KEY")
# cur.execute("DROP TABLE Session_time")
# cur.execute(
#     """
#         CREATE TABLE Session_time (
#             session_id INTEGER PRIMARY KEY,
#             date TEXT ,
#             session_time INTEGER
#         );
#     """
# )


cur.execute("""
SELECT date, session_time 
FROM Session_time
WHERE strftime('%w', date) = '2'
ORDER BY date;
""")
print(cur.fetchall())



conn.commit()
conn.close()