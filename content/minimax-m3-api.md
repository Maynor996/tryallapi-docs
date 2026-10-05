# MiniMax M3 API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-05｜最后更新：2026-10-05
> 利益声明：作者运营 tryallapi.com。MiniMax-M3 的架构、价格与参数来自 MiniMax 官方发布博客与开放平台文档；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-05（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

MiniMax 在 2026-06-01 发布 **MiniMax M3**：新注意力架构 MSA（MiniMax Sparse Attention）、1M 上下文、原生多模态（图片 + 视频输入），重点面向 Coding 与 Agent。它的 API 有两个和别家不一样的地方：**按单次请求的输入长度分 512K 两档计价**，以及 **OpenAI 格式下思考内容默认以 `<think>` 标签混在 `content` 里**。本文逐一说明。

---

## MiniMax-M3 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `MiniMax-M3` | [OpenAI 兼容接口文档](https://platform.minimaxi.com/docs/api-reference/text-openai-api.md) |
| 发布 | 2026-06-01 | [官方发布博客](https://www.minimaxi.com/blog/minimax-m3) |
| 架构 | MSA 稀疏注意力；1M 上下文下每 token 计算量为上代的 1/20，prefill 加速超 9 倍、decode 加速超 15 倍 | 官方发布博客 |
| 上下文 | 1,000,000 tokens；输出速度约 100+ TPS | [文本生成指南](https://platform.minimaxi.com/docs/guides/text-generation.md) |
| 输入模态 | 文本、图片、视频（OpenAI 兼容接口） | OpenAI 兼容接口文档 |
| 国内价（≤512K 输入，每百万 tokens） | 输入 ¥2.10；输出 ¥8.40；缓存读取 ¥0.42（永久五折后） | [官方按量计费](https://platform.minimaxi.com/docs/guides/pricing-paygo.md) |
| 国内价（>512K 输入） | 输入 ¥4.20；输出 ¥16.80；缓存读取 ¥0.84 | 官方按量计费 |
| 国际价（≤512K / >512K） | $0.30 / $1.20 / $0.06；$0.60 / $2.40 / $0.12 | [国际站按量计费](https://platform.minimax.io/docs/guides/pricing-paygo.md) |
| 官方 Base URL（国内） | OpenAI：`https://api.minimax.cn/v1`；Anthropic：`https://api.minimax.cn/anthropic` | 文本生成指南 |
| tryallapi.com | **已上架** `MiniMax-M3`；端点 `openai`；含 512K 阶梯倍率 | `/api/pricing` 2026-10-05 |
| Base URL（聚合） | `https://tryallapi.com/v1` | tryallapi.com |

**三行结论**

1. 单次请求输入 ≤512K tokens 时，M3 官方价 ¥2.1 / ¥8.4；超过 512K 整单翻倍。把输入控制在 512K 以内是最直接的省钱方法。
2. OpenAI 格式默认把思考写进 `content` 的 `<think>` 标签里，多轮对话必须**完整保留**整条 assistant 消息；想拆开显示用 `reasoning_split=true`。
3. tryallapi.com 标定基价等于官方国际价（$0.30 / $1.20），超过 512K 同样 ×2；实际 ≈ 基价 × 分组倍率（1～2.2），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、MSA 与 512K 分档：长上下文到底贵在哪

MiniMax 把 M3 的 1M 上下文归功于 MSA：相比全注意力的平方级复杂度，MSA 先对 KV 分块初筛，再在算子层做「KV outer gather Q」，官方称比开源的同类稀疏注意力算子快 4 倍以上，并且在多数对照实验中能力与全注意力打平。

但计价上，MiniMax 仍然按**单次请求的输入 tokens** 分两档：

| 档位 | 输入 | 输出 | 缓存读取 |
| --- | --- | --- | --- |
| ≤512K 输入（标准） | ¥2.10 | ¥8.40 | ¥0.42 |
| >512K 输入（标准） | ¥4.20 | ¥16.80 | ¥0.84 |
| ≤512K 输入（priority） | ¥3.15 | ¥12.60 | ¥0.63 |
| >512K 输入（priority） | ¥6.30 | ¥25.20 | ¥1.26 |

（单位：元 / 百万 tokens，均为官方「永久五折」后价格。）

实务建议：

- **Agent 长会话**：上下文涨过 512K 后整单（包括输出）都按高档计费，建议在 450K 左右触发摘要压缩；
- **缓存优先**：缓存读取只有输入价的 1/5，固定 system prompt 与工具定义、只追加消息；
- **priority 通道**按标准价 1.5 倍计费，只给 SLA 敏感的请求开（`service_tier="priority"`）。

---

## 二、thinking 与 `<think>` 标签：M3 的三种输出形态

M3 支持 thinking 与 non-thinking 两种模式，官方说明两种模式**共享同一套定价**。OpenAI 兼容接口下的行为：

| 请求参数 | 行为 |
| --- | --- |
| 省略 `thinking` 或 `{"type": "adaptive"}` | 开启 thinking |
| `{"type": "disabled"}` | 跳过 thinking，直接回答（适合对话、补全等延迟敏感场景） |
| `reasoning_split=false`（默认表现） | 思考内容以 `<think>…</think>` 保留在 `content` 中 |
| `reasoning_split=true` | 思考内容拆到 `reasoning_content` 字段 |

两条硬规则：

1. **多轮对话必须完整保留 assistant 消息**（包括 `<think>` 部分），官方文档明确要求，不要为了「干净」把思考内容剥掉再回传；
2. **`max_tokens` 包含思考 tokens**：设得太小会出现 `finish_reason=length` 且 `content` 为空，新接入建议用 `max_completion_tokens` 并留足余量。

另外，`reasoning_effort` 只对 MiniMax 更新的 `MiniMax-M3.1-Flash-Preview` 生效，对 M3 无效；该预览模型目前仅通过 MiniMax 的订阅套餐提供，按量 API 仍以 M3 为主。

---

## 三、MiniMax M3 API 价格：官方 vs tryallapi.com

`MiniMax-M3`：`model_ratio=0.15`、`completion_ratio=4`、`cache_ratio=0.2`，换算基价为输入 $0.30、输出 $1.20、缓存读 $0.06；并配置了阶梯倍率：输入超过 512K 后输入、输出、缓存均 ×2（与官方 >512K 档一致）。2026-10-05 可见分组（≤512K 档）：

| 分组 | 倍率 | 输入估算 | 输出估算 | 缓存读估算 |
| --- | --- | --- | --- | --- |
| Self-Deployed-2 | 1 | $0.30 | $1.20 | $0.06 |
| Self-Deployed-3 | 1.5 | $0.45 | $1.80 | $0.09 |
| Hailuo-3 | 2.2 | $0.66 | $2.64 | $0.132 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。**以控制台为准。**

怎么选：只用 MiniMax、需要 priority 通道或订阅套餐 → 官方开放平台；需要在同一项目里同时调用 Claude、GPT、DeepSeek 等，统一 Key 与账单 → tryallapi.com。

---

## 四、MiniMax M3 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Python（经 tryallapi，拆分思考内容）

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="MiniMax-M3",
    messages=[{"role": "user", "content": "这段 Triton kernel 为什么跑不满带宽？"}],
    max_completion_tokens=8192,              # 思考 tokens 也计入，留足余量
    extra_body={"reasoning_split": True},    # 思考内容放到 reasoning_content
)
msg = r.choices[0].message
print(getattr(msg, "reasoning_content", None))
print(msg.content)
```

`reasoning_split` 是 MiniMax 的扩展参数；经聚合透传时，先用一条短请求确认返回结构，再决定前端如何解析。

### 3. 关闭思考（低延迟场景）

```python
r = client.chat.completions.create(
    model="MiniMax-M3",
    messages=[{"role": "user", "content": "补全这个函数的 docstring"}],
    extra_body={"thinking": {"type": "disabled"}},
)
```

### 4. 视频理解

```python
r = client.chat.completions.create(
    model="MiniMax-M3",
    messages=[{"role": "user", "content": [
        {"type": "video_url", "video_url": {"url": "https://example.com/demo.mp4"}},
        {"type": "text", "text": "总结这段操作录屏里用户卡住的步骤"},
    ]}],
)
```

官方限制：视频支持 MP4 / AVI / MOV / MKV，`fps` 默认 1（可取 0.2～5），URL 或 base64 视频最大 50 MB，图片最大 10 MB，请求体最大 64 MB。

### 5. 对照：官方直连（国内）

```python
client = OpenAI(api_key=os.environ["MINIMAX_API_KEY"], base_url="https://api.minimax.cn/v1")
```

---

## 五、常见报错与排查

| 报错 / 现象 | 原因 | 处理 |
| --- | --- | --- |
| `content` 为空，`finish_reason=length` | `max_tokens` 被思考 tokens 用完 | 调大 `max_completion_tokens` |
| 前端显示一堆 `<think>` | OpenAI 格式默认把思考写进 content | 传 `reasoning_split=true` 或前端折叠显示 |
| 多轮后回答质量下降 | 回传时删掉了 `<think>` 部分 | 完整保留 assistant 消息 |
| 账单突然翻倍 | 单次输入超过 512K | 摘要压缩，控制在 512K 以内 |
| `reasoning_effort` 没效果 | 该参数只对 M3.1-Flash-Preview 生效 | M3 用 `thinking` 开关 |
| 请求体过大 | 超过 64 MB | 视频先压缩或改用文件上传 |

---

## 六、MiniMax M3 FAQ

**Q1：MiniMax M3 的模型 ID 是什么？**  
`MiniMax-M3`（注意大小写），官方与 tryallapi.com 同名。

**Q2：官方价格多少？**  
国内每百万 tokens，单次输入 ≤512K：输入 ¥2.10、输出 ¥8.40、缓存读取 ¥0.42；>512K：¥4.20 / ¥16.80 / ¥0.84。国际价 $0.30 / $1.20 / $0.06（≤512K）。

**Q3：上下文多长？**  
最高 1M tokens，依托 MSA 稀疏注意力。

**Q4：thinking 和 non-thinking 价格一样吗？**  
一样。官方说明两种模式共享同一套定价，可在请求时切换。

**Q5：怎么关闭思考？**  
OpenAI 格式传 `{"thinking": {"type": "disabled"}}`，M3 会跳过思考直接回答。

**Q6：priority 通道多少钱？**  
`service_tier="priority"` 按标准价 1.5 倍计费，例如 ≤512K 档输入 ¥3.15、输出 ¥12.60。

**Q7：国内怎么经 tryallapi 调用？**  
`base_url=https://tryallapi.com/v1`，Key 用 `TRYALLAPI_KEY`，模型 `MiniMax-M3`，OpenAI 兼容格式。

**Q8：tryallapi 怎么计费？**  
基价 $0.30 / $1.20 × 分组倍率（1、1.5、2.2），输入超过 512K 后再 ×2，以控制台为准。

---

## 相关阅读

- 官方参考：[MiniMax M3 发布博客](https://www.minimaxi.com/blog/minimax-m3) · [按量计费价格](https://platform.minimaxi.com/docs/guides/pricing-paygo.md) · [OpenAI 兼容接口](https://platform.minimaxi.com/docs/api-reference/text-openai-api.md) · [文本生成指南](https://platform.minimaxi.com/docs/guides/text-generation.md)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入大模型 API 的实践问题。*
*首发：2026-10-05｜最后更新：2026-10-05｜更新日志：2026-10-05 首版（价格与倍率取自 MiniMax 官方文档与 tryallapi.com 公开接口，取数时间 2026-10-05，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
