from .TeaTest import mcp


def main() -> None:
    print("Hello from mcp-pokemon-server-zyq!")
    mcp.run(transport='stdio')
