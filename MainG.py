import sys
import dataTracker
import sqlite3
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView


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
        #button.setGeometry(900, 600, 100, 50)

        # Position window at (100, 100) byt it is the size of (480 by 80)
        self.setGeometry(600, 300, 680, 400)
        layout.addWidget(self.button2, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.button3, alignment = Qt.AlignmentFlag.AlignBottom)
        button.clicked.connect(self.sync)
        self.button2.clicked.connect(self.start_click)
        self.button3.clicked.connect(self.end_timer)
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


    
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()