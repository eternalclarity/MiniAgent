import requests
import os

from tavily import TavilyClient


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


# 工具字典:根据字符串找到函数
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}
