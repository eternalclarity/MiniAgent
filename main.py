import re
import os

from llm import OpenAICompatibleClient
from tools import available_tools
from prompt import Agent_SYSTEM_PROMPT
from dotenv import load_dotenv


def main():
    load_dotenv()

    # 1. 配置LLM客户端
    API_KEY = os.getenv("LLM_API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL_ID = os.getenv("MODEL_ID")

    llm = OpenAICompatibleClient(MODEL_ID, API_KEY, BASE_URL)

    # 2.初始化Agent的上下文记忆
    user_prompt = input("您打算去哪个城市旅行呢，我可以帮您推荐景点！\n")
    prompt_context = [f"用户请求: {user_prompt}"]

    # 3.运行主循环,限制5轮防止Agent可能出现失控情况
    for i in range(5):
        # 3.1 构建prompt,把上下文记忆一起发给llm
        full_prompt = "\n".join(prompt_context)

        # 3.2 调用llm思考
        llm_output = llm.generate(prompt=full_prompt, system_prompt=Agent_SYSTEM_PROMPT)

        # 3.3 防止模型不听话一次性输出多个 Thought-Action,用re截断它,并加入上下文
        match = re.search(
            pattern=r'(\[Thought\]\s*:.*?\[Action\]\s*:.*?)(?=\n\s*(?:\[Thought\]\s*:|\[Action\]\s*:|\[Observation\]\s*:)|\Z)',
            string=llm_output,
            flags=re.DOTALL
        )
        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
        print(llm_output)
        prompt_context.append(f"模型输出:\n{llm_output}\n")

        # 3.4 解析并执行action
        action_match = re.search(
            pattern=r"\[Action\]\s*:\s*(.*)",
            string=llm_output,
            flags=re.DOTALL
        )
        if not action_match:
            observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 '[Thought]: ...[Action]: ...的格式。"
            observation_str = f"Observation: {observation}"
            prompt_context.append(observation_str)
            print(f"{observation_str}\n")
            continue

        action_str = action_match.group(1).strip()

        if action_str.startswith("Finish"):
            final_match = re.match(
                pattern=r"Finish\[(.*)\]\s*$",
                string=action_str,
                flags=re.DOTALL
            )
            final_answer = final_match.group(1).strip()
            print("\n" + "-" * 10 + "思考完成" + "-" * 10)
            print(f"{final_answer}")
            break

        tool_name = re.search(r"(\w+)\(", action_str).group(1)
        args_str = re.search(r"\((.*)\)", action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误:未定义的工具 '{tool_name}'"

        # 3.5 记录调用结果observation并加入上下文
        observation_str = f"[Observation]: {observation}"
        print(f"{observation_str}\n")
        prompt_context.append(observation_str)


if __name__ == "__main__":
    main()

