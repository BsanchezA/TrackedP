import datetime
import sys
from tkinter.font import Font
import dataTracker
import sqlite3
from PyQt6 import QtWidgets
from datetime import date
from PyQt6.QtCore import QSize, QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QApplication, QCheckBox, QGridLayout, QLineEdit, QMainWindow, QPushButton, QSpinBox, QToolButton, QWidget, QStackedWidget,QVBoxLayout, QLabel, QHeaderView,  QTableView, QStyle, QHBoxLayout
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery, QSqlQueryModel

class MainWindow(QMainWindow):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Trackon App")
        self.conn = conn
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        container = QWidget()
        layout = QGridLayout()
        #adding the screen time window 
        self.App_data_window = secondWindow()

        # All buttons created
        self.button = QPushButton("Sync")
        self.button2 = QPushButton("Start Timer")
        self.button3 = QPushButton("End Timer")
        self.button4 = QPushButton("Activty In Depth")
        self.button5 = QPushButton("Study Mode")
        self.button_settings = QPushButton("Settings")


        self.setGeometry(600, 600, 680, 600)

        #Add the widgets here
        layout.addWidget(self.button2, 0, 0)
        layout.addWidget(self.button, 0, 1)
        layout.addWidget(self.button3, 0, 2)
        layout.addWidget(self.button4,0, 3)
        layout.addWidget(self.button5, 0, 4)
        layout.addWidget(self.button_settings, 0, 5)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        #Connect the buttons here
        self.button.clicked.connect(self.sync)
        self.button2.clicked.connect(self.start_click)
        self.button3.clicked.connect(self.end_timer)
        self.button4.clicked.connect(self.toggle_activity)
        self.button5.clicked.connect(self.gotoStudy)
        self.button_settings.clicked.connect(self.go_settings)


        self.Track_helper = dataTracker.Trackon()
        self.datafornow = {}

        #This adds the Label of the date (I'll personalize this later on)
        today = date.today()
        format_two = today.strftime("%B %d, %Y")
        label_one = QLabel(f"Today is {format_two}", self)
        label_one.setWordWrap(True)


        #UI FONT DOWNLOAD
        font_id = QFontDatabase.addApplicationFont("DM_Sans/static/DMSans-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font_family = font_families[0]
            dm_sans_font = QFont(font_family, 20)
        else:
            print("Failed to load font, going default")
            dm_sans_font = QFont("Arial", 16)
        

        


        label_one.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 22px;
            font-weight: 500;
            padding-bottom: 10px
            """
        )
        
        layout.addWidget(label_one, 1,0, 1, 2)

        self.label_sesssion_completed = QLabel()
        self.load_session()
        layout.addWidget(self.label_sesssion_completed, 1, 5)

        container.setLayout(layout)
        self.setCentralWidget(container)




    def start_click(self):

        if getattr(self.Track_helper, "_started", False):
            return
        self.Track_helper._started = True

        self.button2.setEnabled(False)
        self.Track_helper.start()

        self.timer_window = TimerWindow_Popup(conn)
        self.timer_window.session_completed_time.connect(self._on_timer_session_done)

        index = self.stack.addWidget(self.timer_window)
        self.stack.setCurrentIndex(index)


    def _on_timer_session_done(self, result: int):
        self.Track_helper._started = False
        self.Track_helper.stop_tracking()
        self.Track_helper.wait()

        
        self.mark_session_completed(result)
        self.load_session()

        self.stack.removeWidget(self.timer_window)
        self.timer_window.deleteLater()
        self.timer_window = None

        self.button2.setEnabled(True)
        self.stack.setCurrentIndex(0)

    # This relates to the sessions completed of studying sessions
    def mark_session_completed(self, result):
        query = QSqlQuery(self.conn)
        query.prepare("""INSERT INTO session (date, session_marked) 
                      VALUES (?, ?)
                      ON CONFLICT(date) DO UPDATE SET
                        session_marked = session_marked + excluded.session_marked
                      """)
        query.addBindValue(date.today().isoformat())
        query.addBindValue(result)
        query.exec()
    #Loads the time of the session since this makes more sense
    def load_session(self):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT session_marked FROM session WHERE date = ?")
        query.addBindValue(date.today().isoformat())
        query.exec()
        if query.next():
            session_counted = query.value(0)
        else:
            session_counted = 0

        timenow = str(datetime.timedelta(seconds = session_counted))
        
        self.label_sesssion_completed.setText(f"Time Spent Studying: {timenow}")
        self.label_sesssion_completed.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 18px;
            font-weight: 400;
            padding-bottom: 10px
            """
        )


    def sync(self):
        self.Track_helper.saveDB(self.Track_helper.active_data_time)
        self.Track_helper.saveSBD(self.Track_helper.title_dict)

    
    def end_timer(self):
        try:
            self.Track_helper.saveDB(self.Track_helper.active_data_time)
            self.Track_helper.saveSBD(self.Track_helper.title_dict)
        finally:
            QApplication.instance().quit()

    def toggle_activity(self, checked):
        if self.App_data_window.isVisible():
            self.App_data_window.hide()
        else:
            self.App_data_window.show()

    def gotoStudy(self):
        widget.setCurrentIndex(1)

    def go_settings(self):
        widget.setCurrentIndex(2)



class TimerWindow_Popup(QWidget):
    session_completed_time = pyqtSignal(int)


    def __init__(self, conn,  buffer_seconds = 30 ,parent = None):
        super().__init__(parent)
        # self.stackedWidget2 = QStackedWidget()
        # #maybe if not, delete this
        # self.setCentra
        self.conn = conn
        self.buffer_seconds = buffer_seconds
        self.elapsed_seconds = 0
        self.in_buffer = True
        self.elapsed_start = False



        self.skip_pressed = False
        self.break_pressed = False


        self.break_going_seconds = self.load_break_seconds()


        self.time_label = QLabel(self._format_time(self.buffer_seconds))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        
        self.skip_button = QPushButton("Skip")

        end_button = QPushButton("End Session")
        end_button.clicked.connect(self.end_session)

        break_button = QPushButton("Break")
        break_button.clicked.connect(self.break_connection)
        break_button.setFixedSize(70, 30)

        topPosition = QHBoxLayout()
        topPosition.addStretch()
        topPosition.addWidget(break_button)


        layout = QVBoxLayout(self)
        layout.addLayout(topPosition)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addStretch()
        layout.addWidget(self.skip_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(end_button)

        if self.in_buffer:
            self.time_label.setStyleSheet("font-size: 26pt; color: yellow")
            self.skip_button.clicked.connect(self.skipping)
            self.skip_button.setFixedSize(70, 30)
        

        self.qtimer = QTimer(self)
        self.qtimer.setInterval(1000)
        self.qtimer.timeout.connect(self._tick)
        self.qtimer.start()

    def skipping(self):
        self.skip_pressed= True


    def _tick(self):
        if self.in_buffer:
            if (self.skip_pressed):
                self.in_buffer = False
                self.elapsed_start = True
                self.time_label.setStyleSheet("font-size: 26pt; color: white")
                self.skip_button.hide()
                self.elapsed_seconds = 0
                self.time_label.setText(self._format_time(self.elapsed_seconds))

                return
            self.buffer_seconds -= 1
            self.time_label.setText(self._format_time(self.buffer_seconds))
            if self.buffer_seconds <= 0:
                self.in_buffer = False
                self.elapsed_start = True
                self.time_label.setStyleSheet("font-size: 26pt; color: white")
                self.skip_button.hide()
                self.elapsed_seconds = 0
                self.time_label.setText(self._format_time(self.elapsed_seconds))
        
        elif self.elapsed_start:
            self.elapsed_seconds += 1
            self.time_label.setStyleSheet("font-size: 26pt; color: white")
            self.time_label.setText(self._format_time(self.elapsed_seconds))
            if (self.break_pressed):
                self.qtimer.timeout.connect(self.break_connection)
        elif self.break_pressed:
            self.break_going_seconds -= 1
            self.time_label.setStyleSheet("font-size: 26pt; color: green")
            self.time_label.setText(self._format_time(self.break_going_seconds))
            if (self.break_going_seconds <= 0):
                self.break_pressed = False
                self.elapsed_start = True




    def end_session(self):
        self.qtimer.stop()

        # This is emitting the elapsed time which is adding to the session total
        #This should be the total time spent studying per week
        #I need to seperate 2 things now
        self.session_completed_time.emit(self.elapsed_seconds)
    
    def break_connection(self):
        self.break_pressed = True
        self.elapsed_start = False

    def load_break_seconds(self):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT break_time FROM Settings")
        query.exec()
        if query.next():
            return query.value(0) * 60
        return 120 

    @staticmethod
    def _format_time(seconds: int) -> str:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"
        

class settings_window(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setMinimumSize(500, 800)
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_back_home = QPushButton("Back Home")
        layout.addWidget(
            self.button_back_home, 0, 0,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        
        self.button_back_home.clicked.connect(self.back_home)

        self.Notifications_handle = QLabel("Modify Notifications Below")
        self.Notifications_handle.setStyleSheet(
            """
                font-family = 'DM Sans';
                font-size: 12 px;
                color: #CBCBCB
            """
        )
        layout.addWidget(
            self.Notifications_handle, 1, 0,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        self.break_time_adjuster = QSpinBox()
        self.break_time_adjuster.setMinimum(2)
        self.break_time_adjuster.setMaximum(30)

        self.break_time_adjuster.setSuffix(" Mins")

        self.break_time_adjuster.valueChanged.connect(self.value_changed)


        layout.addWidget(
            self.break_time_adjuster, 1, 1,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        self.apply_button = QPushButton("Apply")
        layout.addWidget(
            self.apply_button, 5,0,
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
        self.apply_button.clicked.connect(self.apply_settings)

        self.load_settings()




    def apply_settings(self):
        query = QSqlQuery(self.conn)
        query.prepare("""INSERT INTO Settings (id, break_time) 
                      VALUES (1, ?)
                      ON CONFLICT(id) DO UPDATE SET
                        break_time = excluded.break_time
                      """)
        query.addBindValue(self.break_time_adjuster.value())
        if not query.exec():
            print("Apply settings failed: ", query.lastError().text())

    def load_settings(self):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT break_time FROM Settings")
        query.exec()
        if query.next():
            self.break_time_adjuster.setValue(query.value(0))

    def value_changed(self, new_value):
        self.current_break_time = new_value

        


    def back_home(self):
        widget.setCurrentIndex(0)




class secondWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Detailed Information")
        self.resize(600, 400)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentIndex(0)
            
        Conn_Name = "secon_window_conn"
        if QSqlDatabase.contains(Conn_Name):
            self.conn = QSqlDatabase.database(Conn_Name)
        else:
            self.conn = QSqlDatabase.addDatabase("QSQLITE", Conn_Name)
            self.conn.setDatabaseName("programs.db")

        if not self.conn.isOpen():
            if not self.conn.open():
                print("Failed to open DB:", self.conn.lastError().text())

        self.create_table_page()

    def create_table_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.projectModel = QSqlQueryModel()
        self.projectModel.setQuery("""
                                   SELECT
                                   Program,
                                   printf('%02d:%02d:%02d',
                                   CAST(time / 3600 AS INT),
                                   CAST(time % 3600 / 60 AS INT),
                                   CAST(time % 60 AS INT)
                                   ) AS Duration
                                   From program                                  
                                   """, self.conn)

        self.projectView = QTableView()
        self.projectView.setModel(self.projectModel)
        layout.addWidget(self.projectView, stretch=1)
        self.projectView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stacked_widget.addWidget(page)
            

class studyWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Study Window")
        self.setMinimumSize(800, 800)
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)


        self.buttonone = QPushButton("Back Home")
        layout.addWidget(self.buttonone, alignment= Qt.AlignmentFlag.AlignCenter)
        self.buttonone.clicked.connect(self.backhome)

        work_space = QVBoxLayout()

               
        today = date.today()
        format_two = today.strftime("%B %d, %Y")
        label_one = QLabel(f"Welcome, Today is {format_two}", self)
        label_one.setWordWrap(True)
        work_space.addWidget(label_one)

        to_do = QLabel("Add an Objective For Today", parent = self)
        to_do.setWordWrap(True)
        self.bottom_line_edit = QLineEdit(parent = self)
        work_space.addWidget(to_do)
        work_space.addWidget(self.bottom_line_edit)
        self.work_space = work_space
        self.buttonO = QPushButton("Add")
        work_space.addWidget(self.buttonO, alignment=Qt.AlignmentFlag.AlignBottom)
        self.created_check = []
        self.buttonO.clicked.connect(self.updatecheck)

        layout.addLayout(work_space)




        layout.addWidget(self.buttonone, alignment= Qt.AlignmentFlag.AlignBottom)
        self.buttonone.clicked.connect(self.backhome)
        self.load_today_goals()
        
    def updatecheck(self):
        if len(self.created_check) >= 3:
            return
        obj = self.bottom_line_edit.text().strip()
        if not obj:
            return
        

        checkbox = QCheckBox(text = obj)
        checkbox.stateChanged.connect(lambda state, o = obj: self.save_goal_state(o, state))
        self.created_check.append(checkbox)
        self.work_space.addWidget(checkbox)


        self.bottom_line_edit.clear()
        self.save_goal(obj)

    def save_goal(self, obj): # new goal
        query = QSqlQuery(self.conn)
        query.prepare("INSERT INTO Goals (date, objective, completed) VALUES (?, ?, 0)")
        query.addBindValue(date.today().isoformat())
        query.addBindValue(obj)
        query.exec()


    def save_goal_state(self, obj, state): #updating goal state in SQL (completing a thing)
        query = QSqlQuery(self.conn)
        query.prepare("UPDATE Goals SET completed = ? WHERE date = ? AND objective = ?")
        query.addBindValue(1 if state else 0)
        query.bindValue(date.today().isoformat())
        query.addBindValue(obj)
        query.exec()

    def load_today_goals(self):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT objective, completed FROM Goals WHERE date = ?")
        query.addBindValue(date.today().isoformat())
        query.exec()
        while query.next():
            obj = query.value(0)
            completed = bool(query.value(1))
            checkbox = QCheckBox(text = obj)
            checkbox.setChecked(completed)
            checkbox.stateChanged.connect(lambda state, o=obj: self.save_goal_state(o, state))
            self.created_check.append(checkbox)
            self.work_space.addWidget(checkbox)



    def backhome(self):
        widget.setCurrentIndex(0)
        


app = QApplication(sys.argv)

conn = QSqlDatabase.addDatabase("QSQLITE", "app_conn")
conn.setDatabaseName("programs.db")
conn.open()

track_helper = dataTracker.Trackon()

widget = QtWidgets.QStackedWidget()
main_window = MainWindow(widget)
study_window = studyWindow(conn)
settings = settings_window(conn)

widget.addWidget(main_window)
widget.addWidget(study_window)
widget.addWidget(settings)
widget.setCurrentIndex(0)  # MAIN WINDOW IS 0 since i put it first
widget.show()

# MAIN WINOW = 0 , STUDY WINDOW = 1 , SETTINGS WINDOW = 2

sys.exit(app.exec())
