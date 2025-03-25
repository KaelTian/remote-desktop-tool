import socket
import zlib
import pickle
import cv2
import logging
import signal
import sys
import time
import numpy as np
from .utils import start_input_listener

class RemoteDesktopClient:
    def __init__(self, host='192.168.1.100', port=9999, buffer_size=4096,
                 target_fps=30, compression_quality=50):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.client_socket = None
        self.running = False
        self.mouse_listener = None 
        self.keyboard_listener = None
        
        # 性能控制参数
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.compression_quality = compression_quality
        self.last_frame_time = 0
        self.fps_stats = []
        self.bandwidth_stats = []
        
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
            
        # 打印性能统计
        if self.fps_stats:
            avg_fps = sum(self.fps_stats) / len(self.fps_stats)
            self.logger.info(f"平均FPS: {avg_fps:.2f}")
        if self.bandwidth_stats:
            avg_bandwidth = sum(self.bandwidth_stats) / len(self.bandwidth_stats)
            self.logger.info(f"平均带宽: {avg_bandwidth/1024/1024:.2f} MB/s")
            
        self.logger.info("客户端已停止")

    def adjust_quality(self, current_fps):
        """根据当前FPS动态调整图像质量"""
        if current_fps < self.target_fps * 0.8:  # FPS过低
            self.compression_quality = max(10, self.compression_quality - 5)
        elif current_fps > self.target_fps * 1.2:  # FPS过高
            self.compression_quality = min(95, self.compression_quality + 5)

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
            
            frame_count = 0
            start_time = time.time()
            last_stats_time = start_time

            while self.running:
                try:
                    current_time = time.time()
                    elapsed = current_time - self.last_frame_time
                    
                    # 控制帧率
                    if elapsed < self.frame_time:
                        time.sleep(self.frame_time - elapsed)
                    
                    # 接收屏幕数据
                    data_length = int.from_bytes(self.client_socket.recv(4), 'big')
                    img_data = b''
                    while len(img_data) < data_length:
                        chunk = self.client_socket.recv(self.buffer_size)
                        if not chunk:
                            raise ConnectionError("服务器断开连接")
                        img_data += chunk

                    # 解压并显示图像
                    frame_data = pickle.loads(zlib.decompress(img_data))
                    img = frame_data['image']
                    server_resolution = frame_data['resolution']
                    
                    # 调整图像大小以匹配服务器分辨率
                    if img.shape[1] != server_resolution[0] or img.shape[0] != server_resolution[1]:
                        img = cv2.resize(img, server_resolution)
                    
                    cv2.imshow('Remote Desktop', img)
                    
                    # 更新性能统计
                    frame_count += 1
                    if current_time - last_stats_time >= 1.0:
                        fps = frame_count / (current_time - last_stats_time)
                        bandwidth = len(img_data) / (current_time - last_stats_time)
                        
                        self.fps_stats.append(fps)
                        self.bandwidth_stats.append(bandwidth)
                        
                        self.logger.info(f"FPS: {fps:.2f}, 带宽: {bandwidth/1024/1024:.2f} MB/s")
                        self.adjust_quality(fps)
                        
                        frame_count = 0
                        last_stats_time = current_time
                    
                    self.last_frame_time = current_time
                    
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
    client = RemoteDesktopClient('192.168.0.209')
    client.start()