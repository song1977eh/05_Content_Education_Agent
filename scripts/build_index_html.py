# -*- coding: utf-8 -*-
"""
build_index_html.py — GD docs_html/index.html 목록 페이지를 문서 목록에서 자동 생성한다.

build_docs_html.py의 DOC_LIST를 그대로 스캔해서 카드 목록을 만든다. 새 md 문서를
DOC_LIST에 추가하기만 하면(build_docs_html.py 상단), 다음 빌드에서 index.html에도
자동으로 카드가 나타난다 — 사람이 index.html을 손으로 고칠 필요가 없다.

03_Haemin_Architecture_Agent/system/08_Automation/scripts/build_index_html.py와 같은
워크스페이스 공통 패턴(2026-09-02)이며, 05 프로젝트 구조에 맞게 스캔 대상만 다르다.

실행:
    python build_index_html.py

CLAUDE.md 절대 규칙 9 자동화 지점 — 원본 .md는 읽기만 한다.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_docs_html import PROJECT_ROOT, GD_ROOT, DOC_LIST  # noqa: E402

SYSTEM_DOCS = ["README.md", "CLAUDE.md", "agent_buildup_process.md", "orchestrator.md"]
REFERENCE_DOCS = [d for d in DOC_LIST if d.startswith("references/")]

# 01~04 원본자료 GD 폴더(사진·PDF 등, md 아님)는 여기서 다루지 않는다 —
# 상위 GD_ROOT/index.html(손으로 관리, 이 스크립트가 건드리지 않음)의 "폴더 바로가기" 카드가 담당한다.


def read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def extract_title_desc(path: Path):
    text = read_text(path)
    lines = [l.rstrip() for l in text.splitlines()]
    title = path.stem
    desc = ""
    title_idx = -1
    for i, line in enumerate(lines):
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            title = m.group(1).strip().strip("`")
            title_idx = i
            break
    for line in lines[title_idx + 1:]:
        s = line.strip()
        if not s or s.startswith(("#", ">", "```", "|")):
            continue
        if re.match(r"^(-{3,}|_{3,}|\*{3,})$", s):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"[`*]", "", s)
        desc = s
        break
    if len(desc) > 110:
        desc = desc[:108].rstrip() + "…"
    return title, desc


def card(href: str, title: str, desc: str) -> str:
    return (
        f'      <a class="card" href="{href}">\n'
        f'        <div class="title">{title}</div>\n'
        f'        <div class="desc">{desc}</div>\n'
        f'      </a>'
    )


def render_section(section_title: str, rel_paths, use_docs_prefix: bool = True) -> str:
    items = []
    for rel in rel_paths:
        p = PROJECT_ROOT / rel
        if not p.exists():
            continue
        title, desc = extract_title_desc(p)
        href = str(Path(rel).with_suffix(".html")).replace("\\", "/")
        items.append(card(href, title, desc))
    if not items:
        return ""
    return f'  <section>\n    <h2>{section_title}</h2>\n    <div class="cards">\n{chr(10).join(items)}\n    </div>\n  </section>\n\n'


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>지식·콘텐츠 에이전트 — 문서</title>
<style>
:root {{
  --bg: #fafaf8; --fg: #1f2328; --muted: #6b7280; --accent: #0891b2;
  --border: #e5e0d8; --card-bg: #ffffff; --link: #0e7490;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #14181e; --fg: #e7e9ec; --muted: #a5acb6; --accent: #7fb0e0;
    --border: #2b313b; --card-bg: #1b2029; --link: #7fb0e0;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14181e; --fg: #e7e9ec; --muted: #a5acb6; --accent: #7fb0e0;
  --border: #2b313b; --card-bg: #1b2029; --link: #7fb0e0;
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--bg); color: var(--fg); margin: 0;
  font-family: -apple-system, "Segoe UI", "Malgun Gothic", sans-serif; line-height: 1.6;
}}
.wrap {{ max-width: 920px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}
header h1 {{ font-size: 1.6rem; margin-bottom: 0.2rem; }}
header p {{ color: var(--muted); margin-top: 0; }}
.freshness {{ font-size: 0.85rem; color: var(--muted); margin: 1rem 0 2rem; }}
section {{ margin-top: 2.2rem; }}
h2 {{ font-size: 1.15rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 1rem; margin-top: 1rem; }}
.card {{
  background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
  padding: 1.1rem 1.2rem; text-decoration: none; color: inherit; display: block;
  transition: border-color .15s;
}}
.card:hover {{ border-color: var(--accent); }}
.card .title {{ font-weight: 600; margin-bottom: 0.3rem; font-size: 0.95rem; }}
.card .desc {{ font-size: 0.83rem; color: var(--muted); }}
.manual-link {{
  display: block; background: var(--accent); color: #0b1420; text-decoration: none;
  padding: 1rem 1.2rem; border-radius: 10px; font-weight: 600; margin-top: 1rem;
}}
footer {{ margin-top: 3rem; color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); padding-top: 1rem; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>지식·콘텐츠 에이전트 — 문서</h1>
    <p>해민 AI 5대 에이전트 운영 시스템 5번 · 답사·전시·세미나·워크숍 원본을 실무자료·강의자료·판매콘텐츠·해민건축콘텐츠로 재가공</p>
  </header>

  <p class="freshness">이 페이지는 프로젝트의 md 문서를 스캔해 자동 생성됩니다(원본은 로컬 git에만 있음) · 마지막 생성: {generated_at}</p>

  <a class="manual-link" href="사용설명서.html">📘 사용설명서 열기 — 이 에이전트를 처음 쓰거나 다른 컴퓨터에서 이어갈 때 먼저 읽을 것</a>

{sections}  <footer>
    이 페이지는 <code>build_index_html.py</code>가 자동 생성합니다(README/CLAUDE/references 등 스캔) · CLAUDE.md 절대 규칙 9.
    원본 md는 <code>C:\\projects\\05_Content_Education_Agent</code>(git)에 있습니다.
  </footer>
</div>
</body>
</html>
"""


def build() -> str:
    sections = ""
    sections += render_section("시스템 문서", SYSTEM_DOCS)
    sections += render_section("지식파일 (references/)", REFERENCE_DOCS)
    return TEMPLATE.format(generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"), sections=sections)


def main() -> int:
    GD_ROOT.mkdir(parents=True, exist_ok=True)
    out = build()
    (GD_ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"[build_index_html] 갱신: {GD_ROOT / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
