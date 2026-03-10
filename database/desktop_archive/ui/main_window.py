import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget
)
from PySide6.QtCore import Qt
from ui.chat_page import ChatPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAITRI - AI Assistant")
        self.setGeometry(100, 100, 1200, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = QVBoxLayout()
        self.sidebar.setAlignment(Qt.AlignTop)

        self.btn_chat = QPushButton("🤖 AI Chat")
        self.btn_email = QPushButton("📧 Emails")
        self.btn_calendar = QPushButton("📅 Calendar")
        self.btn_settings = QPushButton("⚙ Settings")

        for btn in [self.btn_chat, self.btn_email, self.btn_calendar, self.btn_settings]:
            btn.setFixedHeight(50)
            self.sidebar.addWidget(btn)

        # Stack pages
        self.stack = QStackedWidget()
        self.chat_page = ChatPage()

       

        self.email_page = QLabel("Email Page")
        self.email_page.setAlignment(Qt.AlignCenter)

        self.calendar_page = QLabel("Calendar Page")
        self.calendar_page.setAlignment(Qt.AlignCenter)

        self.settings_page = QLabel("Settings Page")
        self.settings_page.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(self.chat_page)
        self.stack.addWidget(self.email_page)
        self.stack.addWidget(self.calendar_page)
        self.stack.addWidget(self.settings_page)

        # Button actions
        self.btn_chat.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_email.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_calendar.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        # Add layouts
        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.stack, 4)

        self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }

            QLabel {
                color: white;
                font-size: 20px;
            }

            QPushButton {
                background-color: #1e293b;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #2563eb;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
