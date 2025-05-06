from mcp_yx_fileinfo.file_info import mcp


def main() -> None:
    print("Hello from mcp-yx-fileinfo!")
    mcp.run(transport='stdio')