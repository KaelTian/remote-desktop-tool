# server/__init__.py
print("Initializing server package...")

# 定义包级别的变量
VERSION = "1.0.0"

# 导入包内的模块，方便外部直接使用
from .server import start_server
from .utils import capture_screen, handle_input