# MiniAgent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Agent-Thought--Action--Observation-7C3AED?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-OpenAI--Compatible-10A37F?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Search-Tavily-FF6B6B?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Weather-wttr.in-00A6ED?style=for-the-badge" />
</p>

---

## 项目学习笔记

**MiniAgent** 是我练习复刻 hello-agent 的基于 Python 实现的轻量级旅行助手智能体示例项目。

这个项目主要用于学习和理解智能体的核心运行流程：

```text
Thought → Action → Observation → Thought → Action → Finish
```

MiniAgent 当前可以完成一个简单但完整的旅行推荐任务：

```text
用户：我想去大连旅游，帮我推荐个景点。
```

MiniAgent 会自动执行：

```text
1. 理解用户想去的城市
2. 判断推荐景点前需要先了解天气
3. 调用天气工具查询当地实时天气
4. 根据天气调用景点搜索工具
5. 综合天气和搜索结果生成最终推荐
```

示例流程：

```text
[Thought]: 用户想去大连旅游，我需要先了解大连当前天气。
[Action]: get_weather(city="大连")

[Observation]: 大连当前天气: Smoky haze，气温29摄氏度

[Thought]: 已经知道大连当前天气，现在可以根据天气推荐景点。
[Action]: get_attraction(city="大连", weather="Smoky haze")

[Observation]: 推荐金龙寺国家森林公园等景点。

[Thought]: 已经获得天气和景点信息，可以给用户最终答复。
[Action]: Finish[根据当前天气，为你推荐金龙寺国家森林公园...]
```

---

## 核心特性

### Thought-Action-Observation 循环

MiniAgent 使用经典的智能体循环机制，让大模型不是一次性直接回答，而是一步步完成任务。

```text
Thought     智能体思考下一步该做什么
Action      智能体决定调用哪个工具
Observation 工具执行后返回的结果
Finish      智能体生成最终答案
```

---

### 工具调用能力

MiniAgent 当前内置两个工具：

| 工具                              | 作用              |
| ------------------------------- | --------------- |
| `get_weather(city)`             | 查询指定城市的实时天气     |
| `get_attraction(city, weather)` | 根据城市和天气搜索推荐旅游景点 |

通过工具机制，MiniAgent 可以把大模型的推理能力和外部真实信息连接起来。

---

### OpenAI-Compatible LLM Client

MiniAgent 使用兼容 OpenAI 接口的大模型调用方式，因此可以接入多种支持 OpenAI-compatible API 的模型服务。

例如：

```text
Gemini API
DeepSeek API
Qwen API
SiliconFlow
OpenRouter
Ollama 本地模型
```

只要服务商支持 OpenAI-compatible 接口，就可以通过统一的客户端方式接入。

---

### 联网搜索能力

MiniAgent 使用 Tavily Search API 获取旅游景点相关信息。

Tavily 在项目中扮演的是搜索工具角色：

```text
LLM 负责思考和决策
Tavily 负责联网搜索
Agent 主循环负责连接两者
```

---

### 实时天气查询

MiniAgent 使用 `wttr.in` 查询城市天气，并将天气结果作为 Observation 返回给智能体。

天气信息会影响后续景点推荐，例如：

```text
晴天 → 推荐户外景点
雨天 → 推荐室内景点
雾霾 → 推荐空气相对较好的自然景区或低强度行程
```

---

## 项目运行机制

MiniAgent 的核心流程如下：

```text
用户输入旅行需求
        ↓
LLM 生成 Thought 和 Action
        ↓
程序解析 Action
        ↓
调用对应工具
        ↓
工具返回 Observation
        ↓
Observation 加入上下文
        ↓
LLM 继续推理
        ↓
生成最终答案 Finish
```

更具体地说：

```text
User Prompt
    ↓
Prompt History
    ↓
LLM
    ↓
[Thought] + [Action]
    ↓
Action Parser
    ↓
Tool Function
    ↓
[Observation]
    ↓
LLM
    ↓
[Finish]
```

---

## 技术栈

| 技术                 | 用途                 |
| ------------------ | ------------------ |
| Python             | 项目主语言              |
| OpenAI SDK         | 调用兼容 OpenAI 接口的大模型 |
| Gemini API         | 当前可用的大模型服务之一       |
| Tavily Search API  | 联网搜索景点信息           |
| wttr.in            | 查询实时天气             |
| Regular Expression | 解析模型输出的 Action     |
| dotenv             | 管理本地环境变量           |

这个项目适合用于理解以下内容：

```text
1. 什么是 Agent Loop
2. LLM 如何决定调用工具
3. Python 如何解析模型输出
4. 工具结果如何作为 Observation 返回给模型
5. 如何让大模型完成多步骤任务
6. 如何从单文件 Demo 逐步演进为工程化 Agent 项目
```

---

## 项目定位

MiniAgent 是一个用于学习 Agent 原理的轻量级项目。

它重点展示的是：

```text
LLM + Tools + Agent Loop
```

而不是复杂的前端页面、后端部署或完整旅游平台。

通过这个项目，可以快速理解智能体最核心的工作方式：
**让大模型不只是回答问题，而是能够思考、行动、观察并完成任务。**

---

## License

This project is for learning and experimentation.
