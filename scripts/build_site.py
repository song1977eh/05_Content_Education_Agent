#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_Content_Education_Agent 문서 빌드 스크립트

이 프로젝트의 모든 md 문서를 html로 변환하고, docs_html/index.html에서
전부 링크로 모아볼 수 있게 한다. md 파일을 새로 쓰거나 수정한 뒤에는
이 스크립트를 다시 실행해야 반영된다(파일 변경을 자동 감시하지는 않음).

사용법:
    python scripts/build_site.py
    python scripts/build_site.py --publish   # GD 동기화 폴더까지 함께 갱신

CLAUDE.md 규칙: 이 프로젝트에서 md 파일을 만들거나 고치면, 그 작업의 마지막 단계로
반드시 이 스크립트를 실행한다(가능하면 --publish 포함).
"""
import argparse
import datetime
import re
import shutil
from pathlib import Path

import markdown

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_OUT = PROJECT_ROOT / "docs_html"

# GD 동기화 폴더(로컬 Drive Desktop 미러) — --publish 시 이 경로로 결과를 복사한다.
GD_TARGET = Path(
    r"I:\다른 컴퓨터\내 노트북\@Haemin AI\Haemin_AI_Workspace(GD)"
    r"\05_Content_Education\05_Content_Education_Agent"
)

# 변환 대상 md 파일 (프로젝트 루트 기준 상대경로) — 그룹별로 정리
DOC_GROUPS = [
    ("시스템 문서", [
        "README.md",
        "CLAUDE.md",
        "agent_buildup_process.md",
        "orchestrator.md",
    ]),
    ("사용 안내", [
        "references/usage_guide.md",
    ]),
    ("지식파일 (references/)", [
        "references/content_principles.md",
        "references/rawsource_taxonomy.md",
        "references/content_conversion_rules.md",
        "references/privacy_masking_checklist.md",
        "references/source_register.md",
        "references/golden_set.md",
    ]),
]

CSS = """
:root{--accent:#0891b2;--accent-bg:#e6f7fa;--bg:#fafafa;--panel:#fff;--text:#1c1f26;--muted:#6b7280;--border:#e5e7eb;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif;
  background:var(--bg);color:var(--text);}
.wrap{max-width:820px;margin:0 auto;padding:40px 24px 100px;}
a{color:var(--accent);}
.backlink{font-size:12.5px;color:var(--muted);text-decoration:none;display:inline-block;margin-bottom:18px;}
.backlink:hover{color:var(--accent);}
h1{font-size:26px;margin:0 0 18px;border-bottom:2px solid var(--accent-bg);padding-bottom:10px;}
h2{font-size:19px;margin-top:34px;color:var(--accent-ink,#0e7490);}
h3{font-size:15px;margin-top:24px;}
p,li{font-size:14px;line-height:1.75;}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--panel);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;margin:14px 0;}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--border);vertical-align:top;}
th{background:var(--accent-bg);font-size:12px;}
code{background:var(--accent-bg);padding:1px 5px;border-radius:4px;font-size:12.5px;}
pre{background:#1c1f26;color:#e5e7eb;border-radius:10px;padding:14px 16px;overflow-x:auto;font-size:12.5px;}
pre code{background:none;color:inherit;padding:0;}
blockquote{border-left:3px solid var(--accent);margin:14px 0;padding:2px 16px;color:var(--muted);background:var(--accent-bg);border-radius:0 8px 8px 0;}
.foot{margin-top:48px;font-size:11.5px;color:var(--muted);border-top:1px solid var(--border);padding-top:14px;}
"""

PAGE_TMPL = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
<a class="backlink" href="{back}">&larr; 문서 목록으로</a>
{body}
<div class="foot">자동 생성됨 · scripts/build_site.py · {built}</div>
</div>
</body>
</html>
"""


def md_to_html_fragment(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
    )


def first_title_and_desc(md_text: str):
    lines = md_text.splitlines()
    title = None
    desc = ""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            # 다음 비어있지 않은 줄을 설명으로 사용 (인용/헤더 제외)
            for rest in lines[i + 1:]:
                rest = rest.strip()
                if not rest or rest.startswith("#"):
                    continue
                desc = re.sub(r"[>*`]", "", rest)[:110]
                break
            break
    return title or "(제목 없음)", desc


def build():
    if DOCS_OUT.exists():
        shutil.rmtree(DOCS_OUT)
    DOCS_OUT.mkdir(parents=True)

    built_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    index_groups_html = []

    for group_name, rel_paths in DOC_GROUPS:
        cards = []
        for rel in rel_paths:
            src = PROJECT_ROOT / rel
            if not src.exists():
                continue
            md_text = src.read_text(encoding="utf-8")
            title, desc = first_title_and_desc(md_text)
            body_html = md_to_html_fragment(md_text)

            out_rel = Path(rel).with_suffix(".html")
            out_path = DOCS_OUT / out_rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            depth = len(out_rel.parts) - 1
            back = ("../" * depth) + "index.html"
            out_path.write_text(
                PAGE_TMPL.format(title=title, css=CSS, back=back, body=body_html, built=built_at),
                encoding="utf-8",
            )

            cards.append(
                f'<a class="card" href="{out_rel.as_posix()}">'
                f'<div class="name">{title}</div>'
                f'<div class="desc">{desc}</div></a>'
            )
        index_groups_html.append(
            f'<h2>{group_name}</h2><div class="cards">{"".join(cards)}</div>'
        )

    index_css = CSS + """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-bottom:8px;}
.card{display:block;border:1px solid var(--border);background:var(--panel);border-radius:12px;
  padding:14px 16px;text-decoration:none;color:var(--text);}
.card:hover{border-color:var(--accent);}
.card .name{font-weight:700;font-size:13.5px;margin-bottom:4px;}
.card .desc{font-size:12px;color:var(--muted);line-height:1.5;}
"""
    index_body = f"""
<h1>05 지식·콘텐츠 에이전트 — 문서 모음</h1>
<p style="color:var(--muted);font-size:13.5px;">이 페이지는 프로젝트의 모든 md 문서를 자동 변환한 목록이다.
md를 수정한 뒤에는 <code>python scripts/build_site.py</code>를 다시 실행해야 갱신된다.</p>
{"".join(index_groups_html)}
"""
    index_html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>지식·콘텐츠 에이전트 — 문서</title>
<style>{index_css}</style>
</head>
<body>
<div class="wrap">
{index_body}
<div class="foot">자동 생성됨 · scripts/build_site.py · {built_at}</div>
</div>
</body>
</html>
"""
    (DOCS_OUT / "index.html").write_text(index_html, encoding="utf-8")
    print(f"[build_site] {DOCS_OUT} 생성 완료 ({built_at})")


def publish():
    if not GD_TARGET.exists():
        print(f"[build_site] GD 폴더를 찾을 수 없어 게시를 건너뜀: {GD_TARGET}")
        return
    dest = GD_TARGET / "docs_html"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(DOCS_OUT, dest)
    print(f"[build_site] GD로 게시 완료: {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true", help="GD 동기화 폴더로도 결과를 복사")
    args = parser.parse_args()
    build()
    if args.publish:
        publish()
