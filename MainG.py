import sys
import dataTracker
import sqlite3
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QApplication, QSizePolicy, QMainWindow, QPushButton, QWidget, QTableWidgetItem,QStackedWidget,QVBoxLayout,QTableWidget, QLabel, QHeaderView, QAbstractItemView, QTableView
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
        #button.setGeometry(900, 600, 100, 50)

        # Position window at (100, 100) byt it is the size of (480 by 80)
        self.setGeometry(600, 300, 680, 400)
        layout.addWidget(self.button2, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button3, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button4, alignment= Qt.AlignmentFlag.AlignBottom)
        button.clicked.connect(self.sync)
        self.button2.clicked.connect(self.start_click)
        self.button3.clicked.connect(self.end_timer)
        self.button4.clicked.connect(self.toggle_activity)
        self.Track_helper = dataTracker.Trackon()

        self.datafornow = {}

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Application", "Time Spent"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)


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


class secondWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Detailed Information")
        self.resize(600, 400)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentIndex(0)
            
                 
        self.conn = QSqlDatabase.addDatabase("QSQLITE", "second_window_conn")
        self.conn.setDatabaseName("programs.db")
        self.conn.open()

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
            




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()