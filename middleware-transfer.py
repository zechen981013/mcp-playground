import asyncio
from typing import Literal, Optional

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


# 1. 定义工具
@tool
def get_weather(city: str) -> str:
    """查询天气"""
    return f"{city}的天气晴朗，气温25度。"


@tool
def transfer_money(amount: int, to_account: str) -> str:
    """转账工具 (敏感操作)"""
    print(f"!!! 正在执行转账: {amount} -> {to_account} !!!")
    return f"成功转账 {amount} 元给 {to_account}。"


# 2. 初始化模型
from common.llm_util import get_llm

llm = get_llm()

# 3. 配置 HumanInTheLoopMiddleware
interrupt_config = {
    "transfer_money": True,  # 需要人工审核
    "get_weather": False  # 自动执行
}
hitl_middleware = HumanInTheLoopMiddleware(interrupt_on=interrupt_config)

# 4. 创建 Agent
checkpointer = InMemorySaver()
agent = create_agent(
    model=llm,
    tools=[get_weather, transfer_money],
    middleware=[hitl_middleware],
    checkpointer=checkpointer,
)


def get_user_decision_interactive(tool_name: str, tool_args: dict, tool_call_id: str = None) -> dict:
    """交互式用户决策"""
    print(f"\n📋 待审核操作: {tool_name}")
    print(f"   参数: {tool_args}")

    while True:
        choice = input("  请选择 (a=批准, r=拒绝, e=编辑): ").strip().lower()

        if choice == 'a':
            print(f"   ✅ 已批准")
            return {"type": "approve"}
        elif choice == 'r':
            print(f"   ❌ 已拒绝")
            return {"type": "reject"}
        elif choice == 'e':
            # 编辑参数 - 注意需要保持参数类型
            new_args = {}
            for key, value in tool_args.items():
                new_val = input(f"    修改 {key} (当前: {value}): ").strip()
                # 保持原始类型
                if isinstance(value, int):
                    new_args[key] = int(new_val) if new_val else value
                elif isinstance(value, float):
                    new_args[key] = float(new_val) if new_val else value
                elif isinstance(value, bool):
                    new_args[key] = new_val.lower() == 'true' if new_val else value
                else:
                    new_args[key] = new_val if new_val else value
            print(f"   ✏️  已编辑: {new_args}")
            # 关键修复：使用 "edited_action" 字段，包含完整的工具调用信息
            return {
                "type": "edit",
                "edited_action": {
                    "name": tool_name,
                    "args": new_args
                }
            }
        else:
            print("  ❌ 无效输入，请输入 a, r 或 e")


def run_demo():
    """使用 invoke 运行演示，保留交互式决策"""
    print("=== HumanInTheLoopMiddleware 演示 (使用 invoke) ===")
    print("场景：用户让 Agent 转账，Agent 在执行前会暂停等待批准。\n")

    thread_id = "thread-1"
    config = {"configurable": {"thread_id": thread_id}}

    # 用户输入
    user_message = "请帮我转账 100 元给 Alice"
    print(f"[User]: {user_message}")
    print("-" * 50)

    current_input = {"messages": [{"role": "user", "content": user_message}]}
    current_command = None

    while True:
        try:
            # 使用 invoke 执行 Agent
            if current_command:
                result = agent.invoke(current_command, config=config)
                current_command = None
            else:
                result = agent.invoke(current_input, config=config)
                current_input = None

            # 打印结果
            if "messages" in result:
                for msg in result["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"[Agent] 调用工具: {tc['name']}({tc['args']})")
                    if hasattr(msg, "type") and msg.type == "tool":
                        print(f"[Tool] {msg.content}")
                    if hasattr(msg, "type") and msg.type == "ai" and not hasattr(msg, "tool_calls"):
                        print(f"[Agent] {msg.content}")

        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            break

        # 检查是否中断
        if "__interrupt__" in result:
            interrupt_value = result["__interrupt__"][0].value
            print(f"\n⏸️  检测到中断，等待人工审核...")

            # 获取待审核的操作
            action_requests = interrupt_value.get("action_requests", [])

            if not action_requests:
                print("⚠️  没有待审核的操作")
                break

            # 逐个审核操作
            decisions = []
            for req in action_requests:
                tool_name = req.get("name", "unknown")
                tool_args = req.get("args", {})
                tool_call_id = req.get("id")  # 获取工具调用ID

                # 调用交互式决策函数
                decision = get_user_decision_interactive(tool_name, tool_args, tool_call_id)
                decisions.append(decision)

            # 恢复执行
            current_command = Command(resume={"decisions": decisions})
            print("\n🔄 继续执行...")
            print("-" * 50)
            continue

        # 没有中断，任务完成
        print("\n✅ 任务完成")
        break


if __name__ == "__main__":
    run_demo()