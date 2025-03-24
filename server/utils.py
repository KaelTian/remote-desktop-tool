from mss import mss
import numpy as np
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

# 初始化输入控制器
mouse = MouseController()
keyboard = KeyboardController()

# 捕获屏幕
def capture_screen():
    with mss() as sct:
        # 获取所有显示器
        monitor = sct.monitors[1]  # 主显示器
        # 获取显示器实际分辨率
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        return img

# 处理输入事件
def handle_input(event):
    if event['type'] == 'mouse':
        # 更新鼠标位置
        x, y = event['x'], event['y'] 
        mouse.position = (x, y)
        
        if event['action'] == 'click':
            # 处理鼠标按钮
            button = Button.left
            if event['button'] == 'right':
                button = Button.right
            elif event['button'] == 'middle':
                button = Button.middle
                
            # 执行点击
            mouse.press(button)
            mouse.release(button)
        elif event['action'] == 'press':
            button = Button.left
            if event['button'] == 'right':
                button = Button.right
            elif event['button'] == 'middle':
                button = Button.middle
            mouse.press(button)
        elif event['action'] == 'release':
            button = Button.left
            if event['button'] == 'right':
                button = Button.right
            elif event['button'] == 'middle':
                button = Button.middle
            mouse.release(button)
        elif event['action'] == 'scroll':
            # 处理滚轮事件
            dx, dy = event.get('dx', 0), event.get('dy', 0)
            mouse.scroll(dx, dy)
            
    elif event['type'] == 'keyboard':
        key = event['key']
        # 处理特殊按键
        if isinstance(key, str) and key.startswith('Key.'):
            key = getattr(Key, key.split('.')[1])
            
        if event['action'] == 'press':
            keyboard.press(key)
        elif event['action'] == 'release':
            keyboard.release(key)