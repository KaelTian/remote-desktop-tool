# Remote Desktop Tool

远程桌面控制工具，基于Python实现，支持实时屏幕传输和远程输入控制。

## 功能特性

- **实时屏幕传输**：将机器B的屏幕实时传输到机器A。
- **远程输入控制**：在机器A上操作机器B的鼠标和键盘。
- **低延迟**：优化图像压缩和传输，确保流畅的远程控制体验。

## 项目结构
remote-desktop-tool/
├── README.md # 项目说明
├── requirements.txt # 依赖库列表
├── server/ # 服务端代码
│ ├── init.py
│ ├── server.py # 服务端主程序
│ └── utils.py # 工具函数（如屏幕捕获、输入处理）
├── client/ # 客户端代码
│ ├── init.py
│ ├── client.py # 客户端主程序
│ └── utils.py # 工具函数（如图像显示、输入捕获）
└── scripts/ # 辅助脚本
├── start_server.sh # 启动服务端的脚本
└── start_client.sh # 启动客户端的脚本

## 快速开始

### 环境要求

- Python 3.7+
- 依赖库：`mss`, `opencv-python`, `pynput`, `numpy`

### 安装依赖

1. 克隆项目：
    git clone https://github.com/your-username/remote-desktop-tool.git
    cd remote-desktop-tool

2. 创建虚拟环境：
    python -m venv venv

3. 激活虚拟环境：

    Windows:

    bash
    Copy
    venv\Scripts\activate
    macOS/Linux:

    bash
    Copy
    source venv/bin/activate

4. 安装依赖：

    bash
    Copy
    pip install -r requirements.txt

运行项目
1. 启动服务端（机器B）：

    进入server目录：

    bash
    Copy
    cd server
    运行服务端：

    bash
    Copy
    python server.py

2. 启动客户端（机器A）：

    进入client目录：

    bash
    Copy
    cd client
    修改client.py中的host为机器B的IP地址。

    运行客户端：

    bash
    Copy
    python client.py

打包为可执行文件（可选）

1. 安装PyInstaller：

    bash
    Copy
    pip install pyinstaller

2. 打包服务端：

    bash
    Copy
    cd server
    pyinstaller --onefile server.py

3. 打包客户端：

    bash
    Copy
    cd client
    pyinstaller --onefile client.py
    
4. 分发可执行文件：

    将生成的server.exe和client.exe分别分发给机器B和机器A。

    许可证
    本项目基于 MIT License 开源。