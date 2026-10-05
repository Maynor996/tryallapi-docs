# MiMo V2.6 Pro API 国内中转调用指南：价格、教程与代码（2026）

> 作者：MaynorAI｜首发：2026-10-05｜最后更新：2026-10-05
> 利益声明：作者运营 tryallapi.com。MiMo-V2.6-Pro 的参数与价格来自小米 MiMo 官方发布页、模型页与定价文档；tryallapi.com 数据取自公开接口 `/api/pricing`，取数时间 2026-10-05（北京时间），最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

小米在 2026-09-22 发布并开源 MiMo-V2.6 系列（Pro 与 Flash 两个原生全模态模型）。**MiMo-V2.6-Pro** 是旗舰：万亿参数级、1M 上下文、文本 / 图片 / 视频 / 音频输入，官方称在 Artificial Analysis 综合智能指数上拿到 46 分。它最大的卖点是价格：输入 ¥3、输出 ¥6，缓存命中只要 ¥0.025。

---

## MiMo-V2.6-Pro 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `mimo-v2.6-pro`（官方要求全小写） | [官方发布页](https://mimo.mi.com/docs/zh-CN/news/latest/v2-6) |
| 发布 | 2026-09-22，权重与技术报告开源 | 官方发布页 |
| 模态 | 输入：文本、图片、视频、音频；输出：文本 | [官方模型页](https://mimo.mi.com/models/en-US/mimo-v2.6-pro) |
| 上下文 / 最大输出 | 1M / 128K | 官方模型页 |
| 默认限额 | RPM 100，TPM 10M | 官方模型页 |
| 能力 | 深度思考、工具调用、流式、联网搜索、结构化输出、上下文缓存 | 官方模型页 |
| 国内价（每百万 tokens） | 缓存命中 ¥0.025；未命中 ¥3；输出 ¥6 | [官方定价](https://mimo.mi.com/static/docs/price/pay-as-you-go.md) |
| 海外价（每百万 tokens） | $0.0036 / $0.435 / $0.87 | 官方定价 |
| 缓存写入 | 限时免费 | 官方定价 |
| 官方 Base URL | `https://api.xiaomimimo.com/v1`（兼容 OpenAI 与 Anthropic 协议） | 官方模型页 |
| tryallapi.com | **已上架** `mimo-v2.6-pro`；端点 `openai` | `/api/pricing` 2026-10-05 |
| Base URL（聚合） | `https://tryallapi.com/v1` | tryallapi.com |

**三行结论**

1. 官方国内价 ¥3 / ¥6，Batch API 再打五折（¥1.5 / ¥3）；缓存命中 ¥0.025，是未命中价的 1/120。
2. 需要极低延迟时有 `mimo-v2.6-pro-ultraspeed`（官方称最高 20 倍推理速度），但单价是标准版的 10 倍，且不支持 Batch。
3. tryallapi.com 标定基价等于官方美元价（$0.435 / $0.87），实际 ≈ 基价 × 分组倍率（1～2.2），以控制台为准。

👉 [前往 tryallapi.com 注册并生成 API Key](https://tryallapi.com/)

---

## 一、MiMo-V2.6-Pro 的三种计费形态怎么选

小米把同一个模型拆成三种调用方式，价格差距是数量级的：

| 调用方式 | 模型名 | 缓存命中 | 未命中输入 | 输出 | 适合 |
| --- | --- | --- | --- | --- | --- |
| 实时 API | `mimo-v2.6-pro` | ¥0.025 | ¥3.00 | ¥6.00 | 在线对话、Agent |
| Batch API | `mimo-v2.6-pro` | ¥0.0125 | ¥1.50 | ¥3.00 | 离线批处理、评测、数据生成 |
| UltraSpeed | `mimo-v2.6-pro-ultraspeed` | ¥0.25 | ¥30.00 | ¥60.00 | 强实时交互、对响应速度极敏感 |

经验法则：

- **能异步就走 Batch**：同一个模型，价格直接减半；
- **UltraSpeed 只给真正卡延迟的环节**（比如语音助手的首轮回复），其余步骤仍用标准版；
- **把缓存当成第一优先级**：命中价与未命中价相差 120 倍，长 system prompt、工具定义、固定知识库前缀都应保持稳定，让请求尽量命中缓存。

另外注意：官方定价页写明，按量付费使用开放平台的普通 API Key、按实际 Token 扣账户余额，**与 Token Plan 套餐额度不互通**，别把两套配置混在一起。

---

## 二、迁移提醒：MiMo-V2.5 系列 10 月 21 日下线

官方定价页写明：`mimo-v2.5-pro` 与 `mimo-v2.5` 将于 **北京时间 2026-10-21 10:00 正式下线**，目前 `mimo-v2.5-pro` 与 `mimo-v2.6-pro` 同价（¥3 / ¥6）。也就是说，升级到 V2.6-Pro 不涨价，但不升级会在三周后直接失效。

迁移清单：

1. 把配置里的 `mimo-v2.5-pro` 改为 `mimo-v2.6-pro`，`mimo-v2.5` 改为 `mimo-v2.6-flash`（官方定价页把二者列为同价对应关系）；
2. 模型名一律小写，官方特别注明调用时使用 `mimo-v2.6-pro`、`mimo-v2.6-flash`、`mimo-v2.6-pro-ultraspeed`；
3. V2.6 新增原生音频、视频理解，如果原来在外面单独做 ASR 再喂文本，可以评估直接多模态输入；
4. 跑一轮回归：官方称 V2.6 在长程软件工程基准 DeepSWE v1.1 上，Pro 从 58.4 提升到 72.6，行为变化不小，提示词可能需要微调。

---

## 三、MiMo-V2.6-Pro API 价格：官方 vs tryallapi.com

### 官方价（2026-10-05 核对）

| 计费项（每百万 tokens） | 国内（¥） | 海外（$） |
| --- | --- | --- |
| 输入（缓存命中） | 0.025 | 0.0036 |
| 输入（缓存未命中） | 3.00 | 0.435 |
| 输出 | 6.00 | 0.87 |
| Batch：命中 / 未命中 / 输出 | 0.0125 / 1.50 / 3.00 | 0.0018 / 0.2175 / 0.435 |

联网搜索插件单独按次计费（国内 ¥16 / 千次），不含在 token 价里。

### tryallapi.com 分组估算（≈ 基价 × 分组倍率）

`mimo-v2.6-pro`：`model_ratio=0.2175`、`completion_ratio=2`、`cache_ratio=0.0083`，换算基价为输入 $0.435、输出 $0.87、缓存读约 $0.0036。2026-10-05 可见分组：

| 分组 | 倍率 | 输入估算 | 输出估算 |
| --- | --- | --- | --- |
| Self-Deployed-2 | 1 | $0.435 | $0.87 |
| Self-Deployed-3 / Xiaomi-1 | 1.5 | ≈ $0.65 | ≈ $1.31 |
| Xiaomi-2 | 2.2 | ≈ $0.96 | ≈ $1.91 |

表中金额是 tryallapi 的美元额度；`/api/status` 显示充值价 `price=1`（元 / 美元额度），实际以充值页为准。**以控制台为准。**

---

## 四、MiMo-V2.6-Pro 国内调用方法：快速接入

### 1. 环境变量

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

### 2. Python（经 tryallapi，OpenAI 兼容）

```python
# pip install -U openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1")
r = client.chat.completions.create(
    model="mimo-v2.6-pro",
    messages=[{"role": "user", "content": "根据这份接口文档生成 pytest 用例"}],
    max_completion_tokens=4096,
)
print(r.choices[0].message.content)
```

### 3. 关闭深度思考（官方示例写法）

小米官方模型页的示例用 `extra_body` 关闭思考，适合简单问答、分类等不需要长推理的请求：

```python
r = client.chat.completions.create(
    model="mimo-v2.6-pro",
    messages=[{"role": "user", "content": "把下面 20 条评论按情绪分类"}],
    extra_body={"thinking": {"type": "disabled"}},
)
```

经聚合调用时，先用一条短请求确认该参数是否生效（看返回的 usage 是否还有大量推理 tokens）。

### 4. 对照：官方直连

```python
client = OpenAI(api_key=os.environ["MIMO_API_KEY"], base_url="https://api.xiaomimimo.com/v1")
```

### 5. cURL（聚合）

```bash
curl https://tryallapi.com/v1/chat/completions \
  -H "Authorization: Bearer $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.6-pro","messages":[{"role":"user","content":"ping"}]}'
```

---

## 五、常见报错与排查

| 报错 / 现象 | 原因 | 处理 |
| --- | --- | --- |
| 模型不存在 | 写成 `MiMo-V2.6-Pro` 等大小写混合形式 | 改为全小写 `mimo-v2.6-pro` |
| 10 月 21 日后突然报错 | 仍在调用 `mimo-v2.5-pro` / `mimo-v2.5` | 迁移到 V2.6 |
| 429 | 超出 RPM 100 / TPM 10M 的默认限额 | 退避重试、降并发，或改走 Batch |
| 401 | 按量 Key、Token Plan Key、tryallapi Key 混用 | 一个环境只配一套 Key 和 Base URL |
| 账单偏高 | 简单任务也开着深度思考 | 简单任务关闭思考，复杂任务再开 |
| 首字慢 | 长上下文 + 深度思考 | 精简上下文、利用缓存，或评估 UltraSpeed |

---

## 六、MiMo-V2.6-Pro FAQ

**Q1：MiMo-V2.6-Pro 的模型 ID 是什么？**  
`mimo-v2.6-pro`，官方要求全小写；tryallapi.com 上同名。

**Q2：官方价格多少？**  
国内每百万 tokens：缓存命中 ¥0.025、未命中 ¥3、输出 ¥6；海外 $0.0036 / $0.435 / $0.87。缓存写入限时免费。

**Q3：Batch API 便宜多少？**  
Batch 价格是实时 API 的一半：¥0.0125 / ¥1.5 / ¥3。

**Q4：上下文和最大输出？**  
上下文 1M tokens，最大输出 128K。

**Q5：UltraSpeed 是什么？**  
`mimo-v2.6-pro-ultraspeed`，官方称推理速度最高 20 倍，国内价 ¥0.25 / ¥30 / ¥60，不支持 Batch。

**Q6：MiMo-V2.5-Pro 还能用多久？**  
官方公告 `mimo-v2.5-pro` 与 `mimo-v2.5` 于北京时间 2026-10-21 10:00 下线，建议尽快迁移到 V2.6。

**Q7：国内怎么经 tryallapi 调用？**  
`base_url=https://tryallapi.com/v1`，Key 用 `TRYALLAPI_KEY`，模型 `mimo-v2.6-pro`，OpenAI 兼容格式。

**Q8：tryallapi 怎么计费？**  
基价 $0.435 / $0.87（与官方海外价一致）× 分组倍率；2026-10-05 可见 1、1.5、2.2 三档，以控制台为准。

---

## 相关阅读

- 官方参考：[MiMo-V2.6 发布](https://mimo.mi.com/docs/zh-CN/news/latest/v2-6) · [MiMo-V2.6-Pro 模型页](https://mimo.mi.com/models/en-US/mimo-v2.6-pro) · [按量计费价格](https://mimo.mi.com/static/docs/price/pay-as-you-go.md)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入大模型 API 的实践问题。*
*首发：2026-10-05｜最后更新：2026-10-05｜更新日志：2026-10-05 首版（价格与倍率取自小米 MiMo 官方文档与 tryallapi.com 公开接口，取数时间 2026-10-05，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
