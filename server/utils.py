from mss import mss
import numpy as np
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

# 初始化输入控制器
mouse = MouseController()
keyboard = KeyboardController()

# 捕获屏幕
def capture_screen():
    with mss() as sct:
        monitor = sct.monitors[1]  # 捕获主屏幕
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        return img

# 处理输入事件
def handle_input(event):
    if event['type'] == 'mouse':
        mouse.position = (event['x'], event['y'])
        if event['action'] == 'click':
            mouse.click(event['button'])
    elif event['type'] == 'keyboard':
        if event['action'] == 'press':
            keyboard.press(event['key'])
        elif event['action'] == 'release':
            keyboard.release(event['key'])