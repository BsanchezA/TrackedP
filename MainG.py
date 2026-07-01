import sys
import dataTracker
import sqlite3
from PyQt6 import QtWidgets
from datetime import date
from PyQt6.QtCore import Qt, QThread
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QApplication, QCheckBox, QLineEdit, QSizePolicy, QMainWindow, QPushButton, QWidget, QTableWidgetItem,QStackedWidget,QVBoxLayout,QTableWidget, QLabel, QHeaderView, QAbstractItemView, QTableView
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery, QSqlQueryModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trackon App")
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        button = QPushButton("Sync")
        self.button2 = QPushButton("Start Timer")
        self.button3 = QPushButton("End Timer")

        self.w = secondWindow()
        self.button4 = QPushButton("Activty In Depth")
        self.button5 = QPushButton("Study Mode")
        #button.setGeometry(900, 600, 100, 50)

        # Position window at (100, 100) byt it is the size of (480 by 80)
        self.setGeometry(600, 300, 680, 400)
        layout.addWidget(self.button2, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button3, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button4, alignment= Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button5, alignment= Qt.AlignmentFlag.AlignBottom)
        button.clicked.connect(self.sync)
        self.button2.clicked.connect(self.start_click)
        self.button3.clicked.connect(self.end_timer)
        self.button4.clicked.connect(self.toggle_activity)
        self.button5.clicked.connect(self.gotoStudy)
        self.Track_helper = dataTracker.Trackon()

        self.datafornow = {}

        # self.table = QTableWidget()
        # self.table.setColumnCount(2)
        # self.table.setHorizontalHeaderLabels(["Application", "Time Spent"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # layout.addWidget(self.table)
        # self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)


    def start_click(self):
        self.button2.setEnabled(False)
        self.thread = QThread()
        self.Track_helper.moveToThread(self.thread)

        self.thread.started.connect(self.Track_helper.run_time)
        self.thread.start()

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
        if self.w.isVisible():
            self.w.hide()
        else:
            self.w.show()

    def gotoStudy(self):
        windowtwo = studyWindow()
        widget.addWidget(windowtwo)
        widget.setCurrentIndex(widget.currentIndex() + 1)


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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Window")
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)


        self.buttonone = QPushButton("Back Home")
        layout.addWidget(self.buttonone, alignment= Qt.AlignmentFlag.AlignCenter)
        self.buttonone.clicked.connect(self.backhome)

        work_space = QVBoxLayout()
        work_space.setContentsMargins(11, 11, 11, 11)

               
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




        layout.addWidget(self.buttonone, alignment= Qt.AlignmentFlag.AlignCenter)
        self.buttonone.clicked.connect(self.backhome)
        
    def updatecheck(self):
        if len(self.created_check) >= 3:
            return
        obj = self.bottom_line_edit.text().strip()
        if not obj:
            return
        

        checkbox = QCheckBox(text = obj)
        self.created_check.append(checkbox)
        self.work_space.addWidget(checkbox)

        self.bottom_line_edit.clear()

    

        

    def backhome(self):
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)






app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
window = MainWindow()
widget.addWidget(window)
window.show()
widget.show()
app.exec()