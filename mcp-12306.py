"""
    测试：使用agent调用MCPServer所提供的工具
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from common.llm_util import get_llm

async def test():
    # 获取MCPServer的客户端
    # https://www.modelscope.cn/mcp/servers/Drfccv/mcp_tool_12306
    client = MultiServerMCPClient(
        {
            "mcp_tool_12306": {
                "transport": "streamable_http",
                "url": "https://mcp.api-inference.modelscope.net/4828809eb50846/mcp"
            }
        }
    )


    # 获取MCPServer所提供的所有的工具
    tools = await client.get_tools()

    print(f"一共有{len(tools)}個工具")

    # 创建llm

    from common.llm_util import get_llm
    llm = get_llm()

    # 创建agent
    agent = create_agent(
        model=llm,
        tools=tools,
    )

    # 通过agent调用大模型 invoke, stream;  ainvoke, astream (異步)
    result = await agent.ainvoke(
        {
            "messages":[
                ("user", "查询明天深圳到长沙的车票，以表格的方式输出结果")
            ]
        }
    )

    print(result["messages"][-1].content)

asyncio.run(test())

