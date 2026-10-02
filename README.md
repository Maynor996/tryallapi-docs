# tryallapi-docs

AI 大模型 API 国内中转调用指南与价格汇总，线上地址：**https://docs.tryallapi.com**

每个模型一篇：官方价格与参数、官方 / 云厂商 / 聚合平台方案对比、在 [tryallapi.com](https://tryallapi.com/) 用 OpenAI 兼容接口接入的步骤、Python / Node.js / cURL 代码和常见报错。目前覆盖 OpenAI、Anthropic、Google、DeepSeek、xAI、Qwen、Moonshot 等厂商的模型。

## 目录

| 路径 | 说明 |
| --- | --- |
| `content/<slug>.md` | 文章正文（Markdown）。第一行 H1 会被统一标题替换；「最后更新：YYYY-MM-DD」决定 dateModified |
| `data/articles.json` | 每篇的元信息：slug、name、model_id、vendor、date_published、description（≤80 字，含「价格」「国内」）、summary（首页卡片） |
| `build.py` | 构建脚本：检查 → 生成 `site/`（文章页、首页、sitemap、robots、404、OG 图）→ 校验 |
| `ping.py` | 把有变化的 URL 提交到 IndexNow |
| `site/` | 构建产物，Cloudflare Pages 直接发布这个目录 |

## 构建

```bash
pip install -r requirements.txt   # markdown-it-py；OG 图需要 google-chrome / chromium，可选 Pillow 压缩
python3 build.py                  # 检查 + 构建 + 校验，任何一步失败都会非 0 退出
python3 build.py --check          # 只做发布前检查
python3 build.py --og             # 强制重新生成全部 OG 图
```

发布前检查会拦截：`待填` / `待核对` / `TODO` / 【待…】占位、标题缺「价格」或超过 32 字（汉字算 1，英文数字算 0.5）、描述超过 80 字或缺「价格」「国内」、正文多个 H1。

## 新增一篇文章

1. 把正文写到 `content/<slug>.md`（slug 形如 `gpt-5.4-api`）；
2. 在 `data/articles.json` 里加一条（vendor 只能是 OpenAI / Anthropic / Google / DeepSeek / xAI / Qwen / Moonshot）；
3. `python3 build.py`：所有页面的「相关阅读」、首页卡片、sitemap 会一起更新；
4. 提交并推送 `main`，Cloudflare Pages 自动部署；
5. 部署完成后 `python3 ping.py` 提交今天有变化的 URL。

站点域名只在 `build.py` 的 `SITE_URL` 一处定义（canonical、og:url、sitemap、JSON-LD 都用它）。
