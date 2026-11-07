import datetime
import sys
import pyqtgraph as pg
from tkinter.font import Font
import dataTracker
import sqlite3
from collections import defaultdict
from PyQt6 import QtWidgets
from datetime import date
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, QSize, QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QGridLayout, QInputDialog, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QScrollBar, QSpinBox, QTextEdit, QToolButton, QWidget, QStackedWidget,QVBoxLayout, QLabel, QHeaderView,  QTableView, QStyle, QHBoxLayout, QVBoxLayout
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery, QSqlQueryModel

class MainWindow(QMainWindow):
    update_bar_graph = pyqtSignal()
    data_sent = pyqtSignal(int)
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Trackon App")
        self.conn = conn
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.id_stack = []

        container = QWidget()
        main_layout = QVBoxLayout()  # top-level row stack

        #  Row 0: Top button bar
        Top_Button_layout = QHBoxLayout()

        # adding the screen time window
        self.App_data_window = secondWindow()

        # All buttons created
        self.button2 = QPushButton("Start Timer")
        self.button4 = QPushButton("Activty In Depth")
        self.button5 = QPushButton("Productivity Peformance")
        self.button_settings = QPushButton("Settings")
        self.add_task_button = QPushButton("Add/Modify Tasks")

        self.setGeometry(600, 600, 680, 600)

        Top_Button_layout.addWidget(self.button2)
        Top_Button_layout.addWidget(self.button4)
        Top_Button_layout.addWidget(self.button5)
        Top_Button_layout.addWidget(self.add_task_button)
        Top_Button_layout.addWidget(self.button_settings)

        Top_Button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Connect the buttons here
        self.button2.clicked.connect(self.start_click)
        self.button4.clicked.connect(self.toggle_activity)
        self.button5.clicked.connect(self.gotoStudy)
        self.add_task_button.clicked.connect(self.opening_task_popup)
        self.button_settings.clicked.connect(self.go_settings)

        main_layout.addLayout(Top_Button_layout)

        self.Track_helper = dataTracker.Trackon()
        self.datafornow = {}

        # Row 1: Date label + session-completed label 
        date_row = QHBoxLayout()
        today = date.today()
        format_two = today.strftime("%B %d, %Y")
        label_one = QLabel(f"Today is {format_two}", self)
        label_one.setWordWrap(True)

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

        self.label_sesssion_completed = QLabel()
        self.load_session()

        date_row.addWidget(label_one, alignment=Qt.AlignmentFlag.AlignTop)
        date_row.addStretch()
        date_row.addWidget(self.label_sesssion_completed, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(date_row)

        #Row 2: Tasks header 
        self.created_check = []
        print(self.created_check)
        self.top_3_goals = QLabel("Todays Tasks :")
        self.top_3_goals.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 18px;
            font-weight: 500;
            padding-bottom: 10px
            """
        )
        main_layout.addWidget(
            self.top_3_goals,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        # Row 3: Workspace 
        self.workspace = QVBoxLayout()
        main_layout.addLayout(self.workspace)
        main_layout.addStretch()
    
        #add strech is what keeps everything together after adding, this should be placed after adding all rows of information

        # Row 4: Bar Graph 
        main_layout.addLayout(self.build_bar_row(self.build_bar_analysis()))







        container.setLayout(main_layout)



        self.load_today_goals()

        self.setCentralWidget(container)

    def build_bar_row(self,  control_widget):
            row = QVBoxLayout()
            row.addStretch()
            row.addWidget(control_widget, alignment=Qt.AlignmentFlag.AlignVCenter)
            row.addStretch()
            return row


    def build_bar_analysis(self):
        self.weekly_rating = pg.PlotWidget()
        hours = self.get_weekly_hours()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        x = list(range(len(days)))

        bar = pg.BarGraphItem(x=x, height = hours, width = 0.6, brush = 'w')
        self.weekly_rating.addItem(bar)

        ticks = [list(zip(x, days))]
        self.weekly_rating.getAxis('bottom').setTicks(ticks)

        #Customizing the bar to be view only and other visual gimmicks
        self.weekly_rating.setLabel('left', 'Hours Studied')
        self.weekly_rating.setYRange(0, max(hours) + 1)
        self.weekly_rating.showGrid(y=True, alpha = 0.3)
        self.weekly_rating.hideButtons()
        self.weekly_rating.setMenuEnabled(False)
        self.weekly_rating.setMouseEnabled(x=False, y=False)
        self.weekly_rating.getViewBox().setMouseEnabled(x=False, y=False)
        print("hours: ", hours)
        return self.weekly_rating





    def get_weekly_hours(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours = {day: 0.0 for day in days}

        query = QSqlQuery(self.conn)
        query.exec(
            """ 
                SELECT strftime('%w', date) as day_num, SUM(session_time)
                FROM Session_time
                Where date >= date('now', 'weekday 0', '-6 days')
                GROUP BY day_num
            """
        )

        while query.next():
            day_num = int(query.value(0))
            total_second = query.value(1)
            total_seconds = int(total_second) if total_second not in (None, '') else 0
            day_name = days[(day_num - 1) % 7]
            hours[day_name] = total_seconds / 3600.0

        return [hours[day] for day in days]

    def update_bar_graph(self):
        ## GETS THE SIGNAL WHEN SESSION IS DONE HERE
        print("bar should be updated")
        self.weekly_rating.clear()
        hours = self.get_weekly_hours()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        x = list(range(len(days)))
        bar = pg.BarGraphItem(x=x, height = hours, width=0.6, brush = 'w')
        self.weekly_rating.addItem(bar)
        ticks = [list(zip(x, days))]
        self.weekly_rating.getAxis('bottom').setTicks(ticks)
        print("hours: ", hours)

     
 

    def start_click(self):

        if getattr(self.Track_helper, "_started", False):
            return
        self.Track_helper._started = True

        self.button2.setEnabled(False)
        self.Track_helper.start()
        self.start_reference = self.Track_helper.reference_start

        self.timer_window = TimerWindow_Popup(conn)
        #ONCE THESE SIGNALS ARE RECIEVED (END SESSION HAS BEEN CLICKED)
        self.timer_window.session_completed_time.connect(self._on_timer_session_done)
        self.timer_window.session_to_review.connect(self.switch_to_review_window)
        self.timer_window.session_update_before_close.connect(self.sync)


        index = self.stack.addWidget(self.timer_window)
        self.stack.setCurrentIndex(index)

    def start_(self):
        query = QSqlQuery(self.conn)
        query.prepare("INSERT INTO Session_time (date,start_time) VALUES (?, ?)")
        query.addBindValue(date.today().isoformat())
        query.addBindValue(datetime.now().timestamp())

        if not query.exec():
            print("Failed to start session", query.lastError().text())
            return

        self.recieved_for_SBD = query.lastInsertId()
        self.Track_helper.set_session_id(self.recieved_for_SBD)


        print("Just created: ", self.recieved_for_SBD)

    def switch_to_review_window(self):
        self.review_window = review_Popup(self)     

        #This prompts going to the text window
        self.review_window.session_to_text.connect(self.go_to_text_window)

        #This prompts to go back home when pressing skip
        self.review_window.completed_review_popup.connect(self.review_cleanup)
        
        
        index_review = self.stack.addWidget(self.review_window)
        self.stack.setCurrentIndex(index_review)
        print(self.stack)


    def review_cleanup(self):
        self.stack.removeWidget(self.review_window)
        self.review_window.deleteLater()
        self.review_window = None
        self.stack.setCurrentIndex(0)

    def go_to_text_window(self):
        self.text_review = text_review(conn, self)

        #This prompts to clean up after finished with the text notes
        self.text_review.text_done.connect(self.text_cleanup)

        index_text = self.stack.addWidget(self.text_review)
        self.stack.setCurrentIndex(index_text)

    def text_cleanup(self):
        self.stack.removeWidget(self.text_review)
        self.text_review.deleteLater()
        self.text_review = None
        self.stack.setCurrentIndex(0)
        

    def _on_timer_session_done(self, result: int): 
        self.Track_helper._started = False
        self.Track_helper.stop_tracking()
        self.Track_helper.wait()

        
        self.id_stack.append(self.mark_session_completed(result))
        self.load_session()


        self.stack.removeWidget(self.timer_window)
        self.timer_window.deleteLater()
        self.timer_window = None

        self.button2.setEnabled(True)
        self.stack.setCurrentIndex(0)

    # This relates to the sessions completed of studying sessions
    def mark_session_completed(self, result):
        query = QSqlQuery(self.conn)
        query.prepare("""UPDATE Session_time  
                        SET end_time = ?, session_time = ?
                        WHERE session_id = ?
                      """)
        query.addBindValue(datetime.now().timestamp())
        query.addBindValue(result)
        query.addBindValue(self.recieved_for_SBD)
        if not query.exec():
            print("Insert failed (Mark sessino completed):", query.lastError().text())
            return None

        recent_session = query.lastInsertId()
        self.update_bar_graph()
        return recent_session



    def load_session(self):
        query = QSqlQuery(self.conn)
        today = date.today().isoformat()
        query.prepare(""" 
            SELECT date, SUM(session_time) AS total_time
            FROM Session_time
            WHERE date = ?
            GROUP BY date
        """)
        query.addBindValue(today)
        query.exec()
        if query.next():
            raw_data = query.value(1)
        else:
            raw_data = 0
        
        session_counted = int(raw_data) if raw_data not in (None, '') else 0
        timenow = str(timedelta(seconds = session_counted))
        
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
        self.end_now = datetime.now()
        self.started = self.Track_helper.reference_start
        self.Track_helper.saveSBD(self.Track_helper.title_dict, self.started, self.end_now)

    

    def toggle_activity(self, checked):
        if self.App_data_window.isVisible():
            self.App_data_window.hide()
        else:
            self.App_data_window.show()

    def gotoStudy(self):
        self.Study_window = studyWindow(conn)
        self.Study_window.study_done.connect(self.study_cleanup)

        index_study = self.stack.addWidget(self.Study_window)
        self.stack.setCurrentIndex(index_study)

    def study_cleanup(self):
        self.stack.removeWidget(self.Study_window)
        self.Study_window.deleteLater()
        self.Study_window = None
        self.stack.setCurrentIndex(0)
    
    def go_settings(self):
        widget.setCurrentIndex(2)

    def opening_task_popup(self):
        dialog = task_pop_up(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_text = dialog.get_text_from_task()
            if task_text.strip():
                self.updatecheck(task_text.strip())
        
    def updatecheck(self, obj):
        if len(self.created_check) >= 3:
            QMessageBox.warning(None, "Warning", "You already have 3 tasks, Focus on those")
            return
        if not obj:
            return
        

        checkbox = QCheckBox(text = obj)
        checkbox.stateChanged.connect(lambda state, o = obj: self.save_goal_state(o, state))
        self.created_check.append(checkbox)
        self.workspace.addWidget(checkbox, Qt.AlignmentFlag.AlignLeft)


        # self.input_task.clear()
        self.save_goal(obj)

    def save_goal_state(self, obj, state): #updating goal state in SQL (completing a thing)
        query = QSqlQuery(self.conn)
        query.prepare("UPDATE Goals SET completed = ? WHERE date = ? AND objective = ?")
        query.addBindValue(1 if state else 0)
        query.addBindValue(date.today().isoformat())
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
            self.workspace.addWidget(checkbox)

    def save_goal(self, obj): # new goal
        query = QSqlQuery(self.conn)
        query.prepare("INSERT INTO Goals (date, objective, completed) VALUES (?, ?, 0)")
        query.addBindValue(date.today().isoformat())
        query.addBindValue(obj)
        query.exec()




class task_pop_up(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        user_prompt = QLabel("Add a Task")
        self.input_task = QLineEdit(self)
        self.button = QPushButton("Add", self)
        layout.addWidget(user_prompt)
        layout.addWidget(self.input_task)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.bridge_connect)

    def bridge_connect(self):
        if self.input_task.text().strip():
            self.accept()
        else:
            self.input.setPlaceholderText("Task has be to inputted")

    def get_text_from_task(self):
        place = self.input_task.text()
        self.input_task.clear()
        return place 


class TimerWindow_Popup(QWidget):
    session_completed_time = pyqtSignal(int)
    session_to_review = pyqtSignal()
    session_update = pyqtSignal()
    session_update_before_close = pyqtSignal()


    def __init__(self, conn,  buffer_seconds = 30 ,parent = None):
        super().__init__(parent)
        self.conn = conn
        self.buffer_seconds = buffer_seconds
        self.elapsed_seconds = 0
        self.in_buffer = True
        self.elapsed_start = False
        self.review_flag = False
        self.title_dict = defaultdict(dict)
        self.review_session_opened = review_Popup(self)
        main_window.start_()
        



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


        self.timer_layout = QVBoxLayout(self)
        self.timer_layout.addLayout(topPosition)
        self.timer_layout.addStretch()
        self.timer_layout.addWidget(self.time_label)
        self.timer_layout.addStretch()
        self.timer_layout.addWidget(self.skip_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.timer_layout.addWidget(end_button)

        if self.in_buffer:
            self.time_label.setStyleSheet("font-size: 26pt; color: yellow")
            self.skip_button.clicked.connect(self.skipping)
            self.skip_button.setFixedSize(70, 30)
        

        self.qtimer = QTimer(self)
        self.qtimer.setInterval(1000)
        self.qtimer.timeout.connect(self._tick)
        self.qtimer.start()
        if (self.review_flag):
            self.review_session_page()

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
        self.session_update_before_close.emit()
        # sends the signal to update the bar graph with new session data
        self.session_update.emit()
        #sends the signal to update to main window and save the data to display
        self.session_completed_time.emit(self.elapsed_seconds)
        #if this signal is sent, we instead of main window, go to the review window
        if (self.in_buffer == False):
            self.session_to_review.emit()
        


        return
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
        
class review_Popup(QWidget):
    session_to_text = pyqtSignal()
    session_to_video = pyqtSignal()
    completed_review_popup = pyqtSignal()
    def __init__(self, main_window):
        super().__init__()
        self.text_flag = False
        self.skip_flag = False
        layout = QVBoxLayout(self)
        layout.addStretch()

        self.skip_review_button = QPushButton("Skip")
        self.text_review = QPushButton("Note")
        self.video_review = QPushButton("Video")

        self.skip_review_button.clicked.connect(self.skip_home)
        self.text_review.clicked.connect(self.text_page)

        middle_position = QHBoxLayout()
        middle_position.addStretch()
        middle_position.addWidget(self.text_review)
        middle_position.addWidget(self.video_review)
        middle_position.addWidget(self.skip_review_button)
        middle_position.addStretch()



        layout.addLayout(middle_position)
        layout.addStretch()

    def text_page(self):
        print("Going to text ...")
        self.text_flag = True
        self.session_to_text.emit()

    def skip_home(self):
        print("Emitted and going back home ... ")
        self.completed_review_popup.emit()

class text_review(QWidget):
    text_done = pyqtSignal()
    def __init__(self, conn, main_win):
        super().__init__()
        self.conn = conn
        self.main_win = main_window
        self.final_id = self.main_win.id_stack.pop()


        layout = QVBoxLayout(self)

        self.top_layout = QHBoxLayout()

        self.title = QLineEdit()
        self.title.setPlaceholderText(f"Session # {self.final_id}")
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.done_activate)
        self.top_layout.addWidget(self.title)

        layout.addLayout(self.top_layout)
        layout.addStretch()

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Review what went over during the session ...")

        self.middle_layout = QHBoxLayout()
        self.middle_layout.addWidget(self.notes)
        layout.addLayout(self.middle_layout)
        layout.addStretch()
        layout.addWidget(self.done_button)



    def get_most_recent_id(self, result_id: int):
        self.stack_text.append(result_id)

    def save_title_and_notes(self, session_id_created):
        title_session = self.title.text()
        complete_notes = self.notes.toPlainText()

        query = QSqlQuery(self.conn)
        query.prepare("""INSERT INTO Session_information (session_title,  session_notes, session_id) 
                      VALUES (?, ?, ?)
                      """)
        query.addBindValue(title_session)
        query.addBindValue(complete_notes)
        query.addBindValue(session_id_created) 
        query.exec()


    def done_activate(self):
        print("Text done, going back home ...")
        self.save_title_and_notes(self.final_id)
        self.final_id = None
        self.text_done.emit()

class settings_window(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setMinimumSize(500, 800)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(12)


        self.button_back_home = QPushButton("Back Home")
        self.button_back_home.clicked.connect(self.back_home)
        main_layout.addWidget(
            self.button_back_home,
            alignment=Qt.AlignmentFlag.AlignLeft
        )
        

        self.Notifications_handle = QLabel("Modify Notifications Below")
        self.Notifications_handle.setStyleSheet(
            """
                font-family: 'DM Sans';
                font-size: 12 px;
                color: #CBCBCB
            """
        )
        main_layout.addWidget(
            self.Notifications_handle,
            alignment=Qt.AlignmentFlag.AlignLeft 
        )

        main_layout.addLayout(self.make_setting_row("Change Break Time", self.build_break_time_adjuster()))

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)

        app_explain = QLabel("Modify Applications / Websites to be banned when a study session is ocurring")
        app_explain.setStyleSheet(
            """
                            font-family: 'DM Sans';
                            font-size: 12 px;
                            color: #CBCBCB
         """

        )
        main_layout.addWidget(app_explain)


       


        apply_row = QHBoxLayout()
        apply_row.addStretch()
        apply_row.addWidget(self.apply_button)
        apply_row.addStretch()
        main_layout.addLayout(apply_row)


        self.load_settings()

    def make_setting_row(self, label_text, control_widget):
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        row.addWidget(label, alignment=Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(control_widget, alignment=Qt.AlignmentFlag.AlignVCenter)
        row.addStretch()
        return row
    

    def build_break_time_adjuster(self):
        self.break_time_adjuster = QSpinBox()
        self.break_time_adjuster.setMinimum(2)
        self.break_time_adjuster.setMaximum(30)
        self.break_time_adjuster.setSuffix(" Mins")
        self.break_time_adjuster.valueChanged.connect(self.value_changed)
        return self.break_time_adjuster




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
            
class studyWindow(QWidget):
    study_done = pyqtSignal()
    open_this = pyqtSignal(str)
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Study Window")
        self.setMinimumSize(800, 800)
        self.session_win = Session_Overview_Page(conn, self)

        layout = QVBoxLayout(self)


        self.workspace = QHBoxLayout()
        self.window_Label = QLabel("View Previous Logs")
        self.window_Label.setStyleSheet(
                    """
                        font-family: 'DM Sans';
                        font-size: 18 px;
                        font-weight: 500;
                        color: #CBCBCB
                    """
                )
        self.workspace.addWidget(self.window_Label)

        layout.addLayout(self.workspace)
        layout.addStretch()

        

        self.middle = QHBoxLayout()
        self.Log_widget = QListWidget(self)
        self.grab_logs()
        Log_scroll = QScrollBar(self)
        Log_scroll.setMaximum(self.Log_widget.count())
        Log_scroll.sliderMoved.connect(self.Log_widget.setCurrentRow)
        self.Log_widget.itemDoubleClicked.connect(self.open_session_page)
        self.middle.addWidget(self.Log_widget)
        self.middle.addWidget(Log_scroll)

        layout.addLayout(self.middle)
        layout.addStretch()
        
        self.buttonone = QPushButton("Back Home")
        layout.addWidget(self.buttonone, alignment= Qt.AlignmentFlag.AlignCenter)
        self.buttonone.clicked.connect(self.backhome)




    def backhome(self):
        self.study_done.emit()

    def open_session_page(self, item):
        if self.session_win.isVisible():
            self.session_win.hide()
        else:
            self.session_win.show()
            self.open_this.emit(item.text())
        


    def grab_logs(self):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT session_title FROM Session_information ORDER BY session_id DESC")
        query.exec()
        while query.next():
            self.Log_widget.addItem(query.value(0))

class Session_Overview_Page(QWidget):
    overview_done = pyqtSignal()
    def __init__(self, conn, study_window):
        super().__init__()
        self.conn = conn
        study_window.open_this.connect(self.grab_title)
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)
        self.evaluation = {}
        self.top_layout = QHBoxLayout()
        self.top_layout.addStretch()
        self.title = QLabel("")
        
        self.title.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 14px;
            font-weight: 700;
            """
        )
        self.this_session_id = QLabel("")
        self.this_session_id.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 12 px;
            font-weight: 600;
            """
        )

        self.top_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.this_session_id, alignment=Qt.AlignmentFlag.AlignRight)


        layout.addLayout(self.top_layout)


        self.date_row = QVBoxLayout()
        self.date_session = QLabel("")
        self.time_from_to = QLabel("")
        self.date_session.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 13px;
            font-weight: 600px;
            """
        )
        self.time_from_to.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 13px;
            font-weight: 600px;
            """
        )
        self.date_row.addWidget(self.date_session, alignment= Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.date_row.addWidget(self.time_from_to, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(self.date_row)

        self.alert_button_row = QHBoxLayout()
        self.alert_button_row.addStretch()
        self.alert_message = QPushButton("Info")
        self.alert_message.setStyleSheet("font-size: 11px; padding: 2px 5px")
        self.alert_message.setFixedSize(50, 20)
        self.alert_message.clicked.connect(self.show_info)
        self.alert_button_row.addWidget(self.alert_message, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(self.alert_button_row)

        self.eval_row = QHBoxLayout()
        self.apps = QLabel("")
        self.apps.setStyleSheet(
            """
            font-family: 'DM Sans';
            font-size: 15px;
            font-weight: 600px;
            """
        )

        self.eval_row.addStretch()
        self.eval_row.addWidget(self.apps, alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addLayout(self.eval_row)
        layout.addStretch()

        self.notes_row = QHBoxLayout()
        self.notes_area = QLabel("")
        self.notes_area.setWordWrap(True)
        self.notes_row.addWidget(self.notes_area)
        self.notes_area.setStyleSheet(
                """
                font-family: 'DM Sans';
                font-size: 16px;
                font-weight: 400px;
                background-color:#303030; 
                """
                )

        layout.addLayout(self.notes_row)
        layout.addStretch()

    def grab_apps(self, session_id):
        #This is for the OverView of Applications (No Sub)
        self.evaluation.clear()
        query = QSqlQuery(self.conn)
        query.prepare("SELECT app_name, duration FROM app_usage WHERE session_id = ? AND duration > 20")
        query.addBindValue(session_id)
        query.exec()
        self.full_time = 0
        while query.next():
            App_name = query.value(0)
            duration_App = query.value(1)
            self.evaluation[App_name] = duration_App
        for name, duration in self.evaluation.items():
            self.full_time += int(duration)
        self.display_apps(self.evaluation, self.full_time)

    def display_apps(self, dictionary, full_time):
        text = ""
        for name, duration in dictionary.items():
            percent_result = (duration / full_time) * 100
            time_duration = str(timedelta(seconds = int(duration)))
            text += f"{name} : {time_duration} - {percent_result:.1f}% \n"
        
        self.apps.setText(text)


    def grab_title(self, item):
        self.title.setText(item)
        self.grab_session_id(item)

    def grab_session_id(self,item):
        query = QSqlQuery(self.conn)
        query.prepare(
            """
                Select session_id FROM Session_information WHERE session_title = ?
            """
        )
        query.addBindValue(item)
        query.exec()
        if query.next():
            session_new = query.value(0)
        self.this_session_id.setText(f"Session: {session_new}")
        self.grab_session_date_time(session_new)
        # self.grab_timestamp(session_new)
        self.grab_notes(session_new)
        self.grab_time_session(session_new)
        self.grab_apps(session_new)

    def grab_session_date_time(self, session_id):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT date FROM Session_time WHERE session_id = ?")
        query.addBindValue(session_id)
        query.exec()
        if query.next():
            self.date_for_this = query.value(0)
        self.date_session.setText(f"Date: {self.date_for_this}")

    def grab_notes(self, session_id):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT session_notes FROM Session_information WHERE session_id = ?")
        query.addBindValue(session_id)
        query.exec()
        if query.next():
            self.notes = query.value(0)
        self.notes_area.setText(self.notes)

    def grab_time_session(self, session_id):
        query = QSqlQuery(self.conn)
        query.prepare("SELECT start_time, end_time, session_time FROM Session_time WHERE session_id = ?")
        query.addBindValue(session_id)
        query.exec()
        real_time = end_time = None
        if query.next():
            real_time = query.value(0)
            end_time = query.value(1)
            duration = query.value(2)
        rl_time = datetime.fromtimestamp(real_time)
        el_time = datetime.fromtimestamp(end_time)
        display_start = rl_time.strftime("%I:%M %p")
        display_end = el_time.strftime("%I: %M %p")
        session_counted = int(duration) if duration not in (None, '') else 0
        timenow = str(timedelta(seconds = session_counted))

        self.time_from_to.setText(f"Started From: {display_start} to {display_end} | Duration: {timenow}")

    def show_info(self):
        alert = QMessageBox(self)
        alert.setWindowTitle("Useful Information")
        alert.setText("The application shown below are the applications tracked during the session. Any application that was focused on less than 20 seconds will not be reported ")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.exec()




        





app = QApplication(sys.argv)
app.setStyleSheet(
    """
    QPushButton{
    background-color: #9D00FF;
    color: white;
    font-weight: bold;

    }
    """
)

conn = QSqlDatabase.addDatabase("QSQLITE", "app_conn")
conn.setDatabaseName("programs.db")
conn.open()


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
