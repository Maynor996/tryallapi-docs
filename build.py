#!/usr/bin/env python3
"""tryallapi-docs 静态站构建脚本。

输入：
  data/articles.json   每篇文章的元信息（slug / 名称 / 模型 ID / 厂商 / 首发日期 / 描述 / 卡片摘要）
  content/<slug>.md    文章正文（Markdown，第一行 H1 会被替换成统一标题）
  （可选）published.json  每日任务的发布记录，用来补全缺失的首发日期
输出：
  site/                Cloudflare Pages 的输出目录（全部重新生成）

用法：
  python3 build.py            # 检查 + 构建 + 校验
  python3 build.py --og       # 强制重新生成所有 OG 图
  python3 build.py --check    # 只做发布前检查
"""
import hashlib, html, json, os, re, shutil, subprocess, sys, tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# ===== 站点常量（切换域名只改这里）=====
SITE_URL = "https://docs.tryallapi.com"
SITE_NAME = "tryallapi.com"
BRAND_URL = "https://tryallapi.com/"
INDEXNOW_KEY = "38abb406c94e51cafcb5b529f816bfff"
HOME_TITLE = "AI 大模型 API 国内中转调用指南与价格汇总 | tryallapi.com"
HOME_DESC = "GPT、Claude、Gemini、DeepSeek、Kimi、MiMo、混元等大模型 API 国内中转调用指南：官方价格、分组倍率、接入教程与代码。"
TITLE_TPL = "{name} API 国内中转调用指南：价格、教程与代码（2026）"
TITLE_MAX = 32      # 加权长度：汉字/全角 = 1，ASCII = 0.5
DESC_MAX = 80       # 描述按字符数计（不加权），≤80
RELATED_N = 6
VENDOR_ORDER = ["OpenAI", "Anthropic", "Google", "DeepSeek", "xAI", "Qwen", "Moonshot", "Xiaomi", "Tencent", "MiniMax", "ByteDance", "Zhipu"]
VENDOR_LABEL = {"OpenAI": "OpenAI", "Anthropic": "Anthropic（Claude）", "Google": "Google（Gemini）",
                "DeepSeek": "DeepSeek", "xAI": "xAI（Grok）", "Qwen": "阿里通义（Qwen）", "Moonshot": "Moonshot（Kimi）",
                "Xiaomi": "小米（MiMo）", "Tencent": "腾讯混元（Hy）", "MiniMax": "MiniMax",
                "ByteDance": "字节跳动（豆包 Seed）", "Zhipu": "智谱（GLM）"}
FORBIDDEN = ["待填", "待核对", "TODO", "TBD", "fonts.googleapis", "fonts.gstatic"]

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
CONTENT = ROOT / "content"
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
PUBLISHED_JSON = Path(os.environ.get("PUBLISHED_JSON", "/workspace/seo-relay-research/published.json"))
TODAY = date.today().isoformat()
e = lambda s: html.escape(str(s), quote=True)


def wlen(s):
    """加权长度：CJK 与全角字符算 1，其余算 0.5。"""
    return sum(1 if (ord(c) >= 0x2E80) else 0.5 for c in s)


def page_url(slug=""):
    return f"{SITE_URL}/{slug}/" if slug else f"{SITE_URL}/"


def utm(url, campaign, medium="article"):
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    q += [("utm_source", "docs"), ("utm_medium", medium), ("utm_campaign", campaign)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", urlencode(q), parts.fragment))


# ---------------- 数据加载 ----------------
def load_articles():
    arts = json.loads((DATA / "articles.json").read_text(encoding="utf-8"))["articles"]
    pub = {}
    if PUBLISHED_JSON.exists():
        for p in json.loads(PUBLISHED_JSON.read_text(encoding="utf-8")).get("articles", []):
            pub[p.get("repo")] = p.get("date")
    for a in arts:
        if not a.get("date_published"):
            a["date_published"] = pub.get(a["slug"]) or git_first_date(CONTENT / f"{a['slug']}.md") or TODAY
        a.setdefault("title", TITLE_TPL.format(name=a["name"]))
        a["url"] = page_url(a["slug"])
        a["md"] = (CONTENT / f"{a['slug']}.md").read_text(encoding="utf-8")
        m = re.search(r"最后更新[：:]\s*(\d{4}-\d{2}-\d{2})", a["md"])
        a["date_modified"] = max(a["date_published"], m.group(1)) if m else a["date_published"]
    return arts


def git_first_date(path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", str(path)],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
        return out[-1] if out else None
    except Exception:
        return None


# ---------------- 发布前检查 ----------------
def precheck(arts):
    errs = []
    slugs = set()
    for a in arts:
        s = a["slug"]
        if s in slugs:
            errs.append(f"{s}: slug 重复")
        slugs.add(s)
        if a["vendor"] not in VENDOR_ORDER:
            errs.append(f"{s}: 未知厂商 {a['vendor']}（可选：{VENDOR_ORDER}）")
        for k in ("name", "model_id", "description", "summary"):
            if not a.get(k):
                errs.append(f"{s}: 缺少字段 {k}")
        blob = a["md"] + a["title"] + a["description"] + a["summary"]
        for bad in FORBIDDEN:
            if bad in blob:
                errs.append(f"{s}: 含禁止内容「{bad}」")
        if re.search(r"【待", blob):
            errs.append(f"{s}: 含【待…】占位")
        if "价格" not in a["title"]:
            errs.append(f"{s}: 标题缺少「价格」")
        if wlen(a["title"]) > TITLE_MAX:
            errs.append(f"{s}: 标题过长 {wlen(a['title'])} > {TITLE_MAX}：{a['title']}")
        if len(a["description"]) > DESC_MAX:
            errs.append(f"{s}: 描述过长 {len(a['description'])} > {DESC_MAX} 字")
        if "价格" not in a["description"] or "国内" not in a["description"]:
            errs.append(f"{s}: 描述需同时包含「价格」「国内」")
        h1 = [l for l in strip_code(a["md"]).splitlines() if re.match(r"^# ", l)]
        if len(h1) > 1:
            errs.append(f"{s}: 正文有 {len(h1)} 个 H1")
    if len(HOME_DESC) > DESC_MAX:
        errs.append("首页描述过长")
    return errs


def strip_code(md):
    return re.sub(r"^```.*?^```", "", md, flags=re.S | re.M)


# ---------------- Markdown 处理 ----------------
def md_renderer():
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        sys.exit("缺少依赖：pip install -r requirements.txt（markdown-it-py）")
    return MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")


def autolink(md):
    """把裸露的 URL 变成 <url>（跳过代码块和行内代码）。"""
    out, in_code = [], False
    for line in md.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code:
            parts = re.split(r"(`[^`]*`)", line)
            for i in range(0, len(parts), 2):
                parts[i] = re.sub(r"(?<![(<\[\"'=])(https?://[^\s|)<>，。；、\]]+)", r"<\1>", parts[i])
            line = "".join(parts)
        out.append(line)
    return "\n".join(out) + "\n"


def related_for(a, arts):
    same = [x for x in arts if x["vendor"] == a["vendor"] and x["slug"] != a["slug"]]
    other = [x for x in arts if x["vendor"] != a["vendor"]]
    same.sort(key=lambda x: x["date_published"], reverse=True)
    # 其他厂商：每个厂商轮流取最新一篇，保证覆盖面
    by_v = {}
    for x in sorted(other, key=lambda x: x["date_published"], reverse=True):
        by_v.setdefault(x["vendor"], []).append(x)
    rr = []
    while any(by_v.values()):
        for v in VENDOR_ORDER:
            if by_v.get(v):
                rr.append(by_v[v].pop(0))
    return (same[:3] + rr)[:RELATED_N]


def prepare_body(a, arts):
    md = a["md"]
    repo_map = {x["slug"]: x["slug"] for x in arts}
    # 去掉正文 H1（统一用模板标题）与作者/日期行（模板里用 <time> 展示）
    md = re.sub(r"\A\s*# .*\n", "", md)
    md = re.sub(r"^> 作者：[^\n]*首发[^\n]*\n", "", md, count=1, flags=re.M)
    # 旧 github.io 链接改为站内链接
    def fix_link(m):
        slug = m.group(1)
        return f"/{slug}/" if slug in repo_map else m.group(0)
    md = re.sub(r"https?://[Mm]aynor996\.github\.io/([^/)\s]+)/?", fix_link, md)
    # 「相关阅读」：删掉旧的系列链接，插入自动生成的列表
    rel = related_for(a, arts)
    rel_md = "\n".join(f"- [{x['name']} API 国内中转调用指南与价格](/{x['slug']}/)：{x['summary']}" for x in rel)
    rel_md += "\n- [全部 AI 大模型 API 国内调用指南与价格汇总](/)\n"
    sec = re.search(r"^## 相关阅读\s*\n(.*?)(?=^---\s*$|^## |\Z)", md, flags=re.S | re.M)
    if sec:
        kept = [l for l in sec.group(1).splitlines()
                if l.strip() and not re.match(r"^- \[[^\]]*\]\(/[^)]*/\)", l) and "待填" not in l]
        new = "## 相关阅读\n\n" + rel_md + ("\n".join(kept) + "\n" if kept else "") + "\n"
        md = md[:sec.start()] + new + md[sec.end():]
    else:
        md = md.rstrip() + "\n\n---\n\n## 相关阅读\n\n" + rel_md
    return autolink(md), rel


def render_html(md, slug, medium="article"):
    out = md_renderer().render(md)
    out = out.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")

    def fix_a(m):
        href = html.unescape(m.group(1))
        if re.match(r"https?://(www\.)?tryallapi\.com", href):
            return f'<a href="{e(utm(href, slug, medium))}" target="_blank" rel="noopener"'
        if href.startswith("http"):
            return f'<a href="{e(href)}" target="_blank" rel="noopener noreferrer"'
        return f'<a href="{e(href)}"'
    return re.sub(r'<a href="([^"]*)"', fix_a, out)


# ---------------- 模板 ----------------
def head(title, desc, url, og_img, og_type, extra_meta="", ld=None):
    ld_html = ""
    if ld:
        ld_html = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=1).replace("</", "<\\/") + "\n</script>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0b1020">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_img}">
{extra_meta}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/style.css">
{ld_html}
</head>"""


def topbar(campaign, medium):
    return f"""<header class="topbar"><div class="topbar-inner">
<a class="brand" href="/"><span class="brand-mark" aria-hidden="true">✦</span>tryallapi<span class="brand-dot">.com</span> <span class="brand-sub">API 调用指南</span></a>
<nav class="topbar-links" aria-label="站点导航"><a href="/">全部模型</a><a href="{e(utm('https://tryallapi.com/pricing', campaign, medium))}" target="_blank" rel="noopener">价格</a><a class="btn" href="{e(utm(BRAND_URL, campaign, medium))}" target="_blank" rel="noopener">注册 tryallapi.com</a></nav>
</div></header>"""


def footer(campaign, medium):
    return f"""<footer class="site-footer"><div class="wrap">
<p><a href="/">AI 大模型 API 国内中转调用指南</a> · <a href="{e(utm(BRAND_URL, campaign, medium))}" target="_blank" rel="noopener">tryallapi.com</a></p>
<p class="muted">文中价格与倍率均标注取数日期，可能随厂商及平台调整，请以官方页面和 tryallapi.com 控制台为准。第三方中转服务不是模型厂商官方服务。</p>
</div></footer>"""


def publisher():
    return {"@type": "Organization", "name": SITE_NAME, "url": BRAND_URL,
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/logo.png", "width": 512, "height": 512}}


def parse_faq(md):
    sec = re.search(r"^## [^\n]*(FAQ|常见问题)[^\n]*\n(.*?)(?=^## |\Z)", md, flags=re.S | re.M)
    if not sec:
        return []
    items = re.findall(r"^\*\*Q\d+[：:]\s*(.+?)\*\*\s*\n(.+?)(?=\n\s*\n|\Z)", sec.group(2), flags=re.S | re.M)
    clean = lambda t: re.sub(r"\s+", " ", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t.replace("`", "").replace("**", ""))).strip()
    return [(clean(q), clean(a)) for q, a in items]


def article_page(a, arts):
    md, rel = prepare_body(a, arts)
    body = render_html(md, a["slug"])
    faq = parse_faq(a["md"])
    og = f"{SITE_URL}/og/{a['slug']}.png"
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": page_url()},
        {"@type": "ListItem", "position": 2, "name": a["title"], "item": a["url"]}]}
    graph = [{
        "@type": "Article", "headline": a["title"], "description": a["description"],
        "image": [og], "datePublished": a["date_published"], "dateModified": a["date_modified"],
        "inLanguage": "zh-CN", "mainEntityOfPage": a["url"], "url": a["url"],
        "author": {"@type": "Person", "name": "MaynorAI", "url": BRAND_URL},
        "publisher": publisher(), "about": {"@type": "Thing", "name": f"{a['name']} API（{a['model_id']}）"}}, crumbs]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq]})
    ld = {"@context": "https://schema.org", "@graph": graph}
    extra = (f'<meta property="article:published_time" content="{a["date_published"]}">\n'
             f'<meta property="article:modified_time" content="{a["date_modified"]}">\n'
             f'<meta property="article:section" content="{e(a["vendor"])}">\n')
    cta = utm("https://tryallapi.com/pricing", a["slug"])
    return f"""{head(a['title'], a['description'], a['url'], og, 'article', extra, ld)}
<body>
{topbar(a['slug'], 'article')}
<main class="wrap">
<nav class="breadcrumb" aria-label="面包屑"><a href="/">首页</a><span aria-hidden="true">›</span><span aria-current="page">{e(a['name'])} API 指南</span></nav>
<article class="article">
<header class="article-head">
<p class="eyebrow">{e(VENDOR_LABEL.get(a['vendor'], a['vendor']))} · <code>{e(a['model_id'])}</code></p>
<h1>{e(a['title'])}</h1>
<p class="meta">作者 MaynorAI · 首发 <time datetime="{a['date_published']}">{a['date_published']}</time> · 更新 <time datetime="{a['date_modified']}">{a['date_modified']}</time></p>
</header>
{body}
<aside class="cta"><p><strong>{e(a['name'])} API 中转调用</strong>：一个 Key 调用 GPT / Claude / Gemini 等多家模型，按官方价 × 分组倍率计费。</p><a class="btn" href="{e(cta)}" target="_blank" rel="noopener">查看 {e(a['name'])} API 中转价格（tryallapi.com）</a></aside>
</article>
</main>
{footer(a['slug'], 'article')}
</body>
</html>
"""


def home_page(arts):
    groups = []
    items = []
    pos = 0
    for v in VENDOR_ORDER:
        va = sorted([x for x in arts if x["vendor"] == v], key=lambda x: x["date_published"], reverse=True)
        if not va:
            continue
        cards = []
        for x in va:
            pos += 1
            items.append({"@type": "ListItem", "position": pos, "url": x["url"], "name": x["title"]})
            cards.append(f"""<li class="card"><a href="/{x['slug']}/"><span class="card-title">{e(x['name'])} API</span><code>{e(x['model_id'])}</code><span class="card-desc">{e(x['summary'])}</span><span class="card-more">国内调用指南与价格 →</span></a></li>""")
        groups.append(f'<section class="vendor" id="{e(v.lower())}"><h2>{e(VENDOR_LABEL[v])}</h2><ul class="cards">' + "".join(cards) + "</ul></section>")
    last = max(a["date_modified"] for a in arts)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": "AI 大模型 API 国内中转调用指南", "url": page_url(), "inLanguage": "zh-CN",
         "description": HOME_DESC, "publisher": publisher()},
        {"@type": "ItemList", "name": "AI 大模型 API 国内中转调用指南列表", "numberOfItems": len(items), "itemListElement": items},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", "item": page_url()}]}]}
    nav = " · ".join(f'<a href="#{v.lower()}">{e(VENDOR_LABEL[v])}</a>' for v in VENDOR_ORDER if any(x["vendor"] == v for x in arts))
    return f"""{head(HOME_TITLE, HOME_DESC, page_url(), SITE_URL + '/og/index.png', 'website', '', ld)}
<body>
{topbar('home', 'hub')}
<main class="wrap">
<header class="hero">
<p class="eyebrow">共 {len(arts)} 篇 · 更新于 <time datetime="{last}">{last}</time></p>
<h1>AI 大模型 API 国内中转调用指南与价格汇总</h1>
<p class="lead">国内开发者调用 GPT、Claude、Gemini、DeepSeek、Grok、Qwen、Kimi、MiMo、混元、MiniMax 等大模型 API 时，常见的问题是网络不通、境外支付和账号限制。本站按模型整理调用指南：每篇都写清官方价格与上下文参数、官方 / 云厂商 / 聚合平台三类方案的对比、在 <a href="{e(utm(BRAND_URL, 'home', 'hub'))}" target="_blank" rel="noopener">tryallapi.com</a> 用 OpenAI 兼容接口接入的步骤，以及 Python、Node.js、cURL 代码和常见报错排查。</p>
<p class="lead">价格与分组倍率都注明了取数日期，计费规则统一为「官方价 × 分组倍率」，最终以官方页面和控制台为准。</p>
<p class="vendor-nav">{nav}</p>
</header>
{''.join(groups)}
</main>
{footer('home', 'hub')}
</body>
</html>
"""


def page_404():
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>页面不存在 | {SITE_NAME}</title><meta name="robots" content="noindex">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.css"></head>
<body>{topbar('404', 'hub')}
<main class="wrap"><header class="hero"><h1>页面不存在（404）</h1>
<p class="lead">你访问的页面可能已经移动。可以回到 <a href="/">首页</a> 查看全部 AI 大模型 API 国内调用指南。</p></header></main>
{footer('404', 'hub')}</body></html>
"""


# ---------------- OG 图 ----------------
def find_chrome():
    for c in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        p = shutil.which(c)
        if p:
            return p
    return None


def og_html(title, sub, tag):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{font-family:"Noto Sans CJK SC","Noto Sans SC","PingFang SC",sans-serif;background:linear-gradient(135deg,#0b1020 0%,#16224a 60%,#1e3a8a 100%);color:#fff;position:relative}}
.box{{position:absolute;left:80px;right:80px;top:70px;bottom:70px;display:flex;flex-direction:column;justify-content:space-between}}
.tag{{display:inline-block;font-size:30px;color:#93c5fd;letter-spacing:1px}}
h1{{font-size:{86 if len(title) <= 16 else 70}px;line-height:1.15;margin:24px 0 18px;font-weight:700}}
.sub{{font-size:38px;color:#e2e8f0}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:32px;color:#cbd5e1}}
.brand{{font-weight:700;color:#fff;font-size:40px}}.brand span{{color:#60a5fa}}
</style></head><body><div class="box"><div><div class="tag">{e(tag)}</div><h1>{e(title)}</h1><div class="sub">{e(sub)}</div></div>
<div class="foot"><div class="brand">✦ tryallapi<span>.com</span></div><div>docs.tryallapi.com</div></div></div></body></html>"""


def shot(html_str, out_png, w, h, chrome):
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "og.html"
        hp.write_text(html_str, encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={td}/prof", f"--window-size={w},{h}", f"--screenshot={out_png}",
                        hp.as_uri()], check=True, capture_output=True, timeout=90)
    try:   # 可选：用 Pillow 压缩成 256 色 PNG（体积约减少 70%）
        from PIL import Image
        im = Image.open(out_png).convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        im.save(out_png, optimize=True)
    except ImportError:
        pass


def build_images(arts, force):
    og_dir = OUT / "og"
    og_dir.mkdir(parents=True, exist_ok=True)
    state_p = DATA / "og-state.json"
    state = json.loads(state_p.read_text()) if state_p.exists() else {}
    jobs = [("index", "AI 大模型 API 国内调用指南", "价格汇总 · 接入教程 · 代码示例", f"{len(arts)} 个模型 · GPT / Claude / Gemini / DeepSeek / Grok / Qwen / Kimi / MiniMax")]
    for a in arts:
        jobs.append((a["slug"], f"{a['name']} API", "国内中转调用指南：价格、教程与代码", f"{a['vendor']} · {a['model_id']}"))
    chrome = None
    for slug, t, sub, tag in jobs:
        key = hashlib.sha1(f"{t}|{sub}|{tag}|v1".encode()).hexdigest()[:12]
        png = og_dir / f"{slug}.png"
        if not force and state.get(slug) == key and png.exists():
            continue   # 文案没变就复用已提交的 OG 图
        chrome = chrome or find_chrome()
        if not chrome:
            sys.exit("需要 google-chrome / chromium 生成 OG 图")
        shot(og_html(t, sub, tag), png, 1200, 630, chrome)
        state[slug] = key
        print("  og:", slug)
    valid = {j[0] for j in jobs}
    for p in og_dir.glob("*.png"):   # 删除已下线文章的 OG 图
        if p.stem not in valid:
            p.unlink()
    state = {k: v for k, v in state.items() if k in valid}
    state_p.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n")
    logo = ASSETS / "logo.png"
    if not logo.exists():
        chrome = chrome or find_chrome()
        shot("""<html><body style="margin:0;width:512px;height:512px;background:#0b1020;display:flex;align-items:center;justify-content:center;font-family:'Noto Sans CJK SC',sans-serif"><div style="color:#60a5fa;font-size:300px;line-height:1">✦</div></body></html>""",
             logo, 512, 512, chrome)


# ---------------- 站点文件 ----------------
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def build(force_og=False):
    arts = load_articles()
    errs = precheck(arts)
    if errs:
        print("发布前检查失败：")
        for x in errs:
            print("  ✗", x)
        sys.exit(1)
    print(f"检查通过：{len(arts)} 篇")
    OUT.mkdir(exist_ok=True)
    keep = {"og"}
    for p in OUT.iterdir():   # 清理旧输出（OG 图目录保留）
        if p.name in keep:
            continue
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(ASSETS, OUT / "assets", dirs_exist_ok=True)
    build_images(arts, force_og)
    shutil.copy2(ASSETS / "logo.png", OUT / "assets" / "logo.png")
    for a in arts:
        write(OUT / a["slug"] / "index.html", article_page(a, arts))
    write(OUT / "index.html", home_page(arts))
    write(OUT / "404.html", page_404())
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    last = max(a["date_modified"] for a in arts)
    urls = [(page_url(), last, "1.0")] + [(a["url"], a["date_modified"], "0.8")
                                          for a in sorted(arts, key=lambda x: x["date_published"], reverse=True)]
    sm = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <priority>{p}</priority>\n  </url>\n" for u, d, p in urls)
    write(OUT / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    write(OUT / f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY + "\n")
    write(OUT / "_headers", HEADERS)
    # 记录本次的 URL 与 lastmod，供 ping.py 判断哪些页面有变化
    write(DATA / "urls.json", json.dumps({u: d for u, d, _ in urls}, indent=1) + "\n")
    print(f"构建完成：{OUT}（{len(arts)} 篇文章 + 首页）")
    return arts


HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Strict-Transport-Security: max-age=31536000

/assets/*
  Cache-Control: public, max-age=604800

/og/*
  Cache-Control: public, max-age=604800

/sitemap.xml
  Cache-Control: public, max-age=3600

https://:project.pages.dev/*
  X-Robots-Tag: noindex
"""


# ---------------- 构建后校验 ----------------
def validate(arts):
    errs = []
    pages = [OUT / "index.html"] + [OUT / a["slug"] / "index.html" for a in arts]
    for p in pages:
        s = p.read_text(encoding="utf-8")
        rel = p.relative_to(OUT)
        if len(re.findall(r"<h1[\s>]", s)) != 1:
            errs.append(f"{rel}: H1 数量不是 1")
        canon = re.findall(r'<link rel="canonical" href="([^"]+)"', s)
        if len(canon) != 1 or not canon[0].startswith(SITE_URL):
            errs.append(f"{rel}: canonical 异常 {canon}")
        t = html.unescape(re.search(r"<title>(.*?)</title>", s).group(1))
        d = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
        if p != OUT / "index.html" and (wlen(t) > TITLE_MAX or "价格" not in t):
            errs.append(f"{rel}: title 不合格 {t}")
        if len(d) > DESC_MAX:
            errs.append(f"{rel}: description 过长")
        for bad in FORBIDDEN + ["maynor996.github.io", "Maynor996.github.io"]:
            if bad in s:
                errs.append(f"{rel}: 含「{bad}」")
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, flags=re.S):
            json.loads(m.replace("<\\/", "</"))
        for m in re.findall(r'<a href="(https?://(?:www\.)?tryallapi\.com[^"]*)"([^>]*)>', s):
            if "utm_source=docs" not in m[0] or 'rel="noopener"' not in m[1]:
                errs.append(f"{rel}: tryallapi 链接缺 UTM/rel：{m[0]}")
        for m in re.findall(r'href="(/[^"#]*)"', s):
            target = OUT / m.lstrip("/")
            if not (target.is_file() or (target / "index.html").is_file()):
                errs.append(f"{rel}: 站内死链 {m}")
    for a in arts:
        if not (OUT / "og" / f"{a['slug']}.png").exists():
            errs.append(f"缺少 OG 图 {a['slug']}")
    if errs:
        print("构建后校验失败：")
        for x in errs:
            print("  ✗", x)
        sys.exit(1)
    print(f"构建后校验通过：{len(pages)} 个页面")


if __name__ == "__main__":
    if "--check" in sys.argv:
        errs = precheck(load_articles())
        print("\n".join("✗ " + x for x in errs) or "检查通过")
        sys.exit(1 if errs else 0)
    validate(build(force_og="--og" in sys.argv))
