from mss import mss
import numpy as np
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import pyautogui
from PIL import ImageGrab
from typing import Tuple, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remote_desktop_server_input.log')
    ]
)
logger = logging.getLogger(__name__)

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
                logger.info(f"收到鼠标移动事件，目标坐标: ({x}, {y})")
                pyautogui.moveTo(x, y)
                logger.info(f"鼠标已移动到坐标: ({x}, {y})")
            elif event['action'] in ['press', 'release']:
                button = event['button'].lower()
                action_str = '按下' if event['action'] == 'press' else '释放'
                logger.info(f"收到鼠标 {action_str} 事件，按钮: {button}，坐标: ({x}, {y})")
                if event['action'] == 'press':
                    pyautogui.mouseDown(x, y, button=button)
                else:
                    pyautogui.mouseUp(x, y, button=button)
                logger.info(f"鼠标 {action_str} 事件处理完成，按钮: {button}，坐标: ({x}, {y})")
            elif event['action'] == 'scroll':
                dy = event.get('dy', 0)
                logger.info(f"收到鼠标滚动事件，滚动值: {dy}")
                pyautogui.scroll(dy)
                logger.info(f"鼠标滚动事件处理完成，滚动值: {dy}")

        elif event['type'] == 'keyboard':
            key = event['key'].strip("'")
            action_str = '按下' if event['action'] == 'press' else '释放'
            logger.info(f"收到键盘 {action_str} 事件，键: {key}")
            if event['action'] == 'press':
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)
            logger.info(f"键盘 {action_str} 事件处理完成，键: {key}")

    except Exception as e:
        logger.error(f"处理输入事件时出错: {e}")