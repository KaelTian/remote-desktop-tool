import pickle
import socket
import pyautogui
from pynput.mouse import Listener as MouseListener, Button
from pynput.keyboard import Listener as KeyboardListener, Key
from typing import Dict, Any, Tuple
import logging

class InputHandler:
    def __init__(self, client_socket: socket.socket):
        self.client_socket = client_socket
        self.mouse_listener = None
        self.keyboard_listener = None
        self.screen_width, self.screen_height = pyautogui.size()

    def send_input(self, event: Dict[str, Any]) -> None:
        """发送输入事件到服务器"""
        try:
            # 添加客户端屏幕分辨率信息
            event['screen_width'] = self.screen_width
            event['screen_height'] = self.screen_height
            event_data = pickle.dumps(event)
            print(f"Sending event: {event}")  # 添加日志输出
            self.client_socket.sendall(event_data)
        except Exception as e:
            print(f"发送输入事件失败: {e}")

    def on_mouse_move(self, x: int, y: int) -> None:
        """处理鼠标移动"""
        self.send_input({
            'type': 'mouse',
            'action': 'move',
            'x': x,
            'y': y
        })

    def on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        """处理鼠标点击"""
        self.send_input({
            'type': 'mouse',
            'action': 'press' if pressed else 'release',
            'x': x,
            'y': y,
            'button': button.name
        })

    def on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """处理鼠标滚轮"""
        self.send_input({
            'type': 'mouse',
            'action': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy
        })

    def on_press(self, key: Key) -> None:
        """处理键盘按下"""
        self.send_input({
            'type': 'keyboard',
            'action': 'press',
            'key': str(key)
        })

    def on_release(self, key: Key) -> None:
        """处理键盘释放"""
        self.send_input({
            'type': 'keyboard',
            'action': 'release',
            'key': str(key)
        })

    def start(self):
        """启动输入监听"""
        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        return self.mouse_listener, self.keyboard_listener

def start_input_listener(client_socket: socket.socket):
    """创建并启动输入处理器"""
    handler = InputHandler(client_socket)
    return handler.start()