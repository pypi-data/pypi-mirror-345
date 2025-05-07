
from .mcp import mcp

def main() -> None:
    print("Hello from mcp-ry-server!")
    mcp.run(transport='stdio')
