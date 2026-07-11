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

# cur.execute("SELECT * FROM program")
# print(cur.fetchall())

# cur.execute(
#         """
          
#         DROP TABLE Settings
#         """




cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            break_time INTEGER
        )
            """


)



# cur.execute("Select * FROM Settings")
# print(cur.fetchall())



conn.commit()
conn.close()