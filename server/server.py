import socket
import zlib
import pickle
from .utils import capture_screen, handle_input

def start_server(host='0.0.0.0', port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    while True:
        # 捕获屏幕并发送
        img = capture_screen()
        img_data = zlib.compress(pickle.dumps(img))  # 压缩图像
        client_socket.sendall(len(img_data).to_bytes(4, 'big'))  # 发送数据长度
        client_socket.sendall(img_data)  # 发送图像数据

        # 接收输入事件
        event_data = client_socket.recv(1024)
        if event_data:
            event = pickle.loads(event_data)
            handle_input(event)

if __name__ == "__main__":
    start_server()