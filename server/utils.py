from mss import mss
import numpy as np
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import pyautogui
from PIL import ImageGrab
from typing import Tuple, Dict, Any

# 初始化输入控制器
mouse = MouseController()
keyboard = KeyboardController()

def get_screen_resolution() -> Tuple[int, int]:
    """获取屏幕分辨率"""
    width, height = pyautogui.size()
    return width, height

def capture_screen() -> Dict[str, Any]:
    """捕获屏幕并返回图像数据和分辨率信息"""
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot)
    width, height = get_screen_resolution()
    return {
        'image': frame,
        'resolution': (width, height)
    }

# 处理输入事件
def handle_input(event: Dict[str, Any]) -> None:
    """处理输入事件"""
    try:
        if event['type'] == 'mouse':
            screen_width, screen_height = get_screen_resolution()
            client_x = event.get('x', 0)
            client_y = event.get('y', 0)
            client_width = event.get('screen_width', screen_width)
            client_height = event.get('screen_height', screen_height)
            
            # 计算实际坐标
            x = int((client_x * screen_width) / client_width)
            y = int((client_y * screen_height) / client_height)
            
            if event['action'] == 'move':
                pyautogui.moveTo(x, y)
            elif event['action'] in ['press', 'release']:
                button = event['button'].lower()
                if event['action'] == 'press':
                    pyautogui.mouseDown(x, y, button=button)
                else:
                    pyautogui.mouseUp(x, y, button=button)
            elif event['action'] == 'scroll':
                pyautogui.scroll(event.get('dy', 0))
                
        elif event['type'] == 'keyboard':
            key = event['key'].strip("'")
            if event['action'] == 'press':
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)
                
    except Exception as e:
        print(f"处理输入事件时出错: {e}")