# Hello World

## exe-demo

一个极简的 macOS 全屏演示程序：屏幕正中央放一个按钮，点击后弹出系统弹窗，显示 `Hello world`。

### 功能

- 启动即进入全屏窗口
- 窗口正中央有一个「点我」按钮
- 点击按钮弹出系统提示框，内容为 `Hello world`
- 按 `Esc` 退出程序

### 运行方式

依赖安装在项目自带的虚拟环境 `.venv` 中（基于 PySide6 / Qt）：

```bash
cd exe-demo
.venv/bin/python main.py
```

如果 `.venv` 不存在，可自行创建并安装依赖：

```bash
cd exe-demo
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python main.py
```

### 技术说明

- GUI 框架：PySide6 (Qt 6)
- 入口文件：[exe-demo/main.py](exe-demo/main.py)
- 说明：最初考虑过 Python 自带的 Tkinter，但当前 Homebrew 的 tcl-tk 9.0.4 在部分 macOS 版本上存在 bug（`tk scaling` 返回 NaN 导致窗口无法创建），因此改用 PySide6 实现。

## Core

一个演示「透明拦截层」的程序：在 exe-demo 的按钮上方覆盖一个置顶透明窗口，拦截用户点击后执行额外操作，再让原流程继续。

### 功能

- 自动启动 exe-demo，并在其按钮位置覆盖一个半透明红色置顶窗口
- 点击红色拦截层时：
  1. 隐藏拦截层，让点击穿透到下层
  2. 快速将鼠标移到左上角，点击选中 radio button
  3. 移回原位置，点击按钮触发「Hello world」弹窗
  4. 重新显示拦截层，恢复遮挡状态
- 目标：用户无感知的情况下完成额外操作

### 运行方式

```bash
cd Core
../exe-demo/.venv/bin/python overlay.py
```

### 技术说明

- 依赖：PySide6 + pyobjc-framework-Quartz
- 入口文件：[Core/overlay.py](Core/overlay.py)
- 鼠标控制：通过 Quartz `CGEventCreateMouseEvent` / `CGEventPost` 实现
- 窗口置顶：macOS 上使用 Cocoa `NSWindow` 原生 API 提升层级（当前有兼容性问题，待修复）

### 已知问题

- macOS 上 `_force_on_top` 的 `windowWithWindowNumber_` 调用报错，窗口层级可能不稳定
- 鼠标快速移动时，系统事件队列存在延迟，可能导致弹窗在鼠标完全回位前弹出
- 需要「辅助功能」权限才能控制鼠标
