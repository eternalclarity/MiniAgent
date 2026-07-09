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

**MiniAgent** 是我练习复刻 hello-agents 的基于 Python 实现的简化版旅行助手智能体项目，并在此基础上进行了一些功能扩展，具体如下。

这个项目主要用于学习和理解智能体的核心运行流程：

```text
Thought → Action → Observation → Thought → Action → Finish
```

MiniAgent 当前可以完成一个带有简单状态管理的旅行推荐任务：

```text
用户：我想去大连旅游，帮我推荐个景点。我比较喜欢历史文化类景点，预算不要太高。
```

MiniAgent 会自动执行：

```text
1. 理解用户想去的城市
2. 识别并保存用户长期偏好
3. 判断推荐景点前需要先了解天气
4. 调用天气工具查询当地实时天气
5. 根据天气调用景点搜索工具
6. 推荐前检查景点门票状态
7. 如果门票售罄，自动搜索备选景点
8. 如果用户连续拒绝推荐，反思原因并调整推荐策略
```

示例流程：

```text
[Thought]: 用户想去大连旅游，并且偏好历史文化类景点、预算不要太高，我需要先保存这些长期偏好。
[Action]: save_memory(key="景点偏好", value="历史文化")

[Observation]: 已保存用户偏好: 景点偏好 = 历史文化

[Thought]: 用户想去大连旅游，我需要先了解大连当前天气。
[Action]: get_weather(city="大连")

[Observation]: 大连当前天气: Smoky haze，气温29摄氏度

[Thought]: 已经知道大连当前天气，现在可以结合用户偏好推荐景点。
[Action]: get_attraction(city="大连", weather="Smoky haze")

[Observation]: 推荐金龙寺国家森林公园等景点。

[Thought]: 我准备推荐金龙寺国家森林公园，但最终推荐前需要检查门票状态。
[Action]: check_ticket_status(attraction="金龙寺国家森林公园", date_str="2026-07-09")

[Observation]: {"attraction": "金龙寺国家森林公园", "status": "available", ...}

[Thought]: 景点门票状态可用，可以给用户最终答复。
[Action]: Finish[根据当前天气和你的偏好，为你推荐金龙寺国家森林公园...]
```

---

## 核心特性

### Thought-Action-Observation 范式循环处理LLM响应

MiniAgent 使用经典的智能体循环机制，让大模型不是一次性直接回答，而是一步步完成任务。

```text
Thought     智能体思考下一步该做什么
Action      智能体决定调用哪个工具
Observation 工具执行后返回的结果
Finish      智能体生成最终答案
```

这个循环现在不仅传递工具结果，也会传递智能体状态：

```text
Memory        用户长期偏好，例如喜欢历史文化景点、预算范围、出行方式
Agent State   当前会话状态，例如连续拒绝次数、已拒绝的推荐
User Feedback 用户对推荐的接受或拒绝反馈
```

---

### 赋予LLM本地工具调用能力

MiniAgent 当前内置以下工具：

| 工具                                                       | 作用                       |
| -------------------------------------------------------- | ------------------------ |
| `get_weather(city)`                                      | 查询指定城市的实时天气              |
| `get_attraction(city, weather)`                          | 根据城市和天气搜索推荐旅游景点          |
| `read_memory()`                                          | 读取用户长期偏好记忆               |
| `save_memory(key, value)`                                | 保存用户偏好，例如景点类型、预算、出行方式   |
| `check_ticket_status(attraction, date_str)`              | 查询景点门票状态                 |
| `get_alternative_attraction(city, original, preference)` | 当原景点门票售罄时搜索备选景点         |

通过工具机制，MiniAgent 可以把大模型的推理能力和提供的本地函数工具连接起来。

---

### 用户偏好记忆存储

MiniAgent 使用 `memory.json` 保存用户长期偏好。

当用户表达稳定偏好时，例如：

```text
我比较喜欢历史文化类景点，预算不要太高。
```

智能体可以调用：

```text
[Action]: save_memory(key="景点偏好", value="历史文化")
[Action]: save_memory(key="预算偏好", value="不要太高")
```

之后再次推荐景点时，主循环会把 `[Memory]` 放入 Prompt History，让模型在新的 Thought 中参考这些偏好。

---

### 门票状态检查与备选推荐

MiniAgent 在最终推荐具体景点前，会先调用 `check_ticket_status` 查询门票状态。

如果 Observation 显示景点门票已售罄、约满或无票，智能体不会直接结束任务，而是继续调用 `get_alternative_attraction` 搜索备选方案。

示例：

```text
[Thought]: 我想推荐故宫，但最终推荐前需要检查门票状态。
[Action]: check_ticket_status(attraction="故宫", date_str="2026-07-09")

[Observation]: {"attraction": "故宫", "status": "sold_out", ...}

[Thought]: 故宫门票已售罄，用户喜欢历史文化景点，我需要寻找同类型备选方案。
[Action]: get_alternative_attraction(city="北京", original="故宫", preference="历史文化")
```

---

### 拒绝反馈与策略反思

当智能体给出最终推荐后，程序会询问用户是否接受。

如果用户拒绝，拒绝原因会作为新的上下文加入下一轮循环：

```text
[User Feedback]: 用户拒绝了推荐，原因是: 太远了
[Agent State]: rejected_count=1, rejected_items=[...]
```

如果用户连续拒绝 3 次，主循环会加入一条特殊 Observation，要求模型先反思失败原因，再改变推荐策略。

```text
[Observation]: 用户已经连续拒绝 3 次推荐。你必须反思之前推荐失败的原因，调整推荐策略，避开 rejected_items 中的推荐，并重新调用工具获取新方案。
```

这样 MiniAgent 不只是机械地继续推荐，而是会尝试从热门景点改为小众景点、从远距离改为近距离、从高预算改为低预算，或根据用户反馈切换推荐方向。

---

### OpenAI-Compatible LLM Client调用封装

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

### 联网搜索能力工具

MiniAgent 使用 Tavily Search API 获取旅游景点相关信息。

Tavily 在项目中扮演的是搜索工具角色：

```text
LLM 负责思考和决策
Tavily 负责联网搜索
Agent 主循环负责连接两者
```

---

### 实时天气查询工具

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
读取 Memory 和初始化 Agent State
        ↓
LLM 生成 Thought 和 Action
        ↓
程序解析 Action
        ↓
调用对应工具
        ↓
工具返回 Observation
        ↓
更新 Memory / Agent State / User Feedback
        ↓
Observation 加入上下文
        ↓
LLM 继续推理
        ↓
生成最终答案 Finish
        ↓
用户接受则结束，用户拒绝则继续循环
```

更具体地说：

```text
User Prompt
    ↓
Memory + Prompt History
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
Memory / Agent State / User Feedback
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
| Tavily Search API  | 联网搜索景点、门票和备选方案信息  |
| wttr.in            | 查询实时天气             |
| JSON               | 保存本地长期记忆           |
| Regular Expression | 解析模型输出的 Action     |
| dotenv             | 管理本地环境变量           |

这个项目适合用于理解以下内容：

```text
1. 什么是 Agent Loop
2. LLM 如何决定调用工具
3. Python 如何解析模型输出
4. 工具结果如何作为 Observation 返回给模型
5. 如何在 Agent Loop 中加入长期记忆
6. 如何处理工具结果中的异常状态，例如门票售罄
7. 如何根据用户拒绝反馈触发反思和策略调整
8. 如何让大模型完成多步骤任务
9. 如何从单文件 Demo 逐步演进为工程化 Agent 项目
```

---

## 项目定位

MiniAgent 是一个用于学习 Agent 原理的轻量级项目。

它重点展示的是：

```text
LLM + Tools + Agent Loop + Memory + Feedback
```

而不是复杂的前端页面、后端部署或完整旅游平台。

通过这个项目，可以快速理解智能体最核心的工作方式：
**让大模型不只是回答问题，而是能够思考、行动、观察、记忆用户偏好，并根据反馈调整策略。**

---

## License

This project is for learning and experimentation.
