import os
import logging
from datetime import datetime
from mcp.server.fastmcp import FastMCP  # 引入 FastMCP 框架

# 初始化 FastMCP server
mcp = FastMCP("file_info")

# 设置日志配置
logging.basicConfig(level=logging.INFO)

@mcp.tool()
async def get_file_info(file_path: str) -> str:
    """返回本地文件的基本信息，包括大小、创建时间、最后修改时间等。

    Args:
        file_path: 文件路径
    """
    try:
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return f"Error: File '{file_path}' does not exist."

        stats = os.stat(file_path)
        size = stats.st_size
        created = datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.fromtimestamp(stats.st_mtime)
        permissions = oct(stats.st_mode)[-3:]

        info = [
            f"File: {os.path.basename(file_path)}",
            f"Size: {size:,} bytes",
            f"Created: {created.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Last Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Is Directory: {os.path.isdir(file_path)}",
            f"Permissions: {permissions}",
            f"Absolute Path: {os.path.abspath(file_path)}"
        ]

        return "\n".join(info)

    except Exception as e:
        logging.error(f"Error getting file info: {str(e)}", exc_info=True)
        return f"Error getting file info: {str(e)}"

@mcp.tool()
async def list_directory(directory_path: str) -> str:
    """列出指定目录中的所有文件和目录。

    Args:
        directory_path: 目录路径
    """
    try:
        if not os.path.exists(directory_path):
            logging.error(f"Directory not found: {directory_path}")
            return f"Error: Directory '{directory_path}' does not exist."

        if not os.path.isdir(directory_path):
            logging.error(f"Not a directory: {directory_path}")
            return f"Error: '{directory_path}' is not a directory."

        items = os.listdir(directory_path)
        contents = []

        for item in sorted(items):
            full_path = os.path.join(directory_path, item)
            item_type = "Directory" if os.path.isdir(full_path) else "File"
            size = os.path.getsize(full_path)
            stats = os.stat(full_path)
            permissions = oct(stats.st_mode)[-3:]
            contents.append(f"{item_type}: {item} ({size:,} bytes) [Permissions: {permissions}]")

        return "\n".join(contents) if contents else "Directory is empty."

    except Exception as e:
        logging.error(f"Error listing directory: {str(e)}", exc_info=True)
        return f"Error listing directory: {str(e)}"
