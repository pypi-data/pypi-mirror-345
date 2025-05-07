from mcp.server import FastMCP

mcp = FastMCP("wzk_test")


@mcp.tool(description="通过三维运算计算a和b的结果")
def add_a_and_b(a, b):
    return a + b
