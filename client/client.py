import socket
import zlib
import pickle
import cv2
from .utils import start_input_listener

def start_client(host='192.168.1.100', port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to {host}:{port}...")

    # 启动输入监听
    mouse_listener, keyboard_listener = start_input_listener(client_socket)

    while True:
        # 接收屏幕数据
        data_length = int.from_bytes(client_socket.recv(4), 'big')  # 接收数据长度
        img_data = b''
        while len(img_data) < data_length:
            img_data += client_socket.recv(4096)
        img = pickle.loads(zlib.decompress(img_data))  # 解压缩图像
        cv2.imshow('Remote Desktop', img)
        if cv2.waitKey(1) == ord('q'):  # 按q退出
            break

    cv2.destroyAllWindows()
    # 停止输入监听
    mouse_listener.stop()
    keyboard_listener.stop()
    client_socket.close()

if __name__ == "__main__":
    start_client()