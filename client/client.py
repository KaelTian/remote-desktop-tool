import socket
import zlib
import pickle
import cv2
import logging
import signal
import sys
from .utils import start_input_listener

class RemoteDesktopClient:
    def __init__(self, host='192.168.1.100', port=9999, buffer_size=4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.client_socket = None
        self.running = False
        self.mouse_listener = None 
        self.keyboard_listener = None
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('remote_desktop_client.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def signal_handler(self, signum, frame):
        """处理系统信号"""
        self.logger.info("收到退出信号，正在关闭客户端...")
        self.stop()
        sys.exit(0)

    def stop(self):
        """停止客户端并清理资源"""
        self.running = False
        cv2.destroyAllWindows()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                self.logger.error(f"关闭socket时出错: {e}")
            self.client_socket = None
            
        self.logger.info("客户端已停止")

    def start(self):
        """启动客户端"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.logger.info(f"已连接到服务器 {self.host}:{self.port}")
            
            # 启动输入监听
            self.mouse_listener, self.keyboard_listener = start_input_listener(self.client_socket)
            self.running = True

            while self.running:
                try:
                    # 接收屏幕数据
                    data_length = int.from_bytes(self.client_socket.recv(4), 'big')
                    img_data = b''
                    while len(img_data) < data_length:
                        chunk = self.client_socket.recv(self.buffer_size)
                        if not chunk:
                            raise ConnectionError("服务器断开连接")
                        img_data += chunk

                    # 解压并显示图像
                    img = pickle.loads(zlib.decompress(img_data))
                    cv2.imshow('Remote Desktop', img)
                    
                    if cv2.waitKey(1) == ord('q'):
                        self.logger.info("用户按下q键，正在退出...")
                        break

                except Exception as e:
                    self.logger.error(f"接收/显示数据时出错: {e}")
                    break

        except Exception as e:
            self.logger.error(f"连接服务器时出错: {e}")
        finally:
            self.stop()

if __name__ == "__main__":
    client = RemoteDesktopClient()
    client.start()