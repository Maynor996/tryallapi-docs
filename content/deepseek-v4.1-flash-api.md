# DeepSeek V4.1 API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-05｜最后更新：2026-10-05
> 利益声明：作者运营 tryallapi.com。DeepSeek V4.1 Flash 的架构、价格与参数来自 DeepSeek 官方新闻与 API 文档；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-05（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

DeepSeek 在 2026-09-10 发布 **DeepSeek V4.1 Flash**，这是 V4.1 系列目前唯一上线的型号。和以往不同，官方 API 的模型名去掉了版本号，改叫 `deepseek-flash`；tryallapi.com 上的模型 ID 则是 `deepseek-v4.1-flash`。本文把这两个名字、峰谷计价和思考模式一次讲清楚。

---

## DeepSeek V4.1 Flash 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 官方模型名 | `deepseek-flash`（模型版本 DeepSeek-V4.1-Flash） | [官方定价页](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/) |
| tryallapi.com 模型 ID | `deepseek-v4.1-flash`；端点 `openai`、`anthropic` | `/api/pricing` 2026-10-05 |
| 发布 | 2026-09-10；新价格同日 12:00 生效 | [官方发布文](https://www.deepseek.com/news/deepseek-v4-1-flash/) |
| 结构 | 552B 参数 MoE，Causal-Encoder-Decoder，输入激活 8B、输出激活 16B | 官方发布文 |
| 上下文 / 最大输出 | 1M / 384K | 官方定价页 |
| 能力 | 思考模式（默认开）与非思考模式、工具调用、JSON Output、图像理解、Anthropic 与 Responses 兼容 | 官方定价页 |
| 官方价（高峰，每百万 tokens） | 缓存命中 ¥0.04；未命中 ¥2；输出 ¥8（美元 $0.006 / $0.30 / $1.20） | 官方定价页 |
| 官方价（空闲） | 高峰价的一半：¥0.02 / ¥1 / ¥4 | 官方定价页 |
| 官方 Base URL | OpenAI：`https://api.deepseek.com`；Anthropic：`https://api.deepseek.com/anthropic` | 官方定价页 |
| Base URL（聚合） | `https://tryallapi.com/v1` | tryallapi.com |

**三行结论**

1. V4.1 Flash 官方高峰价 ¥2 / ¥8（输入未命中 / 输出），空闲时段直接半价；缓存命中只要 ¥0.04，Agent 类长会话最省钱。
2. 官方旧名 `deepseek-v4-flash` 已被路由到 V4.1 Flash；2026-09-14 12:00 之后 `deepseek-v4-pro` 也按 V4.1 Flash 服务和计费（直到 V4.1 Pro 上线）。
3. tryallapi.com 标定基价等于官方美元高峰价（$0.30 / $1.20），实际 ≈ 基价 × 分组倍率（1 或 1.5），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、两个模型名与「静默路由」：先把配置理清

DeepSeek 这次改名带来的混乱，比模型本身更容易踩坑：

| 你在代码里写的 | 实际由谁服务 | 计费 |
| --- | --- | --- |
| `deepseek-flash`（官方直连） | DeepSeek-V4.1-Flash | Flash 价 |
| `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp`（官方直连） | 已下线，临时路由到 V4.1 Flash | Flash 价 |
| `deepseek-v4-pro`（官方直连，2026-09-14 12:00 后） | 路由到 V4.1 Flash，直到 V4.1 Pro 上线 | Flash 价 |
| `deepseek-v4.1-flash`（tryallapi.com） | tryallapi 上架的 V4.1 Flash | 基价 × 分组倍率 |

建议：官方直连统一改成 `deepseek-flash`，不要依赖「临时路由」；经 tryallapi 调用则写 `deepseek-v4.1-flash`。评测报告里同时记下模型名和响应里的版本信息，否则过几个月很难复现「当时到底跑的是哪个模型」。

**为什么 Flash 能替代 V4 Pro？** 官方说明：V4.1 Flash 采用输入、输出不对称的新结构，输入激活只有 8B、输出激活 16B，并且 KV Cache 对 HBM 的需求降到上一代的 1/4、对 SSD 的需求降到 1/8。经官方测试，它在性能、费用、速度、总用时上全面超过 V4 Pro，所以官方计划有序下线 V4 Pro。

---

## 二、峰谷计价：同一个任务，挑时间就能省一半

官方高峰时段为 **北京时间周一至周五 9:00–12:00、14:00–18:00**（不含法定节假日），其余时间（含周末、节假日全天）为空闲时段，价格是高峰的一半：

| 计费项（每百万 tokens） | 高峰 | 空闲 |
| --- | --- | --- |
| 输入（缓存命中） | ¥0.04（$0.006） | ¥0.02（$0.003） |
| 输入（缓存未命中） | ¥2（$0.30） | ¥1（$0.15） |
| 输出 | ¥8（$1.20） | ¥4（$0.60） |

实务做法：

- **批量离线任务**（数据清洗、批量摘要、评测集跑分）放到晚上或周末；
- **在线 Agent** 无法挪时间，就靠缓存：缓存命中价只有未命中的 1/50，固定 system prompt 和工具定义、对话只追加，是最直接的降本手段；
- 官方并发上限为 2500（Flash），高并发压测前先看限速文档。

tryallapi.com 公开接口没有峰谷字段，按基价 × 分组倍率估算即可，见第三节。

---

## 三、DeepSeek V4.1 Flash API 价格：官方 vs tryallapi.com

`deepseek-v4.1-flash`：`model_ratio=0.15`、`completion_ratio=4`、`cache_ratio=0.02`，换算基价为输入 $0.30、输出 $1.20、缓存读 $0.006（与官方美元高峰价一致）。2026-10-05 可见分组：

| 分组 | 倍率 | 输入估算 | 输出估算 | 缓存读估算 |
| --- | --- | --- | --- | --- |
| Self-Deployed-2 | 1 | $0.30 | $1.20 | $0.006 |
| Self-Deployed-3 | 1.5 | $0.45 | $1.80 | $0.009 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。**以控制台为准。**

怎么选：只用 DeepSeek、能在官方开票充值、任务可挪到空闲时段 → 官方直连最便宜；已有 GPT / Claude / Gemini 工具链、希望一个 Key 管理多家模型 → 走 tryallapi.com。

---

## 四、DeepSeek V4.1 Flash 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Python（OpenAI SDK，经 tryallapi）

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="deepseek-v4.1-flash",
    messages=[{"role": "user", "content": "给这段 SQL 找出可能的慢查询原因"}],
    reasoning_effort="high",                      # low / high / max
    extra_body={"thinking": {"type": "enabled"}}, # 非思考模式改为 "disabled"
)
msg = r.choices[0].message
print(getattr(msg, "reasoning_content", None))  # 思维链（若上游返回）
print(msg.content)
```

思考强度与开关参数来自 DeepSeek 官方「思考模式」文档；经聚合透传时，先用一条短请求确认返回里是否带 `reasoning_content`。

### 3. 对照：官方直连

```python
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
r = client.chat.completions.create(model="deepseek-flash", messages=[{"role": "user", "content": "ping"}])
```

### 4. cURL（聚合）

```bash
curl https://tryallapi.com/v1/chat/completions \
  -H "Authorization: Bearer $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4.1-flash","messages":[{"role":"user","content":"ping"}],"thinking":{"type":"disabled"}}'
```

### 5. 图片理解

V4.1 Flash 原生支持视觉，按 OpenAI 多模态格式在 `content` 里放 `image_url` 即可；旧的 `deepseek-v4-flash-vision-exp` 不必再单独接。

---

## 五、思考模式与工具调用的两个硬规则

1. **思考模式默认开启，effort 默认 `high`**。传入的 `medium` 会映射为 `high`、`xhigh` 映射为 `high`、`ultra` 映射为 `max`；想省钱就显式写 `low` 或关闭思考。
2. **带 `tools` 的请求，后续每一轮都必须完整回传 `reasoning_content`**，否则返回 400。最简单的写法是把 `response.choices[0].message` 原样 append 回 messages。不带 tools 的普通多轮对话，`reasoning_content` 不需要回传，传了也会被忽略。

另外，思考模式下 `temperature`、`presence_penalty`、`frequency_penalty` 不生效（不报错）；`top_p` 只在思考模式下生效，取值范围 0.95–1.0。

| 报错 / 现象 | 原因 | 处理 |
| --- | --- | --- |
| 400（工具调用第二轮） | 没回传 `reasoning_content` | 整条 assistant 消息原样追加 |
| 账单比预期高 | 默认思考 + 高峰时段 | 降 effort、关思考或挪到空闲时段 |
| 401 | tryallapi Key 与 DeepSeek Key 混用 | 按 Base URL 对应 Key |
| 404 / 模型不存在 | 在 tryallapi 写了 `deepseek-flash` | 聚合用 `deepseek-v4.1-flash` |
| 改 temperature 没效果 | 思考模式忽略该参数 | 正常现象 |

---

## 六、DeepSeek V4.1 Flash FAQ

**Q1：DeepSeek V4.1 Flash 的模型名是什么？**  
官方 API 是 `deepseek-flash`；tryallapi.com 上是 `deepseek-v4.1-flash`。

**Q2：官方价格多少？**  
高峰时段每百万 tokens：缓存命中 ¥0.04、未命中 ¥2、输出 ¥8；空闲时段减半（¥0.02 / ¥1 / ¥4）。美元价为 $0.006 / $0.30 / $1.20（高峰）。

**Q3：高峰时段是什么时候？**  
北京时间周一至周五 9:00–12:00、14:00–18:00，不含法定节假日；其余时间都是空闲时段。

**Q4：上下文和最大输出？**  
上下文 1M tokens，最大输出 384K。

**Q5：deepseek-v4-pro 还能用吗？**  
官方说明 2026-09-14 12:00 之后、V4.1 Pro 上线之前，`deepseek-v4-pro` 的请求全部路由到 V4.1 Flash，并按 Flash 单价计费。

**Q6：怎么关闭思考模式？**  
OpenAI 格式传 `{"thinking": {"type": "disabled"}}`（OpenAI SDK 放在 `extra_body`）；Responses API 用 `reasoning.effort=none`。

**Q7：国内怎么经 tryallapi 调用？**  
`base_url=https://tryallapi.com/v1`，Key 用 `TRYALLAPI_KEY`，模型 `deepseek-v4.1-flash`；也支持 Anthropic 协议端点。

**Q8：tryallapi 怎么计费？**  
基价 $0.30 / $1.20（与官方美元高峰价一致）× 分组倍率；2026-10-05 可见 Self-Deployed-2（1）与 Self-Deployed-3（1.5），以控制台为准。

---

## 相关阅读

- 官方参考：[V4.1 Flash 发布文](https://www.deepseek.com/news/deepseek-v4-1-flash/) · [模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/) · [思考模式](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入大模型 API 的实践问题。*
*首发：2026-10-05｜最后更新：2026-10-05｜更新日志：2026-10-05 首版（价格与倍率取自 DeepSeek 官方文档与 tryallapi.com 公开接口，取数时间 2026-10-05，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
