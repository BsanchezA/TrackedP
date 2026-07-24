import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt

class OnScreenWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Float on top, frameless, and exclude from taskbar
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        
        # 2. Enable transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 3. Add your content
        label = QLabel("Floating Widget!", self)
        label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); border-radius: 10px; padding: 10px;")
        
        self.setGeometry(100, 100, 200, 50)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OnScreenWidget()
    window.show()
    sys.exit(app.exec())