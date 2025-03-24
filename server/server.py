import socket
import zlib
import pickle
import signal
import sys
import threading
import logging
import time
from typing import Optional, Tuple
from .utils import capture_screen, handle_input

class RemoteDesktopServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 9999, 
                 screen_capture_interval: float = 0.1,
                 buffer_size: int = 1024,
                 max_connections: int = 1):
        """
        初始化远程桌面服务器
        
        Args:
            host: 服务器监听地址
            port: 服务器监听端口
            screen_capture_interval: 屏幕捕获间隔（秒）
            buffer_size: 接收缓冲区大小
            max_connections: 最大连接数
        """
        self.host = host
        self.port = port
        self.screen_capture_interval = screen_capture_interval
        self.buffer_size = buffer_size
        self.max_connections = max_connections
        
        # 状态标志
        self.running = False
        self.connected = False
        
        # 资源
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.screen_thread: Optional[threading.Thread] = None
        self.input_thread: Optional[threading.Thread] = None
        
        # 统计信息
        self.start_time: Optional[float] = None
        self.frames_sent = 0
        self.bytes_sent = 0
        self.last_stats_time = 0
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self):
        """配置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('remote_desktop_server.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def signal_handler(self, signum: int, frame):
        """处理系统信号"""
        self.logger.info("收到退出信号，正在关闭服务器...")
        self.stop()

    def stop(self):
        """停止服务器并清理资源"""
        self.running = False
        self.connected = False
        
        # 停止线程
        if self.screen_thread and self.screen_thread.is_alive():
            self.screen_thread.join(timeout=1.0)
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)
            
        # 关闭socket
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                self.logger.error(f"关闭客户端socket时出错: {e}")
            self.client_socket = None
            
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                self.logger.error(f"关闭服务器socket时出错: {e}")
            self.server_socket = None
            
        # 打印统计信息
        if self.start_time:
            duration = time.time() - self.start_time
            self.logger.info(f"服务器运行时间: {duration:.2f}秒")
            self.logger.info(f"发送帧数: {self.frames_sent}")
            self.logger.info(f"发送字节数: {self.bytes_sent}")
            if duration > 0:
                self.logger.info(f"平均帧率: {self.frames_sent/duration:.2f} FPS")
                self.logger.info(f"平均带宽: {self.bytes_sent/duration/1024/1024:.2f} MB/s")
        
        self.logger.info("服务器已停止")

    def handle_screen_capture(self):
        """处理屏幕捕获和发送"""
        while self.running and self.connected:
            try:
                start_time = time.time()
                
                # 捕获屏幕
                img = capture_screen()
                img_data = zlib.compress(pickle.dumps(img))
                
                # 发送数据
                self.client_socket.sendall(len(img_data).to_bytes(4, 'big'))
                self.client_socket.sendall(img_data)
                
                # 更新统计信息
                self.frames_sent += 1
                self.bytes_sent += len(img_data)
                
                # 控制帧率
                elapsed = time.time() - start_time
                if elapsed < self.screen_capture_interval:
                    time.sleep(self.screen_capture_interval - elapsed)
                    
                # 定期打印统计信息
                current_time = time.time()
                if current_time - self.last_stats_time >= 5.0:  # 每5秒打印一次
                    self._print_stats()
                    self.last_stats_time = current_time
                    
            except Exception as e:
                self.logger.error(f"屏幕捕获/发送错误: {e}")
                break

    def handle_input_events(self):
        """处理输入事件"""
        while self.running and self.connected:
            try:
                event_data = self.client_socket.recv(self.buffer_size)
                if not event_data:
                    self.logger.info("客户端断开连接")
                    break
                event = pickle.loads(event_data)
                handle_input(event)
            except Exception as e:
                self.logger.error(f"输入处理错误: {e}")
                break

    def _print_stats(self):
        """打印统计信息"""
        if self.start_time:
            duration = time.time() - self.start_time
            fps = self.frames_sent / duration if duration > 0 else 0
            bandwidth = self.bytes_sent / duration / 1024 / 1024 if duration > 0 else 0
            self.logger.info(f"状态: FPS={fps:.2f}, 带宽={bandwidth:.2f} MB/s")

    def start(self):
        """启动服务器"""
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            
            self.logger.info(f"服务器正在监听 {self.host}:{self.port}...")
            self.logger.info("按 Ctrl+C 可以优雅退出")
            
            self.running = True
            self.start_time = time.time()
            
            while self.running:
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    self.connected = True
                    self.logger.info(f"新客户端连接: {addr}")
                    
                    # 启动线程
                    self.screen_thread = threading.Thread(target=self.handle_screen_capture)
                    self.input_thread = threading.Thread(target=self.handle_input_events)
                    
                    self.screen_thread.daemon = True
                    self.input_thread.daemon = True
                    
                    self.screen_thread.start()
                    self.input_thread.start()
                    
                    # 等待线程结束
                    self.screen_thread.join()
                    self.input_thread.join()
                    
                except socket.error as e:
                    if self.running:  # 只在非主动停止时打印错误
                        self.logger.error(f"Socket错误: {e}")
                    break
                finally:
                    self.connected = False
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except Exception as e:
                            self.logger.error(f"关闭客户端连接时出错: {e}")
                        self.client_socket = None
                    
        except Exception as e:
            self.logger.error(f"服务器错误: {e}")
        finally:
            self.stop()

def main():
    """主函数"""
    try:
        server = RemoteDesktopServer()
        server.start()
    except Exception as e:
        logging.error(f"程序异常退出: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()