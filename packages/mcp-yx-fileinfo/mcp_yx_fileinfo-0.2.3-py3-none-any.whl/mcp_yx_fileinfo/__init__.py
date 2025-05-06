from mcp_yx_fileinfo.file_info import mcp

def main() -> None:
    print("启动 mcp-yx-fileinfo server!")
    mcp.run(transport='stdio')