# Gemini 2.5 Pro API 国内中转调用指南（2026年最新）

> 作者：MaynorAI｜首发：2026-09-30｜最后更新：2026-10-02
> 利益声明：作者运营 tryallapi.com。文中官方数据都附了来源链接，tryallapi.com 的数据取自站点公开的价格接口，建议你以控制台显示为准。

**先选对入口：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

本文讲的是**开发者用 API 调用** Gemini 2.5 Pro，对应表里的「全模型 API 聚合站」。

---

## Gemini 2.5 Pro 信息卡

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型 ID | `gemini-2.5-pro`（稳定版） | Google 官方模型页 |
| 输入上限 / 输出上限 | 1,048,576 / 65,536 tokens | Google 官方模型页 |
| 输入类型 | 文本、图片、视频、音频、PDF（输出为文本） | Google 官方模型页 |
| 知识截止 | 2025 年 1 月 | Google 官方模型页 |
| 稳定版发布 | 2025-06-17 | Google 官方 changelog / 弃用页 |
| 官方价格（标准，每百万 tokens） | 输入 $1.25（≤200K）/ $2.50（>200K）；输出 $10.00（≤200K）/ $15.00（>200K），输出价含思考 tokens | Google 官方价格页 |
| tryallapi.com 支持的协议 | OpenAI 兼容（`/v1/chat/completions`）、Gemini 原生（`/v1beta/models/{model}:generateContent`） | tryallapi.com 公开价格接口 |
| tryallapi.com Base URL | `https://tryallapi.com/v1`（OpenAI 兼容） | tryallapi.com 站点配置 |
| 核验日期 | 2026-09-30（tryallapi.com 倍率 2026-10-02 复核） | — |

**三句话结论**

1. Google 公布的 Gemini API 可用地区列表里没有中国大陆，国内直接调 `generativelanguage.googleapis.com` 并不现实。
2. 最省事的方式是用兼容 OpenAI 协议的聚合平台：代码里只改 `base_url` 和 `api_key`，模型名写 `gemini-2.5-pro`。
3. tryallapi.com 给 Gemini 2.5 Pro 设置了多个计费分组，价格按「官方价 × 分组倍率」计算。建议先小额充值，在自己的业务上测过再决定用哪个分组。

👉 [注册 tryallapi.com，创建 API Key](https://tryallapi.com/)

---

## 一、为什么国内调用 Gemini API 需要中转？

### 1. 网络与地区限制
Google 维护着一份 Gemini API「可用地区」列表，中国大陆和香港都不在里面（[来源](https://ai.google.dev/gemini-api/docs/available-regions)）。所以国内服务器直连官方接口，经常超时或者直接被拒。

### 2. 支付与账号门槛
官方付费需要绑定 Google Cloud 结算账号，一般要用境外银行卡。对个人开发者和小团队来说，光这一步就会卡住不少人。

### 3. 2026 年多了一个新情况：新用户可能拿不到 2.5 Pro
Google 在模型弃用页里说明：为保证容量，**2.5 系列模型只开放给过去实际用过的用户**。这些模型没有被弃用，会继续提供服务，但新项目会被引导去用更新的模型（[来源](https://ai.google.dev/gemini-api/docs/deprecations)）。也就是说，你手上已有的提示词、评测基线或业务流程如果是按 2.5 Pro 调好的，新开的官方账号未必能直接调用。

### 4. 中转 / 聚合平台做了什么
可以简单理解为：**你的代码 → 聚合平台 → 上游模型服务**。平台对外提供和 OpenAI 或 Gemini 一致的接口，替你解决网络、支付和多模型统一计费的问题。代价是你多依赖了一个服务商，所以后面「避坑」一节很重要。

---

## 二、3 种接入方案对比

| 维度 | Google AI Studio（官方 API） | Vertex AI（Google Cloud） | 聚合平台（如 tryallapi.com） |
| --- | --- | --- | --- |
| 国内可达性 | 官方可用地区不含中国大陆 | 需要 GCP 账号，网络条件同样受限 | 平台提供国内可访问的入口 |
| 支付方式 | Google 结算账号（境外卡） | GCP 结算账号 | tryallapi.com 支持微信支付、支付宝、信用卡 |
| 接入难度 | 低（有官方 SDK） | 中（项目、IAM、区域配置） | 低（改 `base_url` 即可） |
| 协议 | Gemini 原生；官方也提供 OpenAI 兼容端点 | Vertex SDK / REST | OpenAI 兼容 + Gemini 原生 |
| 模型范围 | Google 模型 | Google 及 Model Garden | 多家模型一个 Key |
| 2.5 Pro 新用户可用性 | 受限（见上文） | 以 Google Cloud 控制台与文档为准 | 以平台模型列表为准（tryallapi.com 目前可用） |
| 发票 / 合规 | Google 账单 | GCP 账单 | tryallapi.com：对公转账后开票；国际发票可在网站自助开具（据站点公告） |
| 适合谁 | 海外团队、有稳定海外网络的开发者 | 企业、需要 SLA 和合规的团队 | 国内个人开发者、小团队、多模型用户 |

说句公道话：如果你所在的公司有海外实体，也要求严格的数据合规，那么官方或 Vertex 仍然是首选。聚合平台最适合的是**快速验证、多模型切换，以及国内部署的中小项目**。

---

## 三、5 分钟接入：改 base_url 就能跑

### 第 1 步：注册并创建令牌
1. 打开 [tryallapi.com](https://tryallapi.com/) 注册、登录。
2. 充值（最低充值额以充值页为准），新用户可以先领试用额度（据站点公告）。
3. 进入「令牌」页面生成 API Key。**创建时选好分组**，分组决定上游渠道和价格，详见第四节。

### 第 2 步：Python（OpenAI SDK）

```python
# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key="sk-你的tryallapi.com令牌",
    base_url="https://tryallapi.com/v1",   # 唯一需要改的地方
)

resp = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "system", "content": "你是一名资深 Python 工程师。"},
        {"role": "user", "content": "用 Python 实现 LRU 缓存，并解释时间复杂度。"},
    ],
    stream=True,
)
for chunk in resp:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 第 3 步：Node.js

```javascript
// npm i openai
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.TRYALLAPI_KEY,
  baseURL: "https://tryallapi.com/v1",
});

const res = await client.chat.completions.create({
  model: "gemini-2.5-pro",
  messages: [{ role: "user", content: "总结这段需求文档的三个风险点：..." }],
});
console.log(res.choices[0].message.content);
```

### 第 4 步：cURL

```bash
curl https://tryallapi.com/v1/chat/completions \
  -H "Authorization: Bearer $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "你好，简单介绍一下你自己"}]
  }'
```

### 可选：Gemini 原生协议
tryallapi.com 的公开接口显示，`gemini-2.5-pro` 同时支持 Gemini 原生端点，路径是 `/v1beta/models/{model}:generateContent`。如果你已经在用 Google 官方 SDK，并且依赖原生字段（比如 `thinkingConfig`），可以改走原生端点（鉴权方式以 [tryallapi.com 接口文档](https://5oq7d57fbk.apifox.cn) 为准）：

```bash
curl "https://tryallapi.com/v1beta/models/gemini-2.5-pro:generateContent" \
  -H "x-goog-api-key: $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"你好"}]}]}'
```

> 思考模式小贴士：站点对 Google 模型的说明是，部分模型可以在模型名后加 `-thinking` / `-nothinking`，或者用 `-thinking-*` 自定义思考预算（156–24576）；具体某个模型支持哪些后缀，以控制台模型广场为准。

### 在常用工具里使用

- **Cursor**：Settings → Models，打开 OpenAI API Key 并填入 tryallapi.com 令牌；打开「Override OpenAI Base URL」，填 `https://tryallapi.com/v1`；添加自定义模型 `gemini-2.5-pro`。（Cursor 的菜单名称会随版本变化，以实际界面为准。）
- **Dify**：设置 → 模型供应商 → 选「OpenAI-API-compatible」，API endpoint 填 `https://tryallapi.com/v1`，模型名填 `gemini-2.5-pro`，上下文长度按官方 1,048,576 填或者按需调小。
- **Claude Code**：Claude Code 走的是 Anthropic 协议。tryallapi.com 提供 `/v1/messages` 端点，用 Claude 模型时，在 `~/.claude/settings.json` 里设置 `"ANTHROPIC_BASE_URL": "https://tryallapi.com"` 和 `"ANTHROPIC_AUTH_TOKEN": "sk-你的令牌"`。本文不建议在 Claude Code 里调用 Gemini 2.5 Pro：`gemini-2.5-pro` 在 tryallapi.com 公开接口里列出的端点只有 OpenAI 兼容和 Gemini 原生两种。
- **Cherry Studio / Lobe Chat 等客户端**：新增一个「OpenAI 兼容」服务商，地址填 `https://tryallapi.com`（部分客户端要求填到 `/v1`），模型填 `gemini-2.5-pro`。
- 客户端提示模型不兼容时：站点说明可以在模型名前加 `new-` 前缀来解决部分客户端的兼容问题。

完整文档：[tryallapi.com 接口文档](https://5oq7d57fbk.apifox.cn)

---

## 四、价格：官方 vs tryallapi.com

### 1. 官方价格（Google AI Studio 标准档，每百万 tokens，美元）

| 计费项 | ≤200K 上下文 | >200K 上下文 |
| --- | --- | --- |
| 输入 | $1.25 | $2.50 |
| 输出（含思考 tokens） | $10.00 | $15.00 |
| 上下文缓存 | $0.125 | $0.25（另有存储费 $4.50 / 百万 tokens / 小时） |

来源：[Gemini API 价格页](https://ai.google.dev/gemini-api/docs/pricing)（页面显示最后更新于 2026-09-24 UTC）。官方另有 Batch / Flex 档，≤200K 时输入 $0.625、输出 $5.00，适合离线任务。

### 2. tryallapi.com 怎么计费
tryallapi.com 基于倍率计费，公式是：

**实际消耗（美元额度）= 官方价 × 分组倍率**

站点价格接口里，`gemini-2.5-pro` 的基础倍率换算后正好对应官方的 $1.25 / $10（输入 / 输出），超过 200K 上下文时同样按官方的阶梯加价。不同分组的倍率如下，美元额度是按公式推算的：

| 分组（创建令牌时选） | 分组倍率 | 输入（≤200K）美元额度 / 百万 tokens | 输出（≤200K）美元额度 / 百万 tokens |
| --- | --- | --- | --- |
| Anti-Gemini-1 | 0.14706 | ≈ $0.18 | ≈ $1.47 |
| Cli-Gemini-1 | 0.14706 | ≈ $0.18 | ≈ $1.47 |
| Vertex-Gemini-1 | 0.4 | $0.50 | $4.00 |
| Aistudio-Gemini-2 | 0.52942 | ≈ $0.66 | ≈ $5.29 |
| Aistudio-Gemini-3 | 0.88236 | ≈ $1.10 | ≈ $8.82 |
| Vertex-Gemini-2 | 0.9 | ≈ $1.13 | $9.00 |
| Vertex-Gemini-3 | 1.8 | $2.25 | $18.00 |
| Aistudio-Gemini-4 | 1.91178 | ≈ $2.39 | ≈ $19.12 |

- 数据来自 `tryallapi.com/api/pricing`，取于 2026-09-30，2026-10-02 复核未变。倍率可能调整，**以控制台模型广场显示为准**。
- **充值换算**：站点公告写的是「统一使用美元（USD）展示余额和消费，充值按 1:1 对应美元」；人民币支付时的实际金额以充值页显示为准。
- **批量充值折扣**（站点配置）：满 $10 享 0.99 折扣系数，满 $100 为 0.98，满 $1000 为 0.96，更高档位见充值页。
- **分组名代表上游渠道**：名称里带 Vertex、Aistudio、Cli、Anti 的，上游来源不同，价格和稳定性也不同。建议先用小额在两三个分组上跑同一组请求，再决定生产用哪个。

### 3. 成本估算示例（按公式推算，非实测）
假设每天 1,000 次请求，每次输入 2,000 tokens、输出 800 tokens，一个月按 30 天：
- 月输入 6,000 万 tokens，月输出 2,400 万 tokens；
- 官方标准档：60 × $1.25 + 24 × $10 = **$315**；
- 在 tryallapi.com 用倍率 r 的分组：约 **$315 × r**（美元额度），再按充值比例换算成人民币。

---

## 五、上线前怎么自测 Gemini 2.5 Pro 中转

本文不公布延迟或成功率数字（没有可复现的实测数据之前不写数字）。建议你在自己的网络环境里按下面的方法测一遍：

- 请求设置：模型 `gemini-2.5-pro`，同一组提示词（短问答 + 长上下文 + 代码），`stream=true`
- 样本量：每个分组不少于 200 次，最好跨 24 小时
- 指标：首 token 延迟 P50 / P95、HTTP 成功率、流式中断率、`usage` 与控制台扣费是否一致

**怎么自己验证「是不是真的 2.5 Pro」**
1. 看响应里 `usage` 的 token 数，和本地 tokenizer 估算的差距是否合理；
2. 发一段 30 万 token 以上的长文，检查能否正常处理（2.5 Pro 支持约 100 万 token 输入），同时核对是否按 >200K 阶梯计费；
3. 用同一组有标准答案的推理题，跟官方对照组比较正确率；
4. 在控制台日志里核对每次请求的扣费明细。

---

## 六、常见报错与排查

| 报错 | 常见原因 | 处理方法 |
| --- | --- | --- |
| **401 Unauthorized** / Token not provided | 没带 Key、Key 前后多了空格、`Authorization` 头写错 | 用 `Authorization: Bearer sk-...`；在控制台确认令牌状态和余额 |
| **403** | 令牌分组没有这个模型的权限，或令牌设置了 IP 白名单或模型限制 | 编辑令牌，换一个包含 `gemini-2.5-pro` 的分组 |
| **404 / model not found** | 模型名写错（比如 `gemini-2.5-pro-latest`），或 `base_url` 少了 `/v1`，或多了一层 `/v1` | OpenAI SDK 的 base_url 写 `https://tryallapi.com/v1`；模型名以模型广场为准 |
| **429 Too Many Requests** | 上游限流或分组并发到顶 | 加指数退避重试（1s → 2s → 4s）；降低并发；换分组 |
| **超时 / 流式中断** | 长上下文加深度思考导致首字很慢；客户端默认超时太短 | 把 SDK `timeout` 调到 120 秒以上；用 `stream=true`；必要时调低思考预算 |
| 余额不足 | 额度用完 | 充值，或在令牌上设置额度上限，防止被刷 |

---

## 七、选 Gemini 中转站的 5 个避坑点

1. **算清「汇率 × 倍率」，别只看倍率。** 有的站倍率很低，但充值汇率很高，最终单价未必便宜。用上面的公式换算成「人民币 / 百万 tokens」再比较。
2. **问清上游渠道。** 同一个模型名，背后可能是官方 API、Vertex、CLI 或逆向渠道，稳定性和合规性差别很大。选分组前先看渠道说明。
3. **核对 >200K 阶梯和缓存计费。** 长上下文正是 2.5 Pro 的主要卖点，一定要确认超过 200K 时怎么计费、缓存命中怎么计费。
4. **小额起步、分散充值。** 先充小额，按第五节的方法跑一周，再决定要不要加量；不要把大额资金压在单一平台。
5. **别传敏感数据。** 请求内容会经过第三方平台。涉及个人信息或商业机密的业务，应先阅读平台的隐私政策和服务条款，必要时改用官方或企业渠道。

---

## 八、常见问题（FAQ）

**Q1：国内能直接调用 Gemini 2.5 Pro API 吗？**
Google 公布的 Gemini API 可用地区不包括中国大陆，直连通常不可行。国内开发者一般通过兼容 OpenAI 协议的聚合平台调用，只需修改 base_url 和 API Key。

**Q2：gemini-2.5-pro 和 preview 版本有什么区别？模型 ID 怎么写？**
`gemini-2.5-pro` 是 2025-06-17 发布的稳定版。早期的 `gemini-2.5-pro-preview-03-25`、`-05-06`、`-06-05` 等预览版已于 2025-12-02 下线，所以调用时写 `gemini-2.5-pro` 即可。

**Q3：Gemini 2.5 Pro 的官方价格是多少？**
标准档每百万 tokens：输入 $1.25（≤200K）/ $2.50（>200K），输出 $10.00（≤200K）/ $15.00（>200K），输出价格包含思考 tokens。以 Google 官方价格页为准。

**Q4：tryallapi.com 调用 Gemini 2.5 Pro 怎么收费？**
按「官方价 × 分组倍率」扣美元额度，不同分组倍率不同，从 0.14706 到 1.91178 不等（2026-10-02 复核）。具体以控制台模型广场显示为准。

**Q5：一个 Key 能同时调用 GPT、Claude 和 Gemini 吗？**
可以。tryallapi.com 是多模型聚合平台，同一个令牌在分组权限允许的范围内可以调用多家模型。建议按用途分别创建令牌，方便统计和限额。

**Q6：支持哪些支付方式？能开发票吗？**
站点支持微信支付、支付宝和信用卡。据站点公告，发票目前要对公转账后联系客服开具，国际发票可以在网站上自助开具。

**Q7：会不会「降智」或者掺水？怎么验证？**
先用小额，按本文第五节的自测方法验证：核对 usage 与扣费、测试长上下文、用有标准答案的题目跟官方对照组比较。

**Q8：为什么 Google 官方新账号可能调不了 2.5 Pro？**
Google 在弃用页中说明，2.5 系列模型只开放给过去实际用过的用户，新项目会被引导使用更新的模型。2.5 Pro 本身没有被弃用。

---

## 相关阅读

- [tryallapi.com 模型价格总览](https://tryallapi.com/pricing)
- 官方参考：[Gemini 2.5 Pro 模型页](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro) · [Gemini API 价格](https://ai.google.dev/gemini-api/docs/pricing) · [OpenAI 兼容说明](https://ai.google.dev/gemini-api/docs/openai)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，长期关注国内开发者接入海外大模型的问题。*
*首发：2026-09-30｜最后更新：2026-10-02｜更新日志：2026-09-30 首版；2026-10-02 复核 tryallapi.com 分组倍率，删除未完成的测速表与占位内容。*
*免责声明：本文价格、倍率和政策会随官方及平台调整而变化，请以 Google 官方页面和 tryallapi.com 控制台为准。第三方中转服务不是 Google 官方服务。*
