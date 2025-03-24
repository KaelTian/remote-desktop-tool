import pickle
import socket
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

# 发送输入事件
def send_input(event, client_socket):
    event_data = pickle.dumps(event)
    client_socket.sendall(event_data)

# 捕获鼠标事件
def on_click(x, y, button, pressed, client_socket):
    if pressed:
        send_input({'type': 'mouse', 'action': 'click', 'x': x, 'y': y, 'button': button}, client_socket)

# 捕获键盘事件
def on_press(key, client_socket):
    send_input({'type': 'keyboard', 'action': 'press', 'key': key}, client_socket)

def on_release(key, client_socket):
    send_input({'type': 'keyboard', 'action': 'release', 'key': key}, client_socket)

# 启动输入监听
def start_input_listener(client_socket):
    mouse_listener = MouseListener(on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed, client_socket))
    keyboard_listener = KeyboardListener(on_press=lambda key: on_press(key, client_socket),
                                         on_release=lambda key: on_release(key, client_socket))
    mouse_listener.start()
    keyboard_listener.start()
    return mouse_listener, keyboard_listener