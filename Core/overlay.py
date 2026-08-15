import sys
import subprocess
import time
from pathlib import Path

from Quartz import (
    CGEventCreate,
    CGEventGetLocation,
    CGEventCreateMouseEvent,
    CGEventPost,
    kCGEventMouseMoved,
    kCGHIDEventTap,
)

from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QCursor, QColor
from PySide6.QtWidgets import QApplication, QWidget

# exe-demo 按钮的全局屏幕区域，启动时根据主屏分辨率自动计算
def _calc_button_rect() -> tuple[int, int, int, int]:
    from PySide6.QtWidgets import QApplication

    screen = QApplication.primaryScreen().geometry()
    btn_w, btn_h = 200, 80
    left = screen.x() + (screen.width() - btn_w) // 2
    top = screen.y() + (screen.height() - btn_h) // 2
    return left, top, left + btn_w, top + btn_h
EXE_DEMO_DIR = Path(__file__).parent.parent / "exe-demo"
EXE_DEMO_MAIN = EXE_DEMO_DIR / "main.py"
EXE_DEMO_PYTHON = EXE_DEMO_DIR / ".venv" / "bin" / "python"


def move_mouse(x: float, y: float) -> None:
    event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), 0)
    CGEventPost(kCGHIDEventTap, event)


def get_mouse_pos() -> QPointF:
    event = CGEventCreate(None)
    loc = CGEventGetLocation(event)
    return QPointF(loc.x, loc.y)


class Overlay(QWidget):
    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        left, top, right, bottom = _calc_button_rect()
        self.setGeometry(left, top, right - left, bottom - top)

        self._busy = False
        self.show()
        self._force_on_top()

    def _force_on_top(self) -> None:
        """macOS 上用 Cocoa 原生 API 把窗口提升到 Status 级别。"""
        if sys.platform != "darwin":
            return
        try:
            from Cocoa import NSWindow, NSStatusWindowLevel

            ns_window = NSWindow.windowWithWindowNumber_(self.winId())
            if ns_window is not None:
                ns_window.setLevel_(NSStatusWindowLevel)
                ns_window.setIgnoresMouseEvents_(False)
                ns_window.orderFrontRegardless()
        except Exception as e:
            print(f"[overlay] _force_on_top error: {e}")

    def paintEvent(self, event) -> None:  # noqa: N802
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 0, 0, 30))  # 几乎透明，调试用
        painter.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._busy:
            return
        self._busy = True

        # 1. 记录当前鼠标位置（即按钮中心）
        original_pos = get_mouse_pos()

        # 2. 隐藏拦截层，让点击能穿透到 exe-demo
        self.hide()

        # 3. 极短时间内完成：移到 radio → 点击 → 移回 → 点击按钮 → 重新显示红框
        QTimer.singleShot(5, lambda: self._stealth_click(original_pos))

    def _stealth_click(self, original_pos: QPointF) -> None:
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen().geometry()
        # radio 位置 (20, 80)，中心点大约是 (30, 90)
        radio_x = screen.x() + 30
        radio_y = screen.y() + 90

        # 第一步：移到 radio 并点击
        move_mouse(radio_x, radio_y)
        self._post_click(radio_x, radio_y)

        # 第二步：延迟确保系统处理完移动事件，再移回并点击按钮
        QTimer.singleShot(20, lambda: self._click_button(original_pos))

    def _click_button(self, original_pos: QPointF) -> None:
        # 移回原位
        move_mouse(original_pos.x(), original_pos.y())

        # 再延迟一点点确保鼠标到位，然后点击按钮
        QTimer.singleShot(10, lambda: self._post_click_and_restore(original_pos))

    def _post_click_and_restore(self, original_pos: QPointF) -> None:
        self._post_click(original_pos.x(), original_pos.y())

        # 重新显示红框
        QTimer.singleShot(10, self._restore)

    def _restore(self) -> None:
        self.show()
        self._force_on_top()
        self._busy = False

    @staticmethod
    def _post_click(x: float, y: float) -> None:
        from Quartz import (
            CGEventCreateMouseEvent,
            CGEventPost,
            kCGEventLeftMouseDown,
            kCGEventLeftMouseUp,
            kCGHIDEventTap,
        )

        down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, (x, y), 0)
        up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, (x, y), 0)
        CGEventPost(kCGHIDEventTap, down)
        CGEventPost(kCGHIDEventTap, up)


def main() -> None:
    print("[overlay] starting exe-demo...")
    # 先启动 exe-demo
    proc = subprocess.Popen(
        [str(EXE_DEMO_PYTHON), str(EXE_DEMO_MAIN)],
        cwd=str(EXE_DEMO_DIR),
    )
    print(f"[overlay] exe-demo pid={proc.pid}")

    # 等 exe-demo 窗口出来
    print("[overlay] waiting 2s for exe-demo window...")
    time.sleep(2)

    print("[overlay] creating QApplication...")
    app = QApplication(sys.argv)

    print("[overlay] creating Overlay window...")
    overlay = Overlay()
    print(f"[overlay] overlay geometry={overlay.geometry()}")

    print("[overlay] entering event loop...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
