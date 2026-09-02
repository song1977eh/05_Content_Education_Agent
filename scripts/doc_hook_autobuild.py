# -*- coding: utf-8 -*-
"""
doc_hook_autobuild.py — Claude Code PostToolUse 훅에서 호출되는 헬퍼 (05_Content_Education_Agent)

## 사용 목적
Edit/Write 툴 호출이 끝난 뒤 훅(PostToolUse)이 이 스크립트에 그 호출의 JSON 페이로드를
stdin으로 넘긴다. 수정된 파일이 이 프로젝트의 문서 목록(DOC_LIST, build_docs_html.py)에
해당하면 build_docs_html.py를 그 파일에 대해 자동 실행해 GD의 .html 사본을 갱신하고,
이어서 build_index_html.py로 GD docs_html/index.html 목록도 다시 만든다.
CLAUDE.md 절대규칙 9(문서 수정 시 html도 함께 갱신)를 사람이 매번 기억하지 않아도
되게 만든 실제 자동화 지점이다.

03_Haemin_Architecture_Agent의 동일 이름 스크립트와 같은 패턴(2026-09-02, 워크스페이스 공통).

## 대상 파일 패턴
- README.md, CLAUDE.md, agent_buildup_process.md, orchestrator.md, 사용설명서.md (프로젝트 루트)
- references/*.md
위 목록에 없는 파일이면 아무 출력 없이 조용히 종료한다(exit 0).

## 안전 설계
- 이 스크립트가 실패해도 Claude Code의 원래 작업(Edit/Write)을 막으면 안 되므로,
  모든 예외를 잡아 stderr에만 남기고 항상 exit 0으로 끝난다.
- 원본 .md는 절대 건드리지 않는다 — build_docs_html.py / build_index_html.py 호출만
  한다(둘 다 .md를 읽기만 하고 GD 쪽 .html만 쓴다).
- Edit/Write는 Claude Code를 통한 변경만 감지한다. 탐색기에서 직접 옮기거나 지우는 등
  Claude Code 밖에서 일어난 변경에는 반응하지 않는다 — 그런 경우엔 수동으로
  `python scripts/build_docs_html.py --all` 후 `python scripts/build_index_html.py`를 실행한다.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    # 03의 doc_hook_autobuild.py에서 발견된 근본 원인과 동일: stdin을 reconfigure하지
    # 않으면 Windows 기본 코드페이지(cp949)로 읽혀 UTF-8 JSON 페이로드 속 한글 경로가
    # 깨진다. 항상 UTF-8로 강제한다.
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BUILD_DOCS_SCRIPT = SCRIPT_DIR / "build_docs_html.py"
BUILD_INDEX_SCRIPT = SCRIPT_DIR / "build_index_html.py"
PYTHON_EXE = r"C:\Python310-32\python.exe"

PATTERNS = [
    re.compile(r"/README\.md$", re.IGNORECASE),
    re.compile(r"/CLAUDE\.md$", re.IGNORECASE),
    re.compile(r"/agent_buildup_process\.md$", re.IGNORECASE),
    re.compile(r"/orchestrator\.md$", re.IGNORECASE),
    re.compile(r"/사용설명서\.md$", re.IGNORECASE),
    re.compile(r"/references/[^/]+\.md$", re.IGNORECASE),
]


def matches(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/")
    if "05_Content_Education_Agent" not in normalized:
        return False
    return any(p.search(normalized) for p in PATTERNS)


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)

        file_path = (
            payload.get("tool_input", {}).get("file_path")
            or payload.get("tool_response", {}).get("filePath")
        )
        if not file_path:
            return 0
        if not file_path.lower().endswith(".md"):
            return 0
        if not matches(file_path):
            return 0

        result = subprocess.run(
            [PYTHON_EXE, str(BUILD_DOCS_SCRIPT), "--md", file_path],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            print(f"[doc_hook_autobuild] html 갱신 완료: {file_path}")
        else:
            print(f"[doc_hook_autobuild] build_docs_html.py 실패({result.returncode}): "
                  f"{(result.stderr or '').strip()[:300]}", file=sys.stderr)

        idx_result = subprocess.run(
            [PYTHON_EXE, str(BUILD_INDEX_SCRIPT)],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        if idx_result.returncode == 0:
            print("[doc_hook_autobuild] index.html 목록 갱신 완료")
        else:
            print(f"[doc_hook_autobuild] build_index_html.py 실패({idx_result.returncode}): "
                  f"{(idx_result.stderr or '').strip()[:300]}", file=sys.stderr)
    except Exception as e:  # 훅은 절대 원래 작업을 막으면 안 된다
        print(f"[doc_hook_autobuild] 오류(무시하고 계속): {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
