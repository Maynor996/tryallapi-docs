# 混元 Hy4 Preview API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-05｜最后更新：2026-10-05
> 利益声明：作者运营 tryallapi.com。Hy4 preview 的参数、价格与调用方式来自腾讯官方发布稿与腾讯云 TokenHub「混元调用指南」；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-05（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

2026-08-28，腾讯混元发布并开源新一代大语言模型 **Hy4 preview**：总参数 770B、激活参数 49B，上下文突破 1M，定位「为生产力而生」，重点优化软件工程、办公分析、游戏开发和科研场景。官方定价每百万 tokens 输入 ¥6、输出 ¥18，缓存命中最低 ¥0.3。本文讲清楚它和 Hy3 的区别、思考模式参数，以及如何经 tryallapi.com 调用。

---

## Hy4 preview 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `hy4-preview` | [TokenHub 混元调用指南](https://www.tencentcloud.com/zh/document/product/1300/80695) |
| 发布 | 2026-08-28，同步开源 | [腾讯官方发布稿](https://www.tencent.com/zh-cn/tencent-releases-and-open-sources-tencent-hy4-preview/) |
| 参数规模 | 总参数 770B，激活参数 49B | 官方发布稿 |
| 上下文 / 最大输入 / 最大输出 | 1M / 960K / 64K | TokenHub 调用指南 |
| 协议 | OpenAI Chat Completions、OpenAI Responses、Anthropic Messages | TokenHub 调用指南 |
| 官方价（每百万 tokens） | 输入 ¥6；输出 ¥18；缓存命中最低 ¥0.3 | 官方发布稿 |
| 思考强度 | `reasoning_effort` 默认 `high` | TokenHub 调用指南 |
| 官方文档示例 Base URL | `https://tokenhub-intl.tencentcloudmaas.com/v1` | TokenHub 调用指南 |
| tryallapi.com | **已上架** `hy4-preview`；端点 `openai`、`anthropic`；分组 hunyuan-1 | `/api/pricing` 2026-10-05 |
| Base URL（聚合） | `https://tryallapi.com/v1` | tryallapi.com |

**三行结论**

1. Hy4 preview 的上下文是 Hy3 的 4 倍（1M vs 256K），但最大输出 64K，比 Hy3 的 128K 还少一半；需要超长输出的任务要拆段。
2. 思考模式下做工具调用，官方要求每一轮都回填历史 `reasoning_content`，否则效果会打折扣。
3. tryallapi.com 标定基价 $0.834 / $2.501，当前仅 hunyuan-1 分组（倍率 1.9），实际 ≈ $1.585 / $4.752（美元额度），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、Hy4 preview 和 Hy3 怎么选

TokenHub 同时提供两代混元主力模型，规格差异很明显：

| 对比项 | `hy4-preview` | `hy3` |
| --- | --- | --- |
| 定位 | 新一代生产力模型，Agent 与复杂任务执行全面升级 | 兼顾效果与性价比，强化 Coding、长文、推理和 Agent |
| 上下文窗口 | 1M | 256K |
| 最大输入 | 960K | 192K |
| 最大输出 | 64K | 128K |
| 默认 `reasoning_effort` | `high` | `high` |

选型建议：

- **整仓代码、长合同、多份财报一起读** → Hy4 preview，960K 输入能一次塞进去；
- **一次要生成很长的文档或代码文件**（超过 64K tokens）→ Hy3 的 128K 输出更合适，或者让 Hy4 分章节输出；
- Hy4 目前是 preview 版本，官方说明正式版会跟进，「Hy4 的下一批模型也将在近期陆续上线」，生产环境建议在配置里保留模型名开关，方便切换。

---

## 二、官方披露的实测：盲测与自我优化

腾讯给出的几组数字，比通用榜单更贴近真实工作流：

- **内部工程盲测**：163 名内部专家、203 个工程任务，Hy4 preview 均分 2.99/4，略高于 GLM 5.3（2.92）和 Kimi K3（2.94）；
- **参与自身研发**：Hy4 preview 首次参与训练方法、数据策略、评估体系和底层算子的自动优化，形成初步的「递归自我改进」闭环；
- **推理基础设施优化**：模型自主分析推理系统瓶颈，围绕算子融合、通信优化多轮迭代，端到端吞吐相较基线提升 31.8%。

这些都是腾讯官方口径，适合作为选型参考；落到自己的业务，仍建议用 20～50 条真实任务做小规模对比。

---

## 三、混元 Hy4 preview API 价格：官方 vs tryallapi.com

### 官方价

| 计费项（每百万 tokens） | 价格 |
| --- | --- |
| 输入 | ¥6 |
| 输出 | ¥18 |
| 缓存命中 | 最低 ¥0.3 |

### tryallapi.com（≈ 基价 × 分组倍率）

`hy4-preview`：`model_ratio=0.417`、`completion_ratio≈3`、`cache_ratio=0.05`，换算基价为输入 $0.834、输出 $2.501、缓存读约 $0.042。2026-10-05 只有一个可用分组：

| 分组 | 倍率 | 输入估算 | 输出估算 | 缓存读估算 |
| --- | --- | --- | --- | --- |
| hunyuan-1 | 1.9 | ≈ $1.585 | ≈ $4.752 | ≈ $0.079 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。**以控制台为准。**

怎么选：只用混元、已有腾讯云账号和发票流程 → TokenHub 官方直连；同一个项目还要调 Claude、GPT、DeepSeek 等，希望统一一个 Key 和账单 → tryallapi.com。

---

## 四、混元 Hy4 preview 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Python：开启深度思考

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="hy4-preview",
    messages=[{"role": "user", "content": "分析这份季度报表里毛利率下滑的三个主要原因"}],
    extra_body={"thinking": {"type": "enabled"}, "reasoning_effort": "high"},
)
msg = r.choices[0].message
# OpenAI SDK 没有声明 reasoning_content 字段，按官方示例用 getattr 读取
print("思考过程:", getattr(msg, "reasoning_content", None))
print("最终回答:", msg.content)
```

### 3. 流式输出并拿到 usage

```python
stream = client.chat.completions.create(
    model="hy4-preview",
    messages=[{"role": "user", "content": "写一个贪吃蛇网页小游戏"}],
    stream=True,
    stream_options={"include_usage": True},  # 最后一个 chunk 返回完整 usage
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:
        print("\nusage:", chunk.usage)
```

### 4. 结构化输出（JSON Schema）

```python
schema = {"type": "object",
          "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
          "required": ["name", "age"]}
r = client.chat.completions.create(
    model="hy4-preview",
    messages=[{"role": "user", "content": "提取人物信息：张三，35 岁，高级软件工程师"}],
    response_format={"type": "json_schema", "json_schema": {"name": "person_info", "schema": schema}},
)
print(r.choices[0].message.content)
```

### 5. cURL（聚合）

```bash
curl https://tryallapi.com/v1/chat/completions \
  -H "Authorization: Bearer $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"hy4-preview","messages":[{"role":"user","content":"ping"}]}'
```

经聚合透传时，先用一条短请求确认返回里是否带 `reasoning_content` 与 `reasoning_tokens`，再接入正式业务。

---

## 五、交错式思考：工具调用的回填规则

TokenHub 文档把「深度思考 + 工具调用」称为交错式思考（Interleaved Thinking），流程是：

1. 第 1 轮：模型返回 `reasoning_content` + `tool_calls`（`finish_reason=tool_calls`）；
2. 业务执行工具，把结果以 `role: "tool"`、带上 `tool_call_id` 追加到 messages；
3. **同时把第 1 轮 assistant 消息原样回写，`reasoning_content` 必须保留**；
4. 第 2 轮继续请求，模型可能再次调用工具，也可能给出最终答案；直到结束，每一轮都按此回填。

```python
assistant_msg = {
    "role": "assistant",
    "content": msg1.content,
    "reasoning_content": getattr(msg1, "reasoning_content", ""),
    "tool_calls": [{"id": tc.id, "type": tc.type,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                   for tc in (msg1.tool_calls or [])],
}
messages.append(assistant_msg)
```

另外两条官方规则：多轮对话的消息顺序须为 `system（可选）→ user → assistant → user …`，并且**必须以 user 结尾**；普通多轮对话里回写 assistant 消息时，也建议同时带上 `content` 与 `reasoning_content`，避免推理上下文丢失。

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 工具调用多轮后效果变差 | 没回填 `reasoning_content` | 整条 assistant 消息原样回写 |
| 输出到一半被截断 | 超过 64K 最大输出 | 分章节输出，或改用 Hy3 |
| 读不到 `reasoning_content` | OpenAI SDK 未声明该字段 | 用 `getattr(msg, "reasoning_content", None)` |
| 401 | TokenHub Key 与 tryallapi Key 混用 | 按 Base URL 对应 Key |
| 账单偏高 | 默认 `high` 思考，reasoning tokens 计入输出 | 简单任务降低思考强度 |

---

## 六、混元 Hy4 preview FAQ

**Q1：Hy4 preview 的模型 ID 是什么？**  
`hy4-preview`，TokenHub 与 tryallapi.com 上同名。

**Q2：官方价格多少？**  
每百万 tokens 输入 ¥6、输出 ¥18，缓存命中最低 ¥0.3（腾讯官方发布稿）。

**Q3：上下文有多长？**  
上下文窗口 1M，最大输入 960K，最大输出 64K。

**Q4：Hy4 preview 是开源的吗？**  
是。腾讯在 2026-08-28 发布时同步开源，总参数 770B、激活参数 49B。

**Q5：支持哪些协议？**  
OpenAI Chat Completions、OpenAI Responses 和 Anthropic Messages；tryallapi.com 上提供 `openai` 与 `anthropic` 两种端点。

**Q6：怎么开启或调节深度思考？**  
传 `{"thinking": {"type": "enabled"}}` 开启，`reasoning_effort` 默认 `high`；Python OpenAI SDK 通过 `extra_body` 传入。

**Q7：国内怎么经 tryallapi 调用？**  
`base_url=https://tryallapi.com/v1`，Key 用 `TRYALLAPI_KEY`，模型 `hy4-preview`。

**Q8：tryallapi 怎么计费？**  
基价 $0.834 / $2.501 × 分组倍率；2026-10-05 仅 hunyuan-1 分组（1.9），约合 $1.585 / $4.752 美元额度，以控制台为准。

---

## 相关阅读

- 官方参考：[腾讯发布并开源 Hy4 preview](https://www.tencent.com/zh-cn/tencent-releases-and-open-sources-tencent-hy4-preview/) · [TokenHub 混元调用指南](https://www.tencentcloud.com/zh/document/product/1300/80695)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入大模型 API 的实践问题。*
*首发：2026-10-05｜最后更新：2026-10-05｜更新日志：2026-10-05 首版（价格与倍率取自腾讯官方发布稿、腾讯云 TokenHub 文档与 tryallapi.com 公开接口，取数时间 2026-10-05，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
