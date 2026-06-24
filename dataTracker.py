import sqlite3
import win32gui
import win32process
import psutil
import time
import ctypes
import datetime
import threading
import copy
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from collections import defaultdict
from ctypes import wintypes


class Trackon(QThread):
    finished = pyqtSignal()
    finished_sync = pyqtSignal()
    data_uploaded = pyqtSignal(list)
    log_filename = 'window_log.csv'
    def __init__(self):
        super().__init__()
        self.active_data_time = {}
        self.title_dict = defaultdict(dict)
        self.last_title = None
        self.lock = threading.Lock()
        self.start_time = datetime.now()


    def saveDB(self, active_data_dict):
        conn = sqlite3.connect("programs.db")
        cur = conn.cursor()
        # Check if program is inside the db already, and outsource the time spent
        #if it is, then we add the current time spent with the saved time adn return that back to the database

        #checking
        query = """
            INSERT INTO program (Program, time) 
            Values(?, ?)
            ON CONFLICT(Program) DO UPDATE SET time = time + excluded.time
            """
        # Insert puts in the title and program title into the database if it doesn't exist
        #If the conflict on Program(Since it's a primary key)
        #it will just update the time
        cur.executemany(query, active_data_dict.items())
        print("saved into db correctly")
        conn.commit()
        conn.close()
        active_data_dict.clear()


    def saveSBD(self, last_title):

        print(f"{last_title}")
        conn = sqlite3.connect("programs.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")


        query = """
            INSERT INTO subprogram (Program, title, time)
            VALUES(?, ?, ?)
            ON CONFLICT(Program, title) DO UPDATE SET time = time + excluded.time
            """
        
        data_insert = []
        for program_name, subprogram in last_title.items():
            for sub_title, time in subprogram.items():
                data_insert.append((program_name, sub_title, time))


        try:
            cur.executemany(query, data_insert)
            conn.commit()
            print("Success SubProgram DB")
            last_title.clear()    
        except sqlite3.Error as e:
            print(f"Sub DB ERROR: {e}")
            conn.rollback() # If it messes up, it undos any changes 
        finally:
            conn.close()
    




    last_title = None


    


    ## This is what were trying to replace for the constant dictionary time
    ## This will be inside the while loop as
    def run_time(self):
        start_time = datetime.now()

        self.last_title = None
        self.last_exe = None
        self.last_subname = None
        save_start_time = datetime.now()

        def handle_event(hWinEventHook, event, hwnd, idObject, idDChild, dwEventThread, dwmsEventTime):
            nonlocal start_time
            try:
                title = win32gui.GetWindowText(hwnd)
                _,pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                exe_name = process.name().replace(".exe", "")
                

                if not title:
                    title = exe_name
                
                split = title.split("-")
                if (len(split) > 2):
                    subname = split[-2].strip()
                elif len(split) == 2:
                    subname = split[1].strip()
                else:
                    subname = title.strip()

                if self.last_title is None:
                    self.last_title = title
                    self.last_exe =  exe_name
                    self.last_subname = subname
                    return

                if title != self.last_title:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    with self.lock:
                        self.active_data_time[self.last_exe] = (
                            self.active_data_time.get(self.last_exe, 0) + duration
                        )

                        if self.last_exe not in self.title_dict:
                            self.title_dict[self.last_exe] = {}
                        self.title_dict[self.last_exe][self.last_subname] = (
                            self.title_dict[self.last_exe].get(self.last_subname, 0) + duration
                        )

                    self.last_title = title
                    self.last_exe = exe_name
                    self.last_subname = subname
                    start_time = end_time
                    print(f"Window switched to: {title}")

        

            except Exception:
                pass


        def flush_check():
                    nonlocal save_start_time
                    while True:
                        time.sleep(30)
                        if datetime.now() >= save_start_time + timedelta(minutes = 5):
                            with self.lock:
                                parent_copy = copy.deepcopy(self.active_data_time)
                                child_copy = copy.deepcopy(self.title_dict)
                            
                            self.saveDB(parent_copy)
                            self.saveSBD(child_copy)
                            print("Success after 5 minutes")
                            save_start_time = datetime.now()
        
        threading.Thread(target=flush_check, daemon =True).start()


        WinEventProc = ctypes.WINFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD
        )
        callback = WinEventProc(handle_event)

        hook = ctypes.windll.user32.SetWinEventHook(
            0x0003,
            0x0003,
            None,
            callback,
            0, 0,
            0x0000
        )

        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessage(ctypes.byref(msg))
        
        ctypes.windll.user32.UnhookWinEvent(hook)




if __name__ == "__main__":
    tracker = Trackon()
    tracker.start_tracking()




