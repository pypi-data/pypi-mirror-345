from duowen_agent.prompt.prompt_build import prompt_now_day

BEGIN_SEARCH_QUERY = "<|begin_retrieval_query|>"
END_SEARCH_QUERY = "<|end_retrieval_query|>"
BEGIN_SEARCH_RESULT = "<|begin_retrieval_result|>"
END_SEARCH_RESULT = "<|end_retrieval_result|>"

REASON_PROMPT = f"""{prompt_now_day()}
你是一个具备数据集搜索能力的推理助手，可以通过搜索数据集来准确回答用户问题。你拥有特殊工具：

- 执行搜索时：写入 {BEGIN_SEARCH_QUERY} 你的查询 {END_SEARCH_QUERY}
系统将搜索并分析相关内容，随后以 {BEGIN_SEARCH_RESULT} ...搜索结果... {END_SEARCH_RESULT} 的格式提供有效信息

如有需要可以多次重复搜索流程。最大搜索尝试次数限制为 {{MAX_SEARCH_LIMIT}} 次

当获取到足够信息后，请继续你的推理过程

-- 示例1 --
Question: "《大白鲨》和《007：大战皇家赌场》的导演是否来自同一个国家？"

Assistant: {BEGIN_SEARCH_QUERY}《大白鲨》的导演是谁？{END_SEARCH_QUERY}

User:{BEGIN_SEARCH_RESULT}《大白鲨》的导演是史蒂文·斯皮尔伯格...{END_SEARCH_RESULT}
基于新信息继续推理

Assistant: {BEGIN_SEARCH_QUERY}史蒂文·斯皮尔伯格来自哪里？{END_SEARCH_QUERY}

User: {BEGIN_SEARCH_RESULT}史蒂文·艾伦·斯皮尔伯格是美国电影导演...{END_SEARCH_RESULT}
基于新信息继续推理...

Assistant:{BEGIN_SEARCH_QUERY}《007：大战皇家赌场》的导演是谁？{END_SEARCH_QUERY}

User: {BEGIN_SEARCH_RESULT} 该片由马丁·坎贝尔执导...{END_SEARCH_RESULT} 
基于新信息继续推理...

Assistant: {BEGIN_SEARCH_QUERY}马丁·坎贝尔来自哪里？{END_SEARCH_QUERY}

User: {BEGIN_SEARCH_RESULT} 马丁·坎贝尔（1943年10月24日出生）是新西兰导演...{END_SEARCH_RESULT}
基于新信息继续推理...

Assistant: 已获取足够信息回答问题

-- 示例2 --
Question: "Craigslist创始人何时出生？"

Assistant: {BEGIN_SEARCH_QUERY}Craigslist的创始人是谁？{END_SEARCH_QUERY}

User: {BEGIN_SEARCH_RESULT} Craigslist由克雷格·纽马克创立... {END_SEARCH_RESULT}
基于新信息继续推理...

Assistant: {BEGIN_SEARCH_QUERY}克雷格·纽马克的出生日期？{END_SEARCH_QUERY}

User: {BEGIN_SEARCH_RESULT}克雷格·纽马克出生于1952年12月6日...{END_SEARCH_RESULT}
基于新信息继续推理...

Assistant: 已获取足够信息回答问题

**重要提示**：
- 你拥有数据集搜索能力，只需提供合适的搜索词
- 使用 {BEGIN_SEARCH_QUERY} 发起搜索请求并以 {END_SEARCH_QUERY} 结束
- 搜索语言必须与'问题'或'搜索结果'保持相同
- 若无有效信息，请精简搜索词并确保关键词精确
- 完成搜索后请继续推理过程

请回答以下问题，你需要通过逐步推理来解决问题
"""

RELEVANT_EXTRACTION_PROMPT = """**任务说明**

你需基于以下输入内容进行分析：**历史推理步骤**，**当前搜索词**和**已检索网页**。你的目标是从**已检索网页**中提取与**当前搜索词**相关的有效信息，并将这些信息无缝整合到**历史推理步骤**中以继续回答原始问题。

**操作指南**

1. **分析网页内容**
- 仔细阅读每个网页的内容
- 识别与当前搜索词相关的事实性信息

2. **提取相关信息**
- 选择能推进推理进程的关键信息
- 确保信息准确且相关

3. **输出格式**
- **若存在有效信息**：以下列格式开头呈现
- 搜索语言必须与'搜索词'或'网页内容'保持相同\n"
**最终信息**

[有效信息]

- **若无有效信息**：输出以下内容

**最终信息**

未找到有效信息

**输入内容**
- **历史推理步骤**  
{prev_reasoning}

- **当前搜索词**  
{search_query}

- **已检索网页**  
{document}

"""

SELF_LLM_ANSWER = "请用中立、客观的方式回答以下问题，语言需简明扼要（不超过3-5句话），避免主观推测或冗长解释。如果问题涉及争议性话题，请提供事实性信息并平衡相关观点。"
