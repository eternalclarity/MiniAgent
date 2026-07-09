import requests
import os
import re
import json

from tavily import TavilyClient
from memory import load_memory, update_memory
from datetime import date


def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 来查询指定城市的天气信息
    """

    # api baseurl
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # 发送请求并提取返回的Json数据
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 提取天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        # 格式化成自然语言返回
        return f"{city}当前天气:{weather_desc}，气温{temp_c}摄氏度"

    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"


def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐
    """

    # 从环境变量中读取API密钥
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量。"

    # 初始化tavily客户端
    tavily = TavilyClient(api_key=api_key)

    # 构建查询
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"

    try:
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        # 如果返回结果中有answer字段，直接使用
        if response.get("answer"):
            return response["answer"]

        # 没有 answer字段, 格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        if not formatted_results:
            return "抱歉，没有找到相关的旅游景点推荐。"
        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)
    except Exception as e:
        return f"错误:执行Tavily搜索时出现问题 - {e}"


def read_memory() -> str:
    """
    读取记忆
    """

    memory = load_memory()
    return str(memory) if memory else "暂无用户偏好记忆"


def save_memory(key, value: str) -> str:
    """
    保存记忆
    """

    update_memory(key, value)
    return f"已保存用户偏好: {key} = {value}"


def check_ticket_status(attraction: str, date_str: str = "") -> str:
    """
    查询景点门票状态。
    """

    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量。"

    if not date_str:
        date_str = date.today().isoformat()

    tavily = TavilyClient(api_key=api_key)

    query = f"{attraction} {date_str} 门票 预约 售罄 余票"
    response = tavily.search(
        query=query,
        search_depth="basic",
        include_answer=True,
        max_results=5
    )

    texts = []

    if response.get("answer"):
        texts.append(response["answer"])

    for item in response.get("results", []):
        texts.append(item.get("title", ""))
        texts.append(item.get("content", ""))

    text = "\n".join(texts)

    sold_out_pattern = r"售罄|约满|已约满|无票|暂无余票|预约已满|sold out"
    available_pattern = r"有票|可预约|余票|正常预约|可购买|available"

    if re.search(sold_out_pattern, text, re.IGNORECASE):
        status = "sold_out"
        reason = "搜索结果中出现售罄、约满或无票相关信息"
    elif re.search(available_pattern, text, re.IGNORECASE):
        status = "available"
        reason = "搜索结果中出现有票、可预约或余票相关信息"
    else:
        status = "unknown"
        reason = "未能从搜索结果中可靠判断门票状态"

    return json.dumps({
        "attraction": attraction,
        "date": date_str,
        "status": status,
        "reason": reason,
        "query": query
    }, ensure_ascii=False)


def get_alternative_attraction(city: str, original: str, preference: str = "") -> str:
    """
    查询替代景点
    """
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "错误: 未配置 TAVILY_API_KEY 环境变量。"

    tavily = TavilyClient(api_key=api_key)
    query = f"{city} {original} 门票售罄 替代景点推荐 {preference}"

    response = tavily.search(query=query, search_depth="basic", include_answer=True)
    if response.get("answer"):
        return response["answer"]

    results = response.get("results", [])
    if not results:
        return "没有找到合适的备选景点。"

    return "\n".join(
        f"- {item['title']}: {item['content']}"
        for item in results[:3]
    )


# 工具字典:根据字符串找到函数
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
    "read_memory": read_memory,
    "save_memory": save_memory,
    "check_ticket_status": check_ticket_status,
    "get_alternative_attraction": get_alternative_attraction,
}
