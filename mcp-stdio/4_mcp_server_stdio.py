"""
    测试：模拟MCP Server(stdio)
"""
from mcp.server import FastMCP

mcp = FastMCP(name="demo")

@mcp.tool()
def add(a, b):
    return a + b

@mcp.resource(uri="huawei://stdio/resource")
def test_resource():
    return "get huawei stdio resource successfully"

@mcp.prompt()
def test_prompt(kw):
    return f"讲一个关于{kw}的笑话"

if __name__ == "__main__":
    print("MCP Server 启动中...")
    # run() 会阻塞，启动后会在内部处理 stdio 通信
    # 可以在 run 之前打印
    mcp.run(transport="stdio")
