from wzk_test_mcp.server import mcp


def main() -> None:
    print("Hello from wzk-test-mcp!")
    mcp.run(transport="stdio")
