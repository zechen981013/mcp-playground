"""
    测试：模拟MCP Client(stdio)
    通过stdio_client启动进程：构建stdio启动参数
    建立会话：通过ClientSession构建会话session
    握手初始化：调用session.initialize()
    获取能力: 通过session.list_tools() / session.call_tools() 等获取或者使用MCP能力
"""
import asyncio

from mcp import StdioServerParameters, stdio_client, ClientSession
from mcp.client.streamable_http import streamable_http_client


async def test():
    url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            # 获取MCP Server所有的工具
            tools = await session.list_tools()
            print(tools)
            print("="*100)

            # 获取MCP Server指定的工具
            tool_result = await session.call_tool("add", arguments={"a":100, "b":200})
            print(tool_result)
            print("="*100)

            # 获取MCP Server所有的资源
            resources = await session.list_resources()
            print(resources)
            print("="*100)

            # 获取MCP Server指定的资源
            resource_result = await session.read_resource("huawei://stdio/resource")
            print(resource_result)
            print("="*100)

            # 获取MCP Server所有的提示词
            prompts = await session.list_prompts()
            print(prompts)
            print("="*100)

            # 获取MCP Server指定的提示词
            prompt_result = await session.get_prompt("test_prompt", arguments={"kw":"狗"})
            print(prompt_result)

if __name__ == "__main__":
    asyncio.run(test())

