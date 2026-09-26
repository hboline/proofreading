import multiprocessing as mp
from multiprocessing.process import BaseProcess
from multiprocessing.queues import Queue
import queue
import sys

from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
    QTextBlockFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QTextBrowser,
    QVBoxLayout,
)


class _OverlayWindow(QWidget):
    MAX_WIDTH = 1200
    HORIZONTAL_PADDING = 32
    VERTICAL_PADDING = 5

    SAMPLE_TEXT = "this **is** a ~~markdown~~ test"

    def __init__(self):
        super().__init__()

        self.setObjectName("overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setStyleSheet("""
            QWidget#overlay {
                background-color: #f9f9f9;
                border: 2px solid black;
            }

            QTextBrowser {
                background-color: #f9f9f9;
                color: #000000;
                border: none;
                font-size: 16px;
            }
        """)

        self.text = QTextBrowser()

        self.text.viewport().installEventFilter(self)

        self.text.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.text.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            self.HORIZONTAL_PADDING,
            self.VERTICAL_PADDING,
            self.HORIZONTAL_PADDING,
            self.VERTICAL_PADDING,
        )

        layout.addWidget(self.text)

        QShortcut(
            QKeySequence("Q"),
            self,
            self.close,
        )

        QShortcut(
            QKeySequence("Backspace"),
            self,
            self.clear_text,
        )

        # Determine the width of the blank/default window.
        self.set_text(self.SAMPLE_TEXT)
        self.base_width = self.width()

        self.clear_text()
        self.position_initially()

    def center_text(self):
        cursor = QTextCursor(self.text.document())
        cursor.select(QTextCursor.SelectionType.Document)

        fmt = QTextBlockFormat()
        fmt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cursor.mergeBlockFormat(fmt)

    def set_text(self, markdown: str):
        self.text.setMarkdown(markdown)
        self.center_text()

        document = self.text.document()
        document.setDocumentMargin(0)

        # Find natural unwrapped width.
        document.setTextWidth(-1)
        text_width = document.idealWidth()

        total_width = int(
            text_width + self.HORIZONTAL_PADDING * 2
        )

        if hasattr(self, "base_width"):
            total_width = max(
                total_width,
                self.base_width,
            )

        total_width = min(
            total_width,
            self.MAX_WIDTH,
        )

        available_width = (
            total_width
            - self.HORIZONTAL_PADDING * 2
        )

        # Recalculate height after wrapping.
        document.setTextWidth(available_width)

        text_height = document.size().height()

        height_slack = 8

        total_height = int(
            text_height
            + self.VERTICAL_PADDING * 2
            + height_slack
        )

        center = self.geometry().center()

        self.setFixedSize(
            total_width,
            total_height,
        )

        self.move(
            center.x() - self.width() //2,
            center.y() - self.height() //2,
        )

    def clear_text(self):
        self.text.clear()

        font_height = self.text.fontMetrics().height()

        center = self.geometry().center()

        self.setFixedSize(
            self.base_width,
            font_height
            + self.VERTICAL_PADDING * 2
            + 8,
        )

        self.move(
            center.x() - self.width() //2,
            center.y() - self.height() //2,
        )

    def position_initially(self):
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()

        x = (
            geometry.x()
            + (geometry.width() - self.width()) // 2
            + 45
        )

        target_center_y = (
            geometry.y()
            + int(geometry.height() * 0.85)
        )

        y = target_center_y - self.height() // 2

        self.move(x, y)

    def eventFilter(self, obj, event):
        if (
            obj is self.text.viewport()
            and event.type()
            == QEvent.Type.MouseButtonPress
            and event.button()
            == Qt.MouseButton.LeftButton
            and event.modifiers()
            & Qt.KeyboardModifier.ShiftModifier
        ):
            self.windowHandle().startSystemMove()
            return True

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.modifiers()
            & Qt.KeyboardModifier.ShiftModifier
        ):
            self.windowHandle().startSystemMove()
            event.accept()
            return

        super().mousePressEvent(event)


def _overlay_process(command_queue):
    """
    Runs inside the dedicated Qt process.
    """

    app = QApplication(sys.argv)

    window = _OverlayWindow()
    window.show()

    def process_commands():
        while True:
            try:
                command, value = command_queue.get_nowait()
            except queue.Empty:
                break

            if command == "set_text":
                window.set_text(value)

            elif command == "clear":
                window.clear_text()

            elif command == "close":
                app.quit()
                return

    # Check for messages from the parent application.
    timer = QTimer()
    timer.timeout.connect(process_commands)
    timer.start(25)

    app.exec()


class Overlay:
    """
    Public interface used by the proofreading application.
    """

    def __init__(self):
        self._process: BaseProcess | None = None
        self._queue: Queue | None = None

    @property
    def is_open(self) -> bool:
        return (
            self._process is not None
            and self._process.is_alive()
        )

    def open(self):
        if self.is_open:
            return

        ctx = mp.get_context("spawn")

        self._queue = ctx.Queue()

        self._process = ctx.Process(
            target=_overlay_process,
            args=(self._queue,),
            daemon=True,
        )

        self._process.start()

    def set_text(self, markdown: str):
        if not self.is_open:
            raise RuntimeError("Overlay is not open.")

        assert self._queue is not None
        self._queue.put(("set_text", markdown))


    def clear(self):
        if not self.is_open:
            return

        assert self._queue is not None
        self._queue.put(("clear", None))


    def close(self):
        if not self.is_open:
            return

        assert self._queue is not None
        assert self._process is not None

        self._queue.put(("close", None))

        self._process.join(timeout=1)

        if self._process.is_alive():
            self._process.terminate()
            self._process.join()

        self._process = None
        self._queue = None
