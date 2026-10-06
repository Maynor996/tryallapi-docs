# GLM-5.3 API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-06｜最后更新：2026-10-06
> 利益声明：作者运营 tryallapi.com。GLM-5.3 的模型 ID、发布时间、价格、上下文与参数来自智谱开放平台文档（docs.bigmodel.cn）、API 定价页、Z.ai 国际站文档与官方发布记录；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-06（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

智谱在 2026-08-19 上线新一代旗舰 **GLM-5.3**。它和 GLM-5.2 用的是同一个基础模型，所有提升都来自后训练，重点在复杂软件工程、终端操作和长程 Agent 任务。对 API 调用方来说，变化主要有三处：**思考强制开启，`thinking.type: "disabled"` 会直接报错**；**`reasoning_effort` 只接受 `low` / `high` / `max` 三个值，默认 `max`**；**1M 上下文按单一价格计费，不像 GLM-5.1 / GLM-5 那样按 32K 输入长度分档**。下面分别说明，并给出经 tryallapi.com 的 OpenAI 兼容与 Anthropic 格式（含 Claude Code）调用代码。

---

## glm-5.3 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `glm-5.3`（小写） | [智谱 GLM-5.3 模型页](https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3) |
| 发布 | 2026-08-19（开放平台发布记录；Z.ai 国际站记为 2026-08-18） | [模型与产品发布记录](https://docs.bigmodel.cn/cn/update/new-releases) · [Z.ai Release Notes](https://docs.z.ai/release-notes/new-released) |
| 定位 | 与 GLM-5.2 相同基础模型，提升全部来自后训练；强化编程与 Agent 任务 | 智谱 GLM-5.3 模型页 |
| 输入模态 | 仅文本 | 智谱 GLM-5.3 模型页 |
| 上下文 / 最大输出 | 1M tokens / 128K tokens | 智谱 GLM-5.3 模型页 · [迁移至 GLM-5.3](https://docs.bigmodel.cn/cn/guide/start/migrate-to-glm-new) |
| 思考 | 始终开启，仅支持 `thinking.type: "enabled"`；`reasoning_effort` 可选 `low` / `high` / `max`，默认 `max` | 智谱 GLM-5.3 模型页 · [深度思考](https://docs.bigmodel.cn/cn/guide/capabilities/thinking) |
| 国内价（每百万 tokens） | 输入 ¥8；输出 ¥28；缓存命中 ¥2；缓存存储限时免费 | [智谱 API 定价](https://docs.bigmodel.cn/cn/guide/start/pricing) |
| 国际价（每百万 tokens） | 输入 $1.4；缓存输入 $0.26；输出 $4.4；缓存存储限时免费 | [Z.ai Pricing](https://docs.z.ai/guides/overview/pricing) |
| 工具调用 | Function Calling（`tool_choice` 默认且仅支持 `auto`）；支持 `tool_stream=true` 流式输出工具参数 | [工具调用](https://docs.bigmodel.cn/cn/guide/capabilities/function-calling) · [工具流式输出](https://docs.bigmodel.cn/cn/guide/capabilities/stream-tool) |
| 官方 Base URL（国内） | Chat Completion：`https://open.bigmodel.cn/api/paas/v4`；Response：`https://open.bigmodel.cn/api/v1`；Anthropic：`https://open.bigmodel.cn/api/anthropic` | 智谱 GLM-5.3 模型页 |
| tryallapi.com | **已上架** `glm-5.3`；端点 `openai`（/v1/chat/completions）与 `anthropic`（/v1/messages） | `/api/pricing` 2026-10-06 |
| Base URL（聚合） | OpenAI 兼容：`https://tryallapi.com/v1`；Anthropic / Claude Code：`https://tryallapi.com` | tryallapi.com |

**三行结论**

1. GLM-5.3 不能关思考：从 GLM-5.2 迁移时，把 `disabled` 改成 `enabled` 并把 `reasoning_effort` 设为 `low`，否则请求失败。
2. 官方国内价 ¥8 / ¥28 / 缓存命中 ¥2，1M 上下文内不分输入长度档位；国际价 $1.4 / $4.4 / $0.26。
3. tryallapi.com 标定基价与 Z.ai 国际价一致（$1.40 / $4.40 / $0.26），实际 ≈ 基价 × 分组倍率（0.6～2.2），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、思考只能开不能关：reasoning_effort 三档与迁移陷阱

GLM-5.3 是强制思考模型。官方参数表如下：

| 参数 | 可选值 | 默认 | 说明 |
| --- | --- | --- | --- |
| `thinking.type` | `enabled` | `enabled` | 只支持开启思考；传 `disabled` 报错 |
| `reasoning_effort` | `low`、`high`、`max` | `max` | `low` 轻量推理；`high` 增强推理；`max` 深度推理 |

和 GLM-5.2 相比，最容易踩坑的是取值范围变窄了：

| 写法 | GLM-5.2（标准 API） | GLM-5.3（标准 API） |
| --- | --- | --- |
| `thinking.type: "disabled"` | 支持，直接回答 | **报错** |
| `reasoning_effort: "none"` / `"minimal"` | 放弃思考 | **报错**（仅支持 max / high / low） |
| `reasoning_effort: "medium"` / `"xhigh"` | 分别映射为 high / max | **报错** |
| `reasoning_effort: "low"` | 映射为 high | 轻量推理（`low` 档仅 GLM-5.3 支持） |

注意：上面「报错」是**标准 API** 的规则。GLM Coding Plan 端点会做容错映射，比如 `thinking.type` 为 `disabled` / `false` 时按 `low` 继续请求，`minimal` 映射为 `low`，`medium` 映射为 `high`。所以同一段代码在 Coding Plan 能跑、换到按量 API 却报 400，多半是这个原因。

怎么选档：官方在 Z.ai Code Bench 上公布的数据是，Max 档每项任务平均输出约 7.5 万 token，High 档约 5 万 token。思考 token 直接影响输出费用，日常补全、改写类任务用 `low`，复杂编码和长程 Agent 用 `max`（官方推荐）。

采样参数方面，官方迁移指南给出的默认值是 `temperature=1.0`、`top_p=0.95`，建议两者只调一个。

---

## 二、1M 上下文不分档：GLM-5.3 的计价结构

GLM-5.1、GLM-5 都按 32K 输入长度分两档计价，GLM-5.3 与 GLM-5.2 一样不分档：

| 模型 | 计价档位 | 输入 | 输出 | 缓存命中 |
| --- | --- | --- | --- | --- |
| **GLM-5.3** | 1M 上下文统一价 | ¥8 | ¥28 | ¥2 |
| GLM-5.2 | 1M 上下文统一价 | ¥8 | ¥28 | ¥2 |
| GLM-5.1 | 输入 [0, 32K) | ¥6 | ¥24 | ¥1.3 |
| GLM-5.1 | 输入 ≥32K | ¥8 | ¥28 | ¥2 |

（单位：元 / 百万 tokens，来自智谱 API 定价页；缓存存储当前限时免费。）

几点实务结论：

- **短请求场景**：输入普遍低于 32K 的业务，GLM-5.3 单价比 GLM-5.1 的低档贵（¥8 vs ¥6）；长上下文和 Agent 场景两者同价，GLM-5.3 能力更强。
- **缓存是主要省钱手段**：缓存命中价 ¥2，是输入价的 1/4。上下文缓存为隐式自动识别，不需要手动配置；官方建议重复前缀在 500 token 以上才容易命中，命中数量看 `usage.prompt_tokens_details.cached_tokens`。
- **固定前缀**：system prompt、工具定义、知识库放在最前面且保持完全一致，只在末尾追加消息。

---

## 三、工具调用：tool_stream、交错思考与 reasoning_content 回传

GLM-5.3 的 Function Calling 有三个要注意的点：

| 能力 | 官方说明 | 接入要点 |
| --- | --- | --- |
| `tool_choice` | 默认且仅支持 `auto` | 不要传强制调用某个函数的写法 |
| 工具流式输出 | `stream=True` + `tool_stream=True`（默认关闭） | 流式拼接 `delta.tool_calls[*].function.arguments`；平台不会替你执行工具 |
| 交错式思考 | 默认支持，模型可在工具调用之间、收到工具结果后继续思考 | **必须把 `reasoning_content` 随 assistant 消息一起回传** |
| 保留式思考 | 标准 API 默认关闭，Coding Plan 端点默认开启 | 标准 API 传 `"thinking": {"type": "enabled", "clear_thinking": false}`，并原样回传完整的 reasoning content |

保留式思考主要推荐 Coding / Agent 场景使用。官方要求回传的 reasoning content 与原始生成序列完全一致，不要重排或修改，否则效果和缓存命中率都会下降。

流式响应里，思考在 `delta.reasoning_content`，正式回答在 `delta.content`，前端应分开渲染。

---

## 四、GLM-5.3 API 价格：官方 vs tryallapi.com

### 官方价

| 计费项（每百万 tokens） | 国内（智谱开放平台） | 国际（Z.ai） |
| --- | --- | --- |
| 输入 | ¥8 | $1.4 |
| 输出 | ¥28 | $4.4 |
| 缓存命中 | ¥2 | $0.26 |
| 缓存存储 | 限时免费 | 限时免费 |

### tryallapi.com（≈ 基价 × 分组倍率）

`glm-5.3`：`model_ratio=0.7`、`completion_ratio≈3.143`、`cache_ratio=0.186`，换算基价为输入 $1.40、输出 $4.40、缓存读约 $0.26（与 Z.ai 国际价一致）。2026-10-06 可见分组：

| 分组 | 倍率 | 输入估算 | 输出估算 | 缓存读估算 |
| --- | --- | --- | --- | --- |
| Self-Deployed-1 | 0.6 | $0.84 | $2.64 | ≈ $0.156 |
| Self-Deployed-2 | 1 | $1.40 | $4.40 | ≈ $0.26 |
| Self-Deployed-3 | 1.5 | $2.10 | $6.60 | ≈ $0.39 |
| Alibaba-3 | 2.2 | $3.08 | $9.68 | ≈ $0.573 |
| glm-1 | 2.2 | $3.08 | $9.68 | ≈ $0.573 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。不同分组对应不同上游线路，按需求选择。**以控制台为准。**

怎么选：只用 GLM、需要 GLM Coding Plan 套餐或智谱官方发票 → 智谱开放平台直连；同一个项目里还要调 Claude、GPT、DeepSeek 等，希望一个 Key、一份账单 → tryallapi.com。

---

## 五、GLM-5.3 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Python（OpenAI 兼容，经 tryallapi）

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="glm-5.3",
    messages=[{"role": "user", "content": "这个 Go 服务的 goroutine 泄漏可能出在哪里？"}],
    max_tokens=32768,                              # 最大 128K，思考也会消耗输出
    extra_body={
        "thinking": {"type": "enabled"},           # GLM-5.3 只能是 enabled
        "reasoning_effort": "high",                # low / high / max，默认 max
    },
)
msg = r.choices[0].message
print(getattr(msg, "reasoning_content", None))   # 思考内容
print(msg.content)                               # 正式回答
```

`thinking`、`reasoning_effort` 通过 `extra_body` 透传；经聚合调用时先发一条短请求，确认返回里 `reasoning_content` 的结构，再决定前端如何解析。

### 3. 流式 + 工具参数流式（tool_stream）

```python
tools = [{"type": "function", "function": {
    "name": "run_tests",
    "description": "在指定目录运行单元测试",
    "parameters": {"type": "object",
                   "properties": {"path": {"type": "string"}},
                   "required": ["path"]},
}}]

stream = client.chat.completions.create(
    model="glm-5.3",
    messages=[{"role": "user", "content": "跑一下 ./pkg/cache 的测试并告诉我结果"}],
    tools=tools,
    tool_choice="auto",                            # 仅支持 auto
    stream=True,
    extra_body={"thinking": {"type": "enabled"}, "reasoning_effort": "low", "tool_stream": True},
)
reasoning, content, calls = "", "", {}
for chunk in stream:
    if not chunk.choices:
        continue
    d = chunk.choices[0].delta
    if getattr(d, "reasoning_content", None):
        reasoning += d.reasoning_content
    if d.content:
        content += d.content
    for tc in d.tool_calls or []:
        c = calls.setdefault(tc.index, {"id": tc.id, "name": "", "arguments": ""})
        if tc.function.name:
            c["name"] = tc.function.name
        if tc.function.arguments:
            c["arguments"] += tc.function.arguments
print(calls)
# 回传工具结果时，assistant 消息里要带上 reasoning_content（交错式思考要求）
```

### 4. Anthropic SDK（Anthropic 格式，经 tryallapi）

```python
# pip install -U anthropic
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["TRYALLAPI_KEY"],
    base_url="https://tryallapi.com",   # Anthropic 协议不带 /v1
)
msg = client.messages.create(
    model="glm-5.3",
    max_tokens=8192,
    messages=[{"role": "user", "content": "给这个 Rust 函数补上错误处理并解释改动"}],
)
for block in msg.content:
    if block.type == "text":
        print(block.text)
```

cURL 版本：

```bash
curl https://tryallapi.com/v1/messages \
  -H "x-api-key: $TRYALLAPI_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.3","max_tokens":1024,"messages":[{"role":"user","content":"ping"}]}'
```

### 5. Claude Code（经 tryallapi）

```bash
export ANTHROPIC_BASE_URL="https://tryallapi.com"
export ANTHROPIC_AUTH_TOKEN="$TRYALLAPI_KEY"
export ANTHROPIC_MODEL="glm-5.3"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5.3"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5.3"
claude
```

智谱官方的 Claude Code 切换指南（面向 GLM Coding Plan）还建议设置 `CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000` 来匹配 1M 上下文，并在会话中用 `/effort` 切换思考强度（默认 max）。

### 6. 对照：官方直连（国内）

```python
# OpenAI 兼容
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4")

# Anthropic 兼容
client = anthropic.Anthropic(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/anthropic")
```

官方提示：订阅过 GLM Coding Plan 的账号（含已过期），目前只能通过 OpenAI Chat Completion 协议调用模型 API。

---

## 六、常见报错与排查

| 报错 / 现象 | 原因 | 处理 |
| --- | --- | --- |
| 400，迁移后请求失败 | 仍传 `thinking.type: "disabled"` | 改为 `enabled`，`reasoning_effort` 设 `low` |
| 400，`reasoning_effort` 不合法 | 传了 `medium` / `xhigh` / `minimal` / `none` | 标准 API 只接受 `low` / `high` / `max` |
| 回答前等待很久、输出费用偏高 | 默认 `max` 深度推理 | 轻任务改用 `low` 或 `high` |
| 工具调用多轮后推理不连贯 | 回传时丢掉了 `reasoning_content` | assistant 消息原样带上 `reasoning_content` |
| 强制指定函数无效 | `tool_choice` 仅支持 `auto` | 用 prompt 和工具描述引导调用 |
| 缓存一直不命中 | 前缀太短或每次有变化 | 固定前缀 500 token 以上，变化内容放末尾 |
| 图片输入报错 | GLM-5.3 仅支持文本 | 改用多模态的 GLM-5.3-Flash / FlashX |
| Anthropic 格式 404 | Base URL 多写了 `/v1` | SDK / Claude Code 用 `https://tryallapi.com` |

---

## 七、GLM-5.3 FAQ

**Q1：GLM-5.3 的 API 模型 ID 是什么？**  
`glm-5.3`（全小写），智谱开放平台、Z.ai 与 tryallapi.com 均使用这个 ID。

**Q2：GLM-5.3 什么时候发布的？**  
智谱开放平台发布记录为 2026-08-19 上线，Z.ai 国际站发布记录为 2026-08-18。

**Q3：GLM-5.3 官方价格多少？**  
国内每百万 tokens：输入 ¥8、输出 ¥28、缓存命中 ¥2，缓存存储限时免费；国际价输入 $1.4、缓存输入 $0.26、输出 $4.4。1M 上下文内不分输入长度档位。

**Q4：上下文和最大输出是多少？**  
上下文 1M tokens，最大输出 128K tokens，目前只支持文本输入。

**Q5：GLM-5.3 能关闭思考吗？**  
不能。GLM-5.3 始终启用思考，传 `thinking.type: "disabled"` 会报错；想要更快、更省，就把 `reasoning_effort` 设为 `low`。

**Q6：reasoning_effort 有哪些取值？**  
标准 API 只接受 `low`、`high`、`max`，默认 `max`，其他值会报错；GLM Coding Plan 端点会把 `minimal` 映射为 `low`、`medium` 映射为 `high`、`xhigh` 映射为 `max`。

**Q7：GLM-5.3 工具调用有什么限制？**  
`tool_choice` 默认且仅支持 `auto`；可用 `stream=True` 加 `tool_stream=True` 流式获取工具参数；多轮工具调用需回传 `reasoning_content` 以保持交错式思考连贯。

**Q8：国内怎么经 tryallapi 调用 GLM-5.3？**  
OpenAI 兼容用 `base_url=https://tryallapi.com/v1`，Anthropic SDK 与 Claude Code 用 `https://tryallapi.com`，Key 放在 `TRYALLAPI_KEY`，模型填 `glm-5.3`；计费 ≈ 基价 $1.40 / $4.40 × 分组倍率（0.6～2.2），以控制台为准。

---

## 相关阅读

- 官方参考：[GLM-5.3 模型页](https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3) · [智谱 API 定价](https://docs.bigmodel.cn/cn/guide/start/pricing) · [迁移至 GLM-5.3](https://docs.bigmodel.cn/cn/guide/start/migrate-to-glm-new) · [深度思考](https://docs.bigmodel.cn/cn/guide/capabilities/thinking) · [思考模式](https://docs.bigmodel.cn/cn/guide/capabilities/thinking-mode) · [工具调用](https://docs.bigmodel.cn/cn/guide/capabilities/function-calling) · [工具流式输出](https://docs.bigmodel.cn/cn/guide/capabilities/stream-tool) · [上下文缓存](https://docs.bigmodel.cn/cn/guide/capabilities/cache) · [Claude API 兼容](https://docs.bigmodel.cn/cn/guide/develop/claude/introduction)
- 国际站：[Z.ai GLM-5.3](https://docs.z.ai/guides/llm/glm-5.3) · [Z.ai Pricing](https://docs.z.ai/guides/overview/pricing) · [GLM-5.3 技术博客](https://z.ai/blog/glm-5.3)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入大模型 API 的实践问题。*
*首发：2026-10-06｜最后更新：2026-10-06｜更新日志：2026-10-06 首版（价格与参数取自智谱开放平台、Z.ai 官方文档与 tryallapi.com 公开接口，取数时间 2026-10-06，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
