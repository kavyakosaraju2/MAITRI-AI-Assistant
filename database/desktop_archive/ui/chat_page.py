import sys
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal

# Allow importing from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_decision_engine import ai_decision_engine
from agent_brain.context_memory import memory


# -------------------------------------------------
# BACKGROUND WORKER THREAD
# -------------------------------------------------
class AIWorker(QThread):
    finished = Signal(str)

    def __init__(self, user_text, emails, events, tasks):
        super().__init__()
        self.user_text = user_text
        self.emails = emails
        self.events = events
        self.tasks = tasks

    def run(self):
        try:
            response = ai_decision_engine(
                self.user_text,
                self.emails,
                self.events,
                self.tasks
            )
        except Exception as e:
            response = f"Error: {str(e)}"

        self.finished.emit(response)


# -------------------------------------------------
# CHAT PAGE UI
# -------------------------------------------------
class ChatPage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Input area
        self.input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ask MAITRI something...")
        self.send_button = QPushButton("Send")

        self.input_layout.addWidget(self.user_input)
        self.input_layout.addWidget(self.send_button)

        self.layout.addWidget(self.chat_display)
        self.layout.addLayout(self.input_layout)

        self.send_button.clicked.connect(self.handle_send)
        self.user_input.returnPressed.connect(self.handle_send)

        self.apply_styles()

    # -------------------------------------------------
    # HANDLE SEND
    # -------------------------------------------------
    def handle_send(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return

        self.add_user_message(user_text)
        self.user_input.clear()

        self.add_ai_message("Thinking...")

        # Replace with your real stored data if needed
        emails = getattr(memory, "emails", []) or []
        events = getattr(memory, "events", []) or []
        tasks = getattr(memory, "tasks", []) or []

        self.worker = AIWorker(user_text, emails, events, tasks)
        self.worker.finished.connect(self.display_response)
        self.worker.start()

    # -------------------------------------------------
    # DISPLAY RESPONSE
    # -------------------------------------------------
    def display_response(self, response):
        self.remove_last_message()
        self.add_ai_message(response)

    # -------------------------------------------------
    # MESSAGE HELPERS
    # -------------------------------------------------
    def add_user_message(self, message):
        self.chat_display.append(
            f"<p style='color:#38bdf8; margin:8px 0;'><b>You:</b> {message}</p>"
        )

    def add_ai_message(self, message):
        self.chat_display.append(
            f"<p style='color:#a78bfa; margin:8px 0;'><b>MAITRI:</b> {message}</p>"
        )

    def remove_last_message(self):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.select(cursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

    # -------------------------------------------------
    # DARK THEME STYLING
    # -------------------------------------------------
    def apply_styles(self):
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: white;
                border: none;
                font-size: 14px;
                padding: 10px;
            }

            QLineEdit {
                background-color: #1e293b;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)