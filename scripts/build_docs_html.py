# -*- coding: utf-8 -*-
"""
build_docs_html.py — 05_Content_Education_Agent 문서(.md)를 정적 .html로 변환 (외부 라이브러리 불필요)

## 사용 목적
README.md/CLAUDE.md/agent_buildup_process.md/orchestrator.md/사용설명서.md와 references/*.md를
더블클릭으로 바로 열어볼 수 있는 .html로 변환해 GD `docs_html/`(Drive 동기화 폴더)에 게시한다.
다른 기기(회사 컴퓨터 등)에서도 브라우저로 바로 열람 가능하다.

03_Haemin_Architecture_Agent/system/08_Automation/scripts/build_docs_html.py와 동일한
변환기를 그대로 재사용한다(워크스페이스 공통 패턴, 2026-09-02). 표준 마크다운 전체가
아니라 이 프로젝트 문서들이 실제로 쓰는 문법만 지원한다: 헤딩(#~####), 굵게(**),
인라인 코드(`), 링크([]()), 표(|...|), 순서/비순서 목록, 인용(>), 구분선(---).

## 05 프로젝트 고유 차이점(03과 다른 점)
- 원본 .md는 로컬 git(`C:\\projects\\05_Content_Education_Agent`)에만 있고 GD에는 없다.
  이 스크립트는 git의 .md를 읽어 GD_ROOT(아래)의 같은 상대경로에 .html만 쓴다 — GD에 .md를
  만들지 않는다.
- 여러 폴더 깊이(references/ 등)에서 "목록으로" 링크가 항상 올바르게 돌아가도록 상대 경로
  깊이를 계산한다(03 버전은 항상 "index.html"로 고정되어 있어 하위 폴더에서는 깨짐).

## 실행
    python build_docs_html.py --md "..\\README.md"
    python build_docs_html.py --all   (DOC_LIST 전체를 다시 생성)

CLAUDE.md 절대 규칙 9: 이 스크립트는 문서를 "보기 좋게 바꾸는" 조회용 산출물만 만든다.
원본 .md 파일은 건드리지 않는다(읽기 전용).
"""

import argparse
import html
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GD_ROOT = Path(
    r"I:\다른 컴퓨터\내 노트북\@Haemin AI\Haemin_AI_Workspace(GD)"
    r"\05_Content_Education\05_Content_Education_Agent\docs_html"
)

DOC_LIST = [
    "README.md",
    "CLAUDE.md",
    "agent_buildup_process.md",
    "orchestrator.md",
    "사용설명서.md",
    "references/content_principles.md",
    "references/rawsource_taxonomy.md",
    "references/content_conversion_rules.md",
    "references/privacy_masking_checklist.md",
    "references/source_register.md",
    "references/golden_set.md",
]

CSS = """
:root {
  --bg: #fafaf8; --fg: #1f2328; --muted: #6b7280; --accent: #0891b2;
  --border: #e5e0d8; --table-head: #e6f7fa; --code-bg: #e6f7fa;
  --callout-bg: #e6f7fa; --callout-border: #0891b2; --link: #0e7490;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14181e; --fg: #e7e9ec; --muted: #a5acb6; --accent: #7fb0e0;
    --border: #2b313b; --table-head: #20304a; --code-bg: #20304a;
    --callout-bg: #20304a; --callout-border: #7fb0e0; --link: #7fb0e0;
  }
}
:root[data-theme="dark"] {
  --bg: #14181e; --fg: #e7e9ec; --muted: #a5acb6; --accent: #7fb0e0;
  --border: #2b313b; --table-head: #20304a; --code-bg: #20304a;
  --callout-bg: #20304a; --callout-border: #7fb0e0; --link: #7fb0e0;
}
* { box-sizing: border-box; }
body {
  background: var(--bg); color: var(--fg); margin: 0;
  font-family: -apple-system, "Segoe UI", "Malgun Gothic", sans-serif;
  line-height: 1.7;
}
.page { max-width: 860px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }
h1, h2, h3, h4 { line-height: 1.35; }
h1 { font-size: 1.75rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.5rem; }
h2 { font-size: 1.35rem; margin-top: 2.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
h3 { font-size: 1.1rem; margin-top: 1.8rem; color: var(--accent); }
h4 { font-size: 1rem; margin-top: 1.3rem; }
p { margin: 0.8rem 0; }
a { color: var(--link); }
code { background: var(--code-bg); padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.9em; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; overflow-x: auto; display: block; }
th, td { border: 1px solid var(--border); padding: 0.5rem 0.7rem; text-align: left; }
th { background: var(--table-head); }
blockquote {
  margin: 1rem 0; padding: 0.7rem 1rem; background: var(--callout-bg);
  border-left: 4px solid var(--callout-border); border-radius: 0 6px 6px 0; color: var(--fg);
}
ul, ol { padding-left: 1.4rem; }
li { margin: 0.3rem 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
.meta { color: var(--muted); font-size: 0.9rem; }
.nav-back { display: inline-block; margin-bottom: 1.2rem; font-size: 0.9rem; }
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def convert(md_text: str, title: str, back_href: str) -> str:
    lines = md_text.splitlines()
    out = []
    i = 0
    in_list = None
    in_quote = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    def close_quote():
        nonlocal in_quote
        if in_quote:
            out.append("</blockquote>")
            in_quote = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            close_list()
            close_quote()
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)", stripped)
        if m:
            close_list()
            close_quote()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if stripped == "---":
            close_list()
            close_quote()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            if not in_quote:
                close_list()
                out.append("<blockquote>")
                in_quote = True
            out.append(f"<p>{inline(stripped.lstrip('>').strip())}</p>")
            i += 1
            continue
        else:
            close_quote()

        if stripped.startswith("|"):
            close_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            if len(rows) >= 2:
                header = [c.strip() for c in rows[0].strip("|").split("|")]
                body_rows = rows[2:] if re.match(r"^[\s:|-]+$", rows[1].strip("|")) else rows[1:]
                out.append("<table><thead><tr>")
                for c in header:
                    out.append(f"<th>{inline(c)}</th>")
                out.append("</tr></thead><tbody>")
                for r in body_rows:
                    cells = [c.strip() for c in r.strip("|").split("|")]
                    out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                out.append("</tbody></table>")
            continue

        m = re.match(r"^[-*]\s+(.*)", stripped)
        if m:
            if in_list != "ul":
                close_list()
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            if in_list != "ol":
                close_list()
                out.append("<ol>")
                in_list = "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        close_list()
        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    close_list()
    close_quote()

    body = "\n".join(out)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
<a class="nav-back" href="{back_href}">← 목록으로</a>
{body}
</div>
</body>
</html>
"""


def build_one(md_path: Path):
    rel = md_path.resolve().relative_to(PROJECT_ROOT)
    text = md_path.read_text(encoding="utf-8")
    first_line = next((l for l in text.splitlines() if l.strip()), md_path.stem)
    title = re.sub(r"^#+\s*", "", first_line).strip()

    depth = len(rel.parts) - 1
    back_href = ("../" * depth) + "index.html"

    html_out = convert(text, title, back_href)
    out_path = GD_ROOT / rel.with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"생성: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="05 프로젝트 문서(.md)를 GD docs_html/*.html로 변환")
    parser.add_argument("--md", help="변환할 .md 파일 경로 1개(git 저장소 기준 경로)")
    parser.add_argument("--all", action="store_true", help="DOC_LIST 전체를 다시 생성")
    args = parser.parse_args()

    if args.md:
        build_one(Path(args.md).resolve())
    elif args.all:
        for rel in DOC_LIST:
            p = PROJECT_ROOT / rel
            if p.exists():
                build_one(p)
    else:
        sys.exit("사용법: --md <파일> 또는 --all")


if __name__ == "__main__":
    main()
