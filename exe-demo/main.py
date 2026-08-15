import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("HelloWorld")

        self.radio = QRadioButton("选项", self)
        self.radio.setStyleSheet("font-size: 16px;")
        self.radio.move(20, 80)

        self.button = QPushButton("点我", self)
        self.button.setFixedSize(200, 80)
        self.button.setStyleSheet("font-size: 24px;")
        self.button.clicked.connect(self.show_hello)

        # 按 Esc 退出全屏并关闭程序
        quit_action = self.addAction("quit")
        quit_action.setShortcut(Qt.Key.Key_Escape)
        quit_action.triggered.connect(self.close)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.button.move(
            (self.width() - self.button.width()) // 2,
            (self.height() - self.button.height()) // 2,
        )

    def show_hello(self) -> None:
        QMessageBox.information(self, "提示", "Hello world")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    # 模拟全屏：无边框 + 屏幕大小（跨平台兼容 Windows/macOS）
    window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    window.setGeometry(app.primaryScreen().geometry())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
