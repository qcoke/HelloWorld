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
