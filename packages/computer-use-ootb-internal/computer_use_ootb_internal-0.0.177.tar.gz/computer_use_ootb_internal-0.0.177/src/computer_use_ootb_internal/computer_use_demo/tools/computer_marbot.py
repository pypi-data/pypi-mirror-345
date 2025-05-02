import ctypes
import time
from time import sleep
import pyautogui  # 用于获取当前鼠标位置

# =========================== 结构体定义 ===========================
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong), ("u", _INPUT_UNION)]

# =========================== 常量定义 ===========================
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# 键盘扫描码表（可扩展）
VK_CODE = {
    # 字母
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21,
    'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'm': 0x32, 'n': 0x31, 'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13,
    's': 0x1F, 't': 0x14, 'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D,
    'y': 0x15, 'z': 0x2C,

    # 数字（主键盘）
    '0': 0x0B, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05,
    '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A,

    # 功能键
    'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
    'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
    'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,

    # 控制键
    'esc': 0x01, 'tab': 0x0F, 'capslock': 0x3A,
    'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38,
    'space': 0x39, 'enter': 0x1C, 'backspace': 0x0E,

    # 符号键
    '-': 0x0C, '=': 0x0D, '[': 0x1A, ']': 0x1B,
    '\\': 0x2B, ';': 0x27, "'": 0x28, ',': 0x33,
    '.': 0x34, '/': 0x35, '`': 0x29,

    # 导航键
    'insert': 0x52, 'delete': 0x53,
    'home': 0x47, 'end': 0x4F,
    'pageup': 0x49, 'pagedown': 0x51,

    # 箭头
    'up': 0x48, 'down': 0x50,
    'left': 0x4B, 'right': 0x4D,

    # 小键盘（注意需加 NumLock 才能正确使用）
    'num0': 0x52, 'num1': 0x4F, 'num2': 0x50, 'num3': 0x51,
    'num4': 0x4B, 'num5': 0x4C, 'num6': 0x4D,
    'num7': 0x47, 'num8': 0x48, 'num9': 0x49,
    'num.': 0x53, 'num+': 0x4E, 'num-': 0x4A, 'num*': 0x37, 'num/': 0x35
}


# =========================== 类封装接口 ===========================
class MarbotAutoGUI:
    def __init__(self):
        self.extra = ctypes.c_ulong(0)

    def get_absolute_coords(self, x, y):
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)
        return abs_x, abs_y

    def moveTo(self, x, y, duration=0.5, steps=50):
        from_x, from_y = pyautogui.position()
        step_x = (x - from_x) / steps
        step_y = (y - from_y) / steps
        delay = duration / steps
        for i in range(steps):
            sx = from_x + step_x * i
            sy = from_y + step_y * i
            abs_x, abs_y = self.get_absolute_coords(sx, sy)
            self._send_mouse_move(abs_x, abs_y)
            time.sleep(delay)

    def click(self, x=None, y=None, duration=0.3):
        if x is not None and y is not None:
            self.moveTo(x, y, duration)
            self.moveTo(x + 3, y + 2, duration=0.2)
        self._mouse_click()

    def doubleClick(self, x=None, y=None, duration=0.3):
        self.click(x, y, duration)
        time.sleep(0.1)
        self.click(x, y, duration)

    def keyDown(self, key):
        scan = VK_CODE.get(key.lower())
        if scan:
            self._send_key(scan, down=True)

    def keyUp(self, key):
        scan = VK_CODE.get(key.lower())
        if scan:
            self._send_key(scan, down=False)

    def press(self, key):
        self.keyDown(key)
        time.sleep(0.05)
        self.keyUp(key)

    # ========== 内部实现 ==========

    def _send_mouse_move(self, abs_x, abs_y):
        ii = INPUT(type=INPUT_MOUSE)
        ii.mi = MOUSEINPUT(abs_x, abs_y, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, ctypes.pointer(self.extra))
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

    def _mouse_click(self):
        inputs = (INPUT * 2)()
        inputs[0].type = INPUT_MOUSE
        inputs[0].mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(self.extra))
        inputs[1].type = INPUT_MOUSE
        inputs[1].mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(self.extra))
        ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))

    def _send_key(self, scan_code, down=True):
        ii = INPUT(type=INPUT_KEYBOARD)
        flags = KEYEVENTF_SCANCODE
        if not down:
            flags |= KEYEVENTF_KEYUP
        ii.ki = KEYBDINPUT(wVk=0, wScan=scan_code, dwFlags=flags, time=0, dwExtraInfo=ctypes.pointer(self.extra))
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))



if __name__ == "__main__":
    # 实例化你的类
    bot = MarbotAutoGUI()

    # 等待你切到目标窗口
    print("⌛ Waiting 10 seconds...")
    sleep(5)

    print("🚀 Start action sequence")

    # 设置目标位置
    target_x = 3061
    target_y = 666

    # 按住 Alt 键
    bot.keyDown('alt')
    sleep(1)

    # 移动到目标并点击（内部自动包含微调）
    bot.click(x=target_x, y=target_y, duration=2.0)

    sleep(1)
    # 松开 Alt 键
    bot.keyUp('alt')

    print("✅ Done")