# Gemini 3.1 Pro API 国内中转调用指南（2026年最新）

> 作者：MaynorAI｜首发：2026-10-01｜最后更新：2026-10-01
> 利益声明：作者运营 tryallapi.com。Google Gemini 参数来自 [ai.google.dev](https://ai.google.dev/) 模型页与价格页；tryallapi.com 取数 2026-10-01，最终以控制台为准。

**入口速查：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

面向需要 **多模态长上下文 + Agent 工具调用** 的国内开发者。

---

## 信息卡：gemini-3.1-pro-preview

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| 模型代码 | `gemini-3.1-pro-preview`（另有 `…-customtools`） | [模型页](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview) |
| 状态 | Preview（文档标注 Latest update：February 2026） | Google 模型页 |
| 上下文 / 最大输出 | 1,048,576 / 65,536 tokens | Google 模型页 |
| 模态 | 输入：文本/图像/视频/音频/PDF；输出：文本 | Google 模型页 |
| 能力摘要 | Thinking、Function calling、Search/Maps grounding、Caching、Batch/Flex/Priority | Google 模型页 |
| 官方标准价（≤200K） | 输入 $2.00；输出 $12.00（含 thinking tokens）；缓存 $0.20 | [Pricing](https://ai.google.dev/gemini-api/docs/pricing) 2026-10-01 |
| 官方标准价（>200K） | 输入 $4.00；输出 $18.00；缓存 $0.40；存储约 $4.50/百万 tokens/小时 | 同上 |
| tryallapi.com | **已上架**；端点 `gemini` + `openai` | `/api/pricing` |
| Base URL | `https://tryallapi.com/v1` | tryallapi.com |

**三行结论**

1. Google Gemini API 在中国大陆通常无法稳定直连；支付与地区策略也让个人账号成本高。
2. 3.1 Pro Preview 标准档 ≤200K 为 **$2 / $12**，超过 200K 升到 **$4 / $18**——长视频/PDF 分析前先算阶梯。
3. tryallapi.com 可用 OpenAI 兼容 SDK 调 `gemini-3.1-pro-preview`，创建令牌时选 Gemini 分组，扣费 ≈ 官方价 × 分组倍率。

👉 [前往 tryallapi.com](https://tryallapi.com/)

---

## 一、3.1 Pro Preview 适合什么任务？

Google 文档把它放在「第三代 Pro」：多模态理解、Agent 精确用工具、偏工程与 vibe-coding。和 Flash 系列比：更贵、上下文同样到约 1M，但输出上限 65K，适合深推理而不是海量廉价吞吐。

另有 `gemini-3.1-pro-preview-customtools`：官方说明更偏向 bash + 自定义工具的 Agent；不含这类工具的场景可能波动，按文档选型。

Preview 意味着行为与额度可能变，生产环境要有模型切换预案（例如回退到已稳定的 2.5 Pro，见相关阅读）。

---

## 二、三种国内可达方案

| 方案 | 说明 | 优点 | 代价 |
| --- | --- | --- | --- |
| Google AI Studio / Gemini API | 官方 Developer API | 一手模型、文档全 | 地区与支付门槛 |
| Vertex AI | GCP 企业通道 | 合规、配额可控 | 开通与账单复杂 |
| 聚合（tryallapi.com） | OpenAI / Gemini 兼容入口 | 国内网、统一 Key、支付宝微信 | 经第三方 |

多数个人项目从聚合起步；有 GCP 合同的公司再评估 Vertex。

---

## 三、快速接入

```bash
export TRYALLAPI_KEY="sk-xxxxxxxx"
```

**Python（OpenAI 兼容，改两行）**

```python
# pip install -U openai
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["TRYALLAPI_KEY"], base_url="https://tryallapi.com/v1", timeout=180)
r = client.chat.completions.create(
    model="gemini-3.1-pro-preview",
    messages=[{"role": "user", "content": "根据附件 PDF 大纲写风险清单（此处先测纯文本）"}],
)
print(r.choices[0].message.content)
```

**Node.js**

```javascript
import OpenAI from "openai";
const client = new OpenAI({ apiKey: process.env.TRYALLAPI_KEY, baseURL: "https://tryallapi.com/v1" });
const r = await client.chat.completions.create({
  model: "gemini-3.1-pro-preview",
  messages: [{ role: "user", content: "把这段日志归类成 incident 时间线" }],
});
console.log(r.choices[0].message.content);
```

**cURL**

```bash
curl https://tryallapi.com/v1/chat/completions \
  -H "Authorization: Bearer $TRYALLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3.1-pro-preview","messages":[{"role":"user","content":"ping"}]}'
```

原生 Gemini 路径（若走 `generativelanguage` 风格）以 tryallapi 文档为准；多数业务用 OpenAI 兼容即可。

**Cursor / Dify**：Base URL `https://tryallapi.com/v1`，模型名填完整 `gemini-3.1-pro-preview`（不要省略 `-preview`，除非广场另有别名）。

---

## 四、价格对比

### 官方（Standard Paid，2026-10-01 自 [价格页](https://ai.google.dev/gemini-api/docs/pricing) 核对）

| | ≤200K | >200K |
| --- | --- | --- |
| 输入 | $2.00 | $4.00 |
| 输出（含 thinking） | $12.00 | $18.00 |
| 上下文缓存 | $0.20 | $0.40 |

Batch / Flex 约为标准一半；Priority 更高——以官方页为准。Grounding with Google Search 另有免费额与按次计费。

### tryallapi.com 分组（≈ 官方 × 倍率；model_ratio=1, completion_ratio=6）

| 分组 | 倍率 | ≤200K 输入估算 | ≤200K 输出估算 |
| --- | --- | --- | --- |
| Anti-Gemini-1 | 0.14706 | ≈ $0.29 | ≈ $1.76 |
| Cli-Gemini-1 | 0.14706 | ≈ $0.29 | ≈ $1.76 |
| Aistudio-Gemini-1 | 0.35294 | ≈ $0.71 | ≈ $4.24 |
| Vertex-Gemini-1 | 0.4 | $0.80 | $4.80 |
| Aistudio-Gemini-2 | 0.52942 | ≈ $1.06 | ≈ $6.35 |
| Aistudio-Gemini-3 | 0.88236 | ≈ $1.76 | ≈ $10.59 |
| Vertex-Gemini-2 | 0.9 | $1.80 | $10.80 |
| Vertex-Gemini-3 | 1.8 | $3.60 | $21.60 |
| Aistudio-Gemini-4 | 1.91178 | ≈ $3.82 | ≈ $22.94 |

**以控制台为准。** 超过 200K 时按官方阶梯先算官方价，再乘倍率。

示例（公式）：日 500 次 × 输入 3k / 输出 1k → 月输入 4,500 万、输出 1,500 万；官方 ≤200K 约 45×$2 + 15×$12 = **$270**；倍率 r 时约 **$270×r**。

---


---

## 四·附、多模态与长上下文的计费提醒

Gemini 3.1 Pro Preview 吃图像、视频、音频和 PDF。对中转站来说，常见坑是：

1. **本地以为「一张图」，上游按许多 image tokens 计。** 先看响应里的 `usage`，再和官方 tokenizer / 文档对照。
2. **视频按帧或按时长折算 tokens**（以 Google 当期文档为准），很容易不知不觉跨过 200K 阶梯。
3. **PDF 常按文档/图像模态计价**，不要按「纯文字页数」估算。
4. **Grounding（Search / Maps）** 可能在 token 费之外另计请求费；关掉 grounding 做基线对比，再决定是否打开。

建议在试生产前写一份「模态 × 预估 tokens × 是否 >200K × 分组倍率」的表格，发给团队，避免月底才发现账单翻倍。

---

## 五·附、AI Studio、Vertex 与聚合的分工

- **AI Studio**：适合探索与小流量；免费档有限额，且内容可能用于改进产品（以官方条款为准）。
- **Vertex**：企业配额、VPC、数据区域；工程成本高，但合规路径清晰。
- **tryallapi.com**：把多模型收成一个 Key，适合国内个人与中小团队的原型与中等流量。若日后要过等保或客户审计，再把核心流量迁回 Vertex / 官方。

不要在同一条业务链路上无文档地混用三条通道，否则出错时很难判断是模型问题还是线路问题。


## 五、自测与真伪核对（方法）

- 上传或粘贴接近 20 万+ tokens 的材料，观察是否触发 >200K 计价；
- 对照 `usage` 与控制台流水；
- 多模态请求（图/PDF）单独测失败率；
- 本文不提供编造的延迟表。

---


---

## 工程侧最小验证脚本思路

用同一条提示词，连续请求 20 次：记录 HTTP 状态、是否流式完整、`model` 回显、输入输出 tokens、控制台扣费。若中途换分组，只改令牌分组、不改代码。发现 404 时优先检查模型字符串是否少了 `-preview`；发现偏贵时优先检查是否误开 grounding 或是否跨过 200K。把结果存进表格，而不是截一张「很快」的聊天窗口当证据。

## 六、报错速查

| 报错 | 处理 |
| --- | --- |
| 401 | 检查 Bearer 与令牌状态 |
| 403 | 换包含该模型的 Gemini 分组 |
| 404 | 模型名必须含 `-preview`；base_url 带 `/v1` |
| 429 | 退避、降并发、换分组 |
| 超时 | 长视频/深 thinking 提高 timeout，开流式 |
| 余额不足 | 充值或令牌额度上限 |

---

## 七、避坑

1. Preview 可能改价改行为，关键路径留备用模型。
2. 算清 200K 阶梯，否则「以为 $2/$12」实际按 $4/$18。
3. Grounding / 搜索工具可能单独计费。
4. 低倍率分组上游不同，先小额看稳定性。
5. 敏感影像与合同扫描谨慎过第三方。

---


---

## 和「只写聊天机器人」不一样的预算观

Gemini 3.1 Pro Preview 的账单结构，和纯文本闲聊很不一样。多模态输入、thinking tokens、200K 阶梯、可选的 Search grounding，任意一项被忽略，月度预算都可能偏一截。建议在立项时按「最坏情况」估：所有请求都按 >200K 标准档、开启 grounding、输出接近上限，再乘你打算使用的最高分组倍率，得到天花板；日常监控则看 P50 实际 tokens。tryallapi.com 的价值在于用国内可达的 OpenAI 兼容接口快速试错，并用同一套账单看 GPT / Claude / Gemini 的占比。等某一模型的调用量稳定后，再决定是否把该部分迁到 Vertex 做长期合约。Preview 模型尤其不要写死在不可热更新的客户端里——把 model 字符串放到配置中心，才能在 Google 调整预览策略时迅速切换。


## 八、FAQ

**Q1：模型 ID？**  
`gemini-3.1-pro-preview`；自定义工具场景可看 `gemini-3.1-pro-preview-customtools`。

**Q2：官方价？**  
≤200K：$2 入 / $12 出；>200K：$4 / $18。缓存 $0.20 / $0.40。以 Google 价格页为准。

**Q3：国内直连？**  
通常不行或不稳定；用 Vertex 或聚合。

**Q4：和 Gemini 2.5 Pro？**  
2.5 Pro 标准档更低（≤200K 约 $1.25/$10）；3.1 Pro 为新一代 Preview，能力与价格不同，按需求选。

**Q5：tryallapi 计费？**  
官方价 × 分组倍率；2026-10-01 倍率约 0.15～1.91。

**Q6：能否用 OpenAI SDK？**  
可以，`base_url=https://tryallapi.com/v1`。

**Q7：支付与发票？**  
微信/支付宝/信用卡等以站点为准；发票见公告。

**Q8：一个 Key 多模型？**  
可以，建议分项目限额。

---


---

## 写在接入之后

完成第一次成功响应只是起点。建议你继续做两件事：把 `TRYALLAPI_KEY` 放进密钥管理（不要写进仓库）；为关键路径准备第二个模型作降级。中转站解决的是网络与支付，解决不了提示词质量、评测缺失与密钥泄露。定期打开 tryallapi.com 控制台核对分组倍率是否变动，并回到厂商官方价格页复核——本文数字快照于 2026-10-01，之后一切以页面为准。若你的流量上升到需要合同、发票抬头与专线，再评估直连官方云或企业方案，而不是无限叠加低倍率分组。


---

## 常见架构：网关里的模型路由

很多团队会在自己的 API 网关里写一条规则：默认 `gemini-3.1-pro-preview`，失败则回退 `gemini-2.5-pro`，再失败则回退某款 Flash。配合 tryallapi.com 时，回退只改 `model` 字段，不必换 Key。记得给每次回退打日志，否则线上「偶尔变笨」很难追查。配额方面，聚合平台的限流与 Google 官方限流是两层概念——你可能在平台侧 429，也可能透传上游 429，错误体要分别解析。对于 Dify、FastGPT 一类编排工具，把温度、最大输出、超时做成可配置项，避免把 Preview 模型的默认思考预算拉满导致长时间无首包。最后，定期导出消费 CSV，按模型与分组做透视，比只看余额数字更有利于砍掉浪费。


## 相关阅读

- [Gemini 2.5 Pro API 国内中转调用指南](/gemini-2.5-pro-api/)
- [GPT-6.1 Sol API 国内中转调用指南](/gpt-6.1-sol-api/)
- [GPT-6 Astra API 国内中转调用指南](/gpt-6-astra-api/)
- [Claude Opus 5.5 API 国内中转调用指南](/claude-opus-5-5-api/)
- [Gemini 3.1 Pro API 国内中转调用指南](/gemini-3.1-pro-api/)
- [DeepSeek V3.2 API 国内中转调用指南](/deepseek-v3.2-api/)
- [Grok 4.7 API 国内中转调用指南](/grok-4.7-api/)
- [tryallapi.com 模型价格总览](https://tryallapi.com/pricing)

- 官方参考：[Gemini 3.1 Pro Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview) · [Pricing](https://ai.google.dev/gemini-api/docs/pricing)

---

**其他使用方式，按需选择：**

| 渠道类型 | 访问网址 | 适用场景 |
| --- | --- | --- |
| 全模型 API 聚合站 | https://tryallapi.com/ | 适合开发者调用、低延迟直连、多模型一站式接入 |

---

*作者：MaynorAI，tryallapi.com 运营者，关注国内开发者接入海外大模型的实践问题。*
*首发：2026-10-01｜最后更新：2026-10-01｜更新日志：2026-10-01 首版（价格与倍率取自官方文档与 tryallapi.com 公开接口，取数时间 2026-10-01，最终以控制台为准）。*
*免责声明：文中价格、倍率与政策可能随厂商及平台调整而变化，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。*
