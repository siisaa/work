"""
HTML/CSSプレゼンテーション生成モジュール
16:9形式でPowerPoint代替のスライドを生成する
"""

import os
from datetime import datetime


# ---- テーマ定義 ----

THEMES = {
    "corporate": {
        "primary": "#1E3A5F",
        "secondary": "#2E6DA4",
        "accent": "#F0A500",
        "text": "#333333",
        "slide_bg": "#F5F7FA",
        "bg": "#FFFFFF",
    },
    "dark": {
        "primary": "#0D1B2A",
        "secondary": "#1B4F72",
        "accent": "#E74C3C",
        "text": "#ECF0F1",
        "slide_bg": "#1A252F",
        "bg": "#1A252F",
    },
    "modern": {
        "primary": "#4A235A",
        "secondary": "#7D3C98",
        "accent": "#F1C40F",
        "text": "#2C3E50",
        "slide_bg": "#F8F4FF",
        "bg": "#FFFFFF",
    },
}


# ---- スライドHTML生成 ----

def _bullets_html(bullets: list) -> str:
    html = "<ul class='bullet-list'>"
    for b in bullets:
        if isinstance(b, str):
            html += f"<li>{b}</li>"
        elif isinstance(b, dict):
            html += f"<li>{b.get('text', '')}</li>"
            for sub in b.get("sub", []):
                html += f"<li class='sub-bullet'>{sub}</li>"
    html += "</ul>"
    return html


def _slide_title(slide: dict, num: int, total: int, t: dict) -> str:
    subtitle = slide.get("subtitle", "")
    return f"""
        <div class="slide slide-title">
            <div class="main-title">{slide.get('title', '')}</div>
            <div class="accent-line"></div>
            {f'<div class="subtitle">{subtitle}</div>' if subtitle else ''}
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_section(slide: dict, num: int, total: int, t: dict) -> str:
    subtitle = slide.get("subtitle", "")
    return f"""
        <div class="slide slide-section">
            <div class="section-number">{num:02d}</div>
            <div class="section-title">{slide.get('title', '')}</div>
            <div class="section-line"></div>
            {f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''}
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_bullets(slide: dict, num: int, total: int, t: dict) -> str:
    return f"""
        <div class="slide">
            <div class="slide-header">
                <h2>{slide.get('title', '')}</h2>
                <div class="header-accent"></div>
            </div>
            <div class="slide-body">
                {_bullets_html(slide.get('bullets', []))}
            </div>
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_two_column(slide: dict, num: int, total: int, t: dict) -> str:
    left_title = slide.get("left_title", "")
    right_title = slide.get("right_title", "")
    left = _bullets_html(slide.get("left", []))
    right = _bullets_html(slide.get("right", []))
    return f"""
        <div class="slide">
            <div class="slide-header">
                <h2>{slide.get('title', '')}</h2>
                <div class="header-accent"></div>
            </div>
            <div class="slide-body">
                <div class="two-column">
                    <div class="column-card">
                        {f'<h3>{left_title}</h3>' if left_title else ''}
                        {left}
                    </div>
                    <div class="column-card">
                        {f'<h3>{right_title}</h3>' if right_title else ''}
                        {right}
                    </div>
                </div>
            </div>
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_table(slide: dict, num: int, total: int, t: dict) -> str:
    headers = slide.get("headers", [])
    rows = slide.get("rows", [])
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"""
        <div class="slide">
            <div class="slide-header">
                <h2>{slide.get('title', '')}</h2>
                <div class="header-accent"></div>
            </div>
            <div class="slide-body">
                <table class="data-table">
                    <thead><tr>{header_html}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_summary(slide: dict, num: int, total: int, t: dict) -> str:
    cards_html = ""
    for card in slide.get("cards", []):
        icon = card.get("icon", "✓")
        cards_html += f"""
            <div class="summary-card">
                <div class="card-icon">{icon}</div>
                <h3>{card.get('title', '')}</h3>
                <p>{card.get('description', '')}</p>
            </div>"""
    return f"""
        <div class="slide">
            <div class="slide-header">
                <h2>{slide.get('title', '')}</h2>
                <div class="header-accent"></div>
            </div>
            <div class="slide-body">
                <div class="summary-grid">{cards_html}</div>
            </div>
            <div class="slide-number">{num} / {total}</div>
        </div>"""


def _slide_content(slide: dict, num: int, total: int, t: dict) -> str:
    content = slide.get("content", "")
    return f"""
        <div class="slide">
            <div class="slide-header">
                <h2>{slide.get('title', '')}</h2>
                <div class="header-accent"></div>
            </div>
            <div class="slide-body">
                <p class="content-text">{content}</p>
            </div>
            <div class="slide-number">{num} / {total}</div>
        </div>"""


_SLIDE_RENDERERS = {
    "title": _slide_title,
    "section": _slide_section,
    "bullets": _slide_bullets,
    "two_column": _slide_two_column,
    "table": _slide_table,
    "summary": _slide_summary,
}


# ---- メイン生成関数 ----

def generate_html_presentation(
    title: str,
    slides: list[dict],
    theme: str = "corporate",
    output_dir: str = "presentations",
) -> str:
    """
    HTML/CSSプレゼンテーションを生成してファイルに保存する。

    Returns:
        保存されたHTMLファイルのパス
    """
    t = THEMES.get(theme, THEMES["corporate"])
    total = len(slides)

    slides_html = ""
    for i, slide in enumerate(slides):
        renderer = _SLIDE_RENDERERS.get(slide.get("type", "content"), _slide_content)
        slides_html += renderer(slide, i + 1, total, t)

    html = _build_html(title, slides_html, total, t)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in "-_ " else "" for c in title).strip()[:30]
    filename = f"{safe}_{timestamp}.html".replace(" ", "_")
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(filepath)


def _build_html(title: str, slides_html: str, total: int, t: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
    background:#1C1C1C;
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
    font-family:'Segoe UI','Hiragino Sans','Yu Gothic',sans-serif;
    overflow:hidden;
}}

/* 16:9 ビューポート */
.slide-viewport {{
    position:relative;
    width: min(100vw, 177.78vh);
    height: min(56.25vw, 100vh);
    overflow:hidden;
}}

.slide {{
    position:absolute;
    inset:0;
    display:none;
    flex-direction:column;
    background:{t['bg']};
}}
.slide.active {{ display:flex; }}

/* ---- タイトルスライド ---- */
.slide-title {{
    background:linear-gradient(135deg, {t['primary']} 0%, {t['secondary']} 100%);
    justify-content:center;
    align-items:center;
    text-align:center;
    padding:8%;
}}
.slide-title .main-title {{
    font-size:clamp(1.8rem, 4.5vw, 4.5rem);
    font-weight:700;
    color:#FFF;
    line-height:1.2;
    margin-bottom:0.4em;
    text-shadow:0 2px 8px rgba(0,0,0,.25);
}}
.slide-title .subtitle {{
    font-size:clamp(1rem, 2vw, 2rem);
    color:rgba(255,255,255,.85);
    font-weight:300;
}}
.slide-title .accent-line {{
    width:80px; height:5px;
    background:{t['accent']};
    margin:.8em auto;
    border-radius:3px;
}}

/* ---- セクションスライド ---- */
.slide-section {{
    background:{t['primary']};
    justify-content:center;
    align-items:center;
    text-align:center;
    position:relative;
}}
.section-number {{
    font-size:clamp(4rem, 12vw, 10rem);
    font-weight:900;
    color:rgba(255,255,255,.1);
    position:absolute;
    line-height:1;
    user-select:none;
}}
.section-title {{
    font-size:clamp(1.5rem, 3.5vw, 3.5rem);
    font-weight:700;
    color:#FFF;
    position:relative;
    z-index:1;
}}
.section-line {{
    width:60px; height:4px;
    background:{t['accent']};
    margin:.5em auto;
    border-radius:2px;
    position:relative; z-index:1;
}}
.section-subtitle {{
    font-size:clamp(.9rem, 1.5vw, 1.5rem);
    color:rgba(255,255,255,.7);
    position:relative; z-index:1;
    margin-top:.5em;
}}

/* ---- 共通ヘッダー ---- */
.slide-header {{
    background:{t['primary']};
    padding:3% 5%;
    flex-shrink:0;
}}
.slide-header h2 {{
    font-size:clamp(1.2rem, 2.2vw, 2.2rem);
    color:#FFF;
    font-weight:600;
}}
.header-accent {{
    width:50px; height:3px;
    background:{t['accent']};
    margin-top:.3em;
    border-radius:2px;
}}

/* ---- ボディ ---- */
.slide-body {{
    flex:1;
    padding:4% 6%;
    display:flex;
    flex-direction:column;
    justify-content:center;
    background:{t['slide_bg']};
    overflow:hidden;
}}

/* 箇条書き */
.bullet-list {{ list-style:none; }}
.bullet-list li {{
    display:flex;
    align-items:flex-start;
    margin-bottom:.65em;
    font-size:clamp(.9rem, 1.6vw, 1.6rem);
    color:{t['text']};
    line-height:1.45;
}}
.bullet-list li::before {{
    content:'';
    display:inline-block;
    width:10px; height:10px;
    background:{t['secondary']};
    border-radius:50%;
    margin-right:.6em;
    margin-top:.35em;
    flex-shrink:0;
}}
.bullet-list li.sub-bullet {{
    font-size:clamp(.8rem, 1.3vw, 1.3rem);
    margin-left:2em;
    color:#777;
}}
.bullet-list li.sub-bullet::before {{
    width:7px; height:7px;
    background:{t['accent']};
}}

/* 2カラム */
.two-column {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:5%;
    height:100%;
}}
.column-card {{
    background:#FFF;
    border-radius:10px;
    padding:5%;
    box-shadow:0 2px 16px rgba(0,0,0,.08);
    overflow:auto;
}}
.column-card h3 {{
    font-size:clamp(.9rem, 1.4vw, 1.4rem);
    color:{t['secondary']};
    margin-bottom:.8em;
    padding-bottom:.4em;
    border-bottom:2px solid {t['accent']};
}}

/* テーブル */
.data-table {{
    width:100%;
    border-collapse:collapse;
    font-size:clamp(.75rem, 1.3vw, 1.3rem);
}}
.data-table th {{
    background:{t['primary']};
    color:#FFF;
    padding:.6em 1em;
    text-align:left;
    font-weight:600;
}}
.data-table td {{
    padding:.6em 1em;
    border-bottom:1px solid #E0E0E0;
    color:{t['text']};
}}
.data-table tr:nth-child(even) td {{
    background:rgba(0,0,0,.03);
}}

/* まとめカード */
.summary-grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(150px, 1fr));
    gap:4%;
    align-items:start;
}}
.summary-card {{
    background:#FFF;
    border-radius:10px;
    padding:6%;
    text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,.08);
    border-top:4px solid {t['accent']};
}}
.summary-card .card-icon {{ font-size:clamp(1.5rem, 2.5vw, 2.5rem); margin-bottom:.3em; }}
.summary-card h3 {{
    font-size:clamp(.8rem, 1.2vw, 1.2rem);
    color:{t['primary']};
    margin-bottom:.4em;
    font-weight:600;
}}
.summary-card p {{
    font-size:clamp(.7rem, 1vw, 1rem);
    color:#666;
    line-height:1.4;
}}

/* テキスト */
.content-text {{
    font-size:clamp(1rem, 1.6vw, 1.6rem);
    color:{t['text']};
    line-height:1.7;
}}

/* スライド番号 */
.slide-number {{
    position:absolute;
    bottom:10px; right:16px;
    font-size:.75em;
    color:rgba(0,0,0,.25);
    z-index:10;
}}
.slide-title .slide-number,
.slide-section .slide-number {{ color:rgba(255,255,255,.35); }}

/* ---- ナビゲーション ---- */
.nav-controls {{
    position:fixed;
    bottom:18px;
    left:50%;
    transform:translateX(-50%);
    display:flex;
    align-items:center;
    gap:10px;
    background:rgba(0,0,0,.6);
    backdrop-filter:blur(10px);
    padding:7px 14px;
    border-radius:30px;
    z-index:200;
}}
.nav-btn {{
    background:rgba(255,255,255,.2);
    border:none;
    color:#FFF;
    width:34px; height:34px;
    border-radius:50%;
    cursor:pointer;
    font-size:1em;
    transition:background .2s;
}}
.nav-btn:hover {{ background:rgba(255,255,255,.4); }}
.slide-counter {{
    color:rgba(255,255,255,.9);
    font-size:.85em;
    min-width:55px;
    text-align:center;
}}
.progress-bar {{
    position:fixed;
    bottom:0; left:0;
    height:3px;
    background:{t['accent']};
    transition:width .3s ease;
    z-index:200;
}}
</style>
</head>
<body>
<div class="slide-viewport">
{slides_html}
</div>

<div class="nav-controls">
    <button class="nav-btn" onclick="go(-1)">&#8592;</button>
    <span class="slide-counter" id="ctr">1 / {total}</span>
    <button class="nav-btn" onclick="go(1)">&#8594;</button>
</div>
<div class="progress-bar" id="prog"></div>

<script>
let cur = 0;
const N = {total};
const slides = document.querySelectorAll('.slide');

function show(n) {{
    slides[cur].classList.remove('active');
    cur = Math.max(0, Math.min(n, N - 1));
    slides[cur].classList.add('active');
    document.getElementById('ctr').textContent = (cur+1) + ' / ' + N;
    document.getElementById('prog').style.width = ((cur+1)/N*100) + '%';
}}
function go(d) {{ show(cur + d); }}

document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') go(1);
    if (e.key === 'ArrowLeft') go(-1);
    if (e.key === 'f' || e.key === 'F') document.documentElement.requestFullscreen?.();
}});

show(0);
</script>
</body>
</html>"""
