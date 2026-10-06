# Claude Fable 5.1 API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-06｜最后更新：2026-10-06
> 利益声明：作者运营 tryallapi.com。Claude Fable 5.1 的参数、价格与行为变更来自 Anthropic 官方文档（模型总览、模型页、What's new、定价页、effort 文档）与 anthropic.com 官方发布文章；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-06（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

Claude Fable 5.1 于 2026-09-01 发布，是 Anthropic 当前能力最强的公开可用模型，官方定位是「高难度推理与长周期 Agent 任务」。它和 Fable 5 输入、输出同价（$10 / $50），但**缓存读取只要基础输入价的 2.5%**，比 Fable 5 便宜 75%，长会话 Agent 的总成本因此明显下降。代价是 3 项破坏性变更：强制工具调用直接 400、旧模型读不了它的思考块、改动历史会让思考块失效。本文先讲这些变化，再给国内经 tryallapi.com 调用的价格与代码。

---

## claude-fable-5-1 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `claude-fable-5-1`（Bedrock：`anthropic.claude-fable-5-1`；Google Cloud / Microsoft Foundry / Claude Platform on AWS 同为 `claude-fable-5-1`） | [官方模型页](https://platform.claude.com/docs/en/models/fable-5-1/overview) |
| 发布 / 退役 | 2026-09-01 发布；退役不早于 2027-09-01 | 官方模型页 |
| 上下文 / 最大输出 | 1M tokens（整窗按标准价）/ 128K（同步 Messages API） | [What's new](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1) |
| 思考 | Adaptive thinking 始终开启；默认 effort=`high`，支持 `low` / `medium` / `high` / `xhigh` / `max` | [Effort 文档](https://platform.claude.com/docs/en/build-with-claude/effort) |
| 输入 → 输出 | 文本 + 图片 → 文本 | 官方模型页 |
| 知识截止 | 可靠知识截止 2026 年 6 月；训练数据截止 2026 年 6 月 | [模型总览](https://platform.claude.com/docs/en/about-claude/models/overview) |
| 延迟（官方相对值） | Slower（当前阵容中最慢档） | 模型总览 |
| 官方价（每百万 tokens） | 输入 $10；输出 $50；5 分钟缓存写 $12.50；1 小时缓存写 $20；缓存读 $0.25；Batch 五折（$5 / $25） | [官方定价](https://platform.claude.com/docs/en/about-claude/pricing) |
| Tokenizer | 与 Fable 5 相同（Opus 4.7 引入），同样文本比 Opus 4.7 之前的模型多约 30% tokens | What's new |
| tryallapi.com | **已上架**；端点 `anthropic`（/v1/messages）与 `openai`（/v1/chat/completions） | `/api/pricing` 2026-10-06 |
| Base URL（聚合） | OpenAI 兼容：`https://tryallapi.com/v1`；Anthropic / Claude Code：`https://tryallapi.com` | tryallapi.com |

**三行结论**

1. 官方价 $10 / $50，与 Fable 5 一致；缓存读从 $1 降到 $0.25，Anthropic 官方估算典型负载总成本降约 25%，重度 Agent 负载最多降约 45%。
2. 从 Fable 5 迁移不能只改模型名：`tool_choice` 为 `any` / `tool` 会 400，思考块只能「向上」跨模型保留，对话历史必须只追加。
3. tryallapi.com 上 Fable 5.1 的标定基价与官方一致，实际扣费 ≈ 基价 × 分组倍率（2026-10-06 可见 0.35294～2.2），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、从 Fable 5 迁移：3 项破坏性变更

官方 What's new 把 Fable 5.1 相对 Fable 5 的变化分成「3 项破坏性 + 5 项新增」。先看会让旧代码出错的 3 项：

| 变更 | 旧写法会怎样 | 新写法 |
| --- | --- | --- |
| 不支持强制工具调用 | `tool_choice` 为 `{"type":"any"}` 或 `{"type":"tool","name":"..."}` → 400 `invalid_request_error`（token 计数接口同样校验） | 保留 `auto`（默认）或 `none`；要合法 JSON 用 `strict: true` 的 strict tool use 或结构化输出；在提示词里写清「用 X 工具回答」 |
| 旧模型读不了 Fable 5.1 的思考块 | 对话从 Fable 5.1 切回 Fable 5 / Opus 5 等旧模型，这些轮次的推理会丢失；无法读取的块会被 API 静默丢弃（不计入 `input_tokens`、不计费） | 中途换模型只做「向上切换」；加 `thinking-binding-controls-2026-08-01` beta 头可在 `input_transformations` 里看到被丢弃的块 |
| 改动历史会让思考块失效 | 修改思考块之前的 `system`、`tools` 或早先消息 → 下一次请求 400（报错信息含 `The block is bound to a different conversation`） | 对话只追加；用会话中途的 system message / 中途工具变更代替改写；用服务端 compaction 或 context editing 裁剪上下文 |

关于第 3 项的生效范围：官方说明该校验对 **2026-08-31 及之后创建的账号**强制执行；更早的账号只记录不匹配，除非请求里设置了 `thinking.block_binding.prefix_mismatch_behavior`。想先摸清自己的代码有没有改历史，可以带上述 beta 头并设 `prefix_mismatch_behavior: "drop_block"` 跑一轮，再看 `input_transformations` 里有没有 `reason: "prefix_binding_mismatch"`。

以下几种常见写法都会让之后的思考块全部失效，迁移前逐项排查：

- 编辑、重排或删除较早的轮次，同时保留后面的轮次；
- 每次请求往早先轮次里临时塞一行提醒，下一次再删掉；
- 同一会话中重建顶层 `system` 或 `tools`；
- 图片 / 文档 URL 在后续请求里返回了不同的字节（校验看字节，不看 URL）。

反过来，这些操作**不会**破坏思考块：从最早处成段删除思考块、服务端 compaction / context editing、移动 `cache_control` 标记、在请求之间修改 `effort`。

与 Fable 5 **保持不变**、但从更老模型迁来的人最容易踩的限制：

- `thinking: {"type": "enabled", "budget_tokens": ...}` 和 `thinking: {"type": "disabled"}` 都返回 400，省略 `thinking` 或传 `{"type": "adaptive"}`；
- 预填 assistant 回复（prefill）返回 400；
- `temperature`、`top_p`、`top_k` 设为非默认值返回 400；
- `thinking.display` 默认 `"omitted"`，可选 `"summarized"`，原始思维链不会返回；
- 最小可缓存 prompt 长度 512 tokens。

---

## 二、缓存读 2.5%：为什么 Fable 5.1 跑长 Agent 更省钱

Fable 5.1 的缓存读倍率是 **0.025×**基础输入价，而其他 Claude 模型是 0.1×（Opus 5.5 为 0.05×）。缓存写倍率和 512 tokens 起缓存的门槛都没变。

| 计费项（每百万 tokens） | Fable 5 | Fable 5.1 | Opus 5.5 |
| --- | --- | --- | --- |
| 输入 / 输出 | $10 / $50 | $10 / $50 | $4 / $20 |
| 5 分钟缓存写 | $12.50 | $12.50 | $5 |
| 1 小时缓存写 | $20 | $20 | $8 |
| 缓存读 | $1 | **$0.25** | $0.20 |
| Batch（输入 / 输出） | $5 / $25 | $5 / $25 | $2 / $10 |

按官方价做个粗算：一次 Agent 循环请求带 200K tokens 已缓存前缀 + 5K 新输入 + 2K 输出——

- Fable 5：缓存读 0.2M × $1 = $0.20，新输入 $0.05，输出 $0.10，合计 **$0.35**；
- Fable 5.1：缓存读 0.2M × $0.25 = $0.05，新输入 $0.05，输出 $0.10，合计 **$0.20**。

Agent 循环里每一步都会重读整段上下文，缓存读占比越高，降幅越接近官方给出的「最多约 45%」。要吃到这部分优惠，前提正是上一节的「只追加」：前缀不变，缓存才命中，思考块也才有效。

其他官方计费规则：

- 1M 上下文整窗按标准单价计费，不另收长上下文溢价；
- `inference_geo: "us"`（仅美国推理）所有计费项 ×1.1；
- 被安全分类器拒绝（`stop_reason: "refusal"`）且发生在任何输出之前的请求，在误报率低的类别中会计费（2026-09-24 之前不计费）；流式中途拒绝按已输入和已输出 tokens 正常计费。官方允许的 fallback 目标是 Claude Opus 4.8 和 Claude Opus 5。

---

## 三、effort、逐条消息调档与进度更新

Fable 5.1 思考始终开启，**effort 是控制深度与成本的主开关**。官方建议：从默认 `high` 起步；最吃能力的 Agent / 编码任务升到 `xhigh` 或 `max`；常规或延迟敏感任务在评测确认质量不降后降到 `medium` / `low`。`high` 及以上要把 `max_tokens` 设大，它是「思考 + 正文」的硬上限。

另外 3 项新增能力（均为 beta）：

| 功能 | beta 头 | 用法 |
| --- | --- | --- |
| 逐条消息调 effort | `mid-conversation-output-config-2026-07-01` | 插入一条 `{"role":"system","content":[],"output_config":{"effort":"low"}}`，从下一个 user 轮生效，**不打断 prompt cache**；Fable 5 不支持，会返回 400 |
| 单轮生效的 system message | `mid-conversation-system-clear-at-2026-08-21` | system 消息加 `clear_at: "next_user_message"`，只对当前轮生效，之后不再渲染、不计输入 tokens，适合工具循环里的临时提醒 |
| 工具调用之间的进度更新 | `thinking-display-updates-2026-08-18` | `thinking.display` 设为 `"updates"`，只返回进度说明、推理仍隐藏；默认 `"omitted"` 下这些块为空，长任务前端会显得「没动静」 |

官方特别提示：在 Fable 5.1 上调 effort 优先用逐条消息的方式；改顶层 `output_config.effort` 会让缓存重来，而且模型倾向于延续之前轮次的风格，调档效果更弱。

不改代码也会出现的行为差异（相对 Fable 5）：

- **并行工具调用更不稳定**：可能一轮只发一个工具调用，增加轮次与耗时，可在提示词里加一句「批量执行相互独立的读取」；
- **长工具链中的进度说明更少**，effort 越高越明显；
- **`low` effort 下更常凭记忆作答**，少调用搜索 / 检索工具；
- **改小处也倾向重写整个文件**，输出 tokens 更多；
- 聊天中更少用粗体、标题和列表；总结文档时更可能不加引号地复述原文。

另外两点合规与数据相关信息：Fable 5.1 生成的文本在所有平台带 Anthropic 的统计文本水印（不增加 tokens、不含用户信息）；模型页注明它采用 30 天数据保留，未经 Anthropic 明确授权不提供零数据保留（ZDR）。

---

## 四、Claude Fable 5.1 API 价格：官方 vs tryallapi.com

### 官方价（2026-10-06 核对）

| 计费项 | 每百万 tokens |
| --- | --- |
| 输入 | $10.00 |
| 输出 | $50.00 |
| 5 分钟缓存写 | $12.50 |
| 1 小时缓存写 | $20.00 |
| 缓存读 | $0.25 |
| Batch API | 输入 $5、输出 $25（五折） |
| 仅美国推理（inference_geo） | 所有计费项 1.1 倍 |

### tryallapi.com 分组估算（≈ 基价 × 分组倍率）

`claude-fable-5-1`：`model_ratio=5`、`completion_ratio=5`、`cache_ratio=0.025`、5 分钟缓存写 1.25、1 小时缓存写 2，换算后标定基价与官方一致（$10 / $50 / 缓存读 $0.25）。2026-10-06 可见分组：

| 分组 | 倍率 | 输入估算 | 输出估算 | 缓存读估算 |
| --- | --- | --- | --- | --- |
| Claude-Code-1 | 0.35294 | ≈ $3.53 | ≈ $17.65 | ≈ $0.088 |
| Claude-Code-2 | 0.58824 | ≈ $5.88 | ≈ $29.41 | ≈ $0.147 |
| AWS-Claude-2 | 1.76472 | ≈ $17.65 | ≈ $88.24 | ≈ $0.441 |
| AWS-Claude-3 | 2.2 | $22.00 | $110.00 | $0.55 |
| Anthropic-Claude-1 | 2.2 | $22.00 | $110.00 | $0.55 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。缓存写同样按倍率折算，例如 Claude-Code-1 分组 5 分钟缓存写 ≈ $4.41、1 小时缓存写 ≈ $7.06。Claude-Code 分组倍率低，适合个人开发与 Claude Code；AWS / Anthropic 分组对应不同上游线路，按稳定性需求选择。**以控制台为准。**

---

## 五、Claude Fable 5.1 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Anthropic SDK（推荐，原生支持 effort / thinking）

```python
# pip install -U anthropic
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["TRYALLAPI_KEY"],
    base_url="https://tryallapi.com",   # Anthropic 协议不带 /v1
)

# max_tokens 较大时用流式，避免长请求超时
with client.messages.stream(
    model="claude-fable-5-1",
    max_tokens=32000,                      # 思考 + 正文的硬上限，high 及以上要留足
    output_config={"effort": "high"},      # low / medium / high / xhigh / max
    messages=[{"role": "user", "content": "审查这个仓库的数据库迁移脚本，列出可能导致数据丢失的步骤"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

注意：不要传 `thinking: {"type": "disabled"}`、`temperature` / `top_p` / `top_k`，也不要预填 assistant 回复；`tool_choice` 只用 `auto` 或 `none`。beta 功能（逐条调 effort、`display: "updates"`）经聚合透传时，先用一条短请求确认返回结构再上线。

### 3. OpenAI 兼容（Cursor、Dify、Cherry Studio 等）

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="claude-fable-5-1",
    messages=[{"role": "user", "content": "把这份季度财报里的关键指标整理成表格，并指出同比变化最大的三项"}],
    max_tokens=16000,
)
print(r.choices[0].message.content)
```

很多框架会默认带 `temperature=0.7` 或强制工具调用，接入 Fable 5.1 前先在框架设置里关掉。

### 4. cURL（Anthropic Messages）

```bash
curl https://tryallapi.com/v1/messages \
  -H "x-api-key: $TRYALLAPI_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-fable-5-1","max_tokens":2048,"output_config":{"effort":"low"},"messages":[{"role":"user","content":"ping"}]}'
```

### 5. Claude Code

```bash
export ANTHROPIC_BASE_URL="https://tryallapi.com"
export ANTHROPIC_AUTH_TOKEN="$TRYALLAPI_KEY"
export ANTHROPIC_MODEL="claude-fable-5-1"
claude
```

Anthropic 官方说明 Fable 5.1 在 Claude Code 中默认 High effort。Claude Code 会自动保持对话前缀不变，所以第一节的「改历史导致思考块失效」问题主要出现在自己拼 `messages` 的自研 Agent 里。

### 6. 对照：官方直连

```python
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])  # 默认 https://api.anthropic.com
```

---

## 六、常见报错与排查

| 报错 / 现象 | 原因 | 处理 |
| --- | --- | --- |
| 400：`tool_choice: type "tool" and "any" are not supported for this model.` | 强制工具调用 | 改 `auto` + strict tool use，或改用结构化输出 |
| 400：`The block is bound to a different conversation` | 回放思考块前改动了 system / tools / 历史消息 | 对话只追加；或用 `prefix_mismatch_behavior: "drop_block"` 丢弃失效块 |
| 400：thinking 相关 | 传了 `disabled` 或 `enabled` + `budget_tokens` | 省略 `thinking` 或传 `{"type": "adaptive"}` |
| 400：temperature 相关 | SDK / 框架默认带了非默认采样参数 | 删掉 `temperature` / `top_p` / `top_k` |
| 400：prefill 相关 | 最后一条是 assistant 预填 | 去掉预填，改在提示词里约束格式 |
| 输出被截断或正文为空 | `max_tokens` 被思考 tokens 用完 | 调大 `max_tokens` 并使用流式 |
| 长任务前端「没动静」 | `thinking.display` 默认 `omitted`，进度块为空 | 用 `display: "updates"`（beta）或在提示词里要求阶段性汇报 |
| `stop_reason: "refusal"` | 安全分类器拒绝 | 改写请求，或按官方方案 fallback 到 Opus 4.8 / Opus 5 |
| 401 | tryallapi Key 与 Anthropic 官方 Key 混用 | 检查 `ANTHROPIC_AUTH_TOKEN` / `x-api-key` |
| 404 | Base URL 写错（Anthropic 协议多加了 `/v1`） | Anthropic SDK / Claude Code 用 `https://tryallapi.com` |

---

## 七、Claude Fable 5.1 FAQ

**Q1：Claude Fable 5.1 的模型 ID 是什么？**  
Claude API、Google Cloud、Microsoft Foundry、Claude Platform on AWS 和 tryallapi.com 都是 `claude-fable-5-1`；Amazon Bedrock 为 `anthropic.claude-fable-5-1`。

**Q2：Claude Fable 5.1 官方价格是多少？**  
每百万 tokens 输入 $10、输出 $50、5 分钟缓存写 $12.50、1 小时缓存写 $20、缓存读 $0.25；Batch API 为 $5 / $25。除缓存读外与 Fable 5 同价。

**Q3：上下文和最大输出是多少？**  
1M tokens 上下文（默认即最大，整窗按标准价计费），同步 Messages API 最大输出 128K tokens。

**Q4：Claude Fable 5.1 什么时候发布？知识截止到什么时候？**  
2026-09-01 发布，官方承诺退役不早于 2027-09-01；可靠知识截止与训练数据截止均为 2026 年 6 月。

**Q5：能关闭思考吗？**  
不能。Fable 5.1 的 adaptive thinking 始终开启，传 `disabled` 会返回 400；想省 tokens 就把 effort 降到 `medium` 或 `low`。

**Q6：从 Fable 5 迁移要改哪些代码？**  
改模型名之后，去掉 `tool_choice` 的 `any` / `tool`，保证对话历史只追加、思考块原样回传，重新调 effort，并在 Agent 循环中留意一轮只发一个工具调用的情况，最后重跑评测。

**Q7：国内怎么调用 Claude Fable 5.1？**  
在 tryallapi.com 生成 Key：Anthropic 协议 `base_url=https://tryallapi.com`，OpenAI 兼容 `base_url=https://tryallapi.com/v1`，模型 `claude-fable-5-1`；Claude Code 设置 `ANTHROPIC_BASE_URL` 与 `ANTHROPIC_AUTH_TOKEN` 即可。

**Q8：tryallapi.com 上怎么计费？**  
标定基价与官方一致（$10 / $50 / 缓存读 $0.25），实际 ≈ 基价 × 分组倍率；2026-10-06 可见 Claude-Code-1（0.35294）到 AWS-Claude-3 / Anthropic-Claude-1（2.2）等分组，以控制台为准。

**Q9：Fable 5.1 和 Opus 5.5 怎么选？**  
官方建议多数负载先用 Opus 5.5（$4 / $20，延迟 Moderate）；高难度推理、长周期 Agent，或 Opus 5.5 调高 effort 后评测仍不达标时，再用 Fable 5.1（$10 / $50，延迟 Slower）。

---

## 相关阅读

- 官方参考：[Claude Fable 5.1 模型页](https://platform.claude.com/docs/en/models/fable-5-1/overview) · [What's new in Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1) · [模型总览](https://platform.claude.com/docs/en/about-claude/models/overview) · [Claude 定价](https://platform.claude.com/docs/en/about-claude/pricing) · [Effort 参数](https://platform.claude.com/docs/en/build-with-claude/effort) · [官方发布：Introducing Claude Fable 5.1 and Claude Mythos 5.1](https://www.anthropic.com/claude-fable-and-mythos-5-1)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入海外大模型的实践问题。*
*首发：2026-10-06｜最后更新：2026-10-06｜更新日志：2026-10-06 首版（价格与倍率取自 Anthropic 官方文档与 tryallapi.com 公开接口，取数时间 2026-10-06，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
