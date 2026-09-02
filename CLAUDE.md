# CLAUDE.md — 05_Content_Education_Agent 절대규칙

이 프로젝트에서 작업할 때 아래 규칙을 항상 지킨다. 시스템 프롬프트(정체성/원칙 요약)는 [README.md](README.md)를 참조한다.

## 절대 규칙

1. **보류는 승인 대기다, 자동 차단이 아니다.** 출처·마스킹·저작권 중 결측이 있으면 구체적으로 짚어 사용자에게 승인을 요청하고, 승인받은 뒤에만 다음 단계로 진행한다. 승인 없이 임의로 넘어가지 않는다.
2. **관리 단위는 폴더(행사 1건)다.** `03_답사_전시_세미나기록/[행사명]/` 안의 파일을 개별적으로 상태 추적하지 않는다. 폴더 전체를 하나의 덩어리로 분석한다.
3. **사실/의견/우리 해석을 항상 구분해 표기한다.** ([references/rawsource_taxonomy.md](references/rawsource_taxonomy.md) §4)
4. **개인정보·클라이언트 식별정보는 콘텐츠 초안에 남기지 않는다.** ([references/privacy_masking_checklist.md](references/privacy_masking_checklist.md))
5. **원문 그대로의 재유포를 하지 않는다.** 강사 자료·전시 이미지 등은 요약·재구성만 한다. 판매용 콘텐츠는 특히 엄격히 적용.
6. **이 에이전트는 최종 발행·판매 등록을 하지 않는다.** 산출물은 항상 "검수 전 초안" 상태까지다.
7. **상태값은 `data/state.json`에 영속 저장한다.** 대화가 끝나도 다음 세션에서 `data/state.json`을 먼저 읽고 이어받는다.
8. **확정적 지시·보장 문구를 쓰지 않는다.** "~로 판단됨/검토 의견"으로 표현한다.
9. **문서 수정 시 HTML도, GD `docs_html/index.html` 목록도 함께 갱신한다.** `README.md`·`CLAUDE.md`·`agent_buildup_process.md`·`orchestrator.md`·`사용설명서.md`·`references/*.md`를 수정하면 GD의 `.html` 사본도 같이 최신화한다. `.claude/settings.json`의 PostToolUse 훅(`scripts/doc_hook_autobuild.py`)이 Edit/Write 직후 `build_docs_html.py`(개별 .html)와 `build_index_html.py`(목록 재생성)를 순서대로 자동 호출하므로 평소엔 신경 쓸 필요가 없다. 훅은 Claude Code의 Edit/Write를 통한 변경만 감지하므로, 탐색기에서 직접 옮기거나 지운 경우 또는 훅이 아직 로드되지 않은 세션에서는 `python scripts/build_docs_html.py --all` 후 `python scripts/build_index_html.py`를 수동 실행한다. 새 md 문서를 추가했다면 `scripts/build_docs_html.py`의 `DOC_LIST`에도 경로를 추가해야 훅과 목록이 그 문서를 인식한다(03_Haemin_Architecture_Agent와 동일 패턴, 워크스페이스 공통).

## GD 연동

- 대응 GD 폴더: `Haemin_AI_Workspace(GD)/05_Content_Education/05_Content_Education_Agent/`
- 폴더 URL: https://drive.google.com/drive/folders/1tALrUvNSr1pmUaTps_4JmAJr-PCvKRC7
- 이 프로젝트에서 **로컬(Git)**에 두는 것: `CLAUDE.md`, `README.md`, `agent_buildup_process.md`, `references/`, `orchestrator.md`, `data/state.json`
- 이 프로젝트에서 **GD**에 두는 것:
  - `01_원본강의자료/` (기존 유지 — 협회 교육 원본)
  - `02_교육자료분석/` (기존 유지 — 교육 비교분석)
  - `03_답사_전시_세미나기록/` (원본 기록, 신설 — 여기서 폴더 단위로 원본을 받는다)
  - `04_지식재사용노트/` (최종 산출물 — 4종 콘텐츠 초안/완성본)

## 집·사무실 병행작업 체크리스트

- 세션 시작 시: ① `git pull`로 로컬 최신화 ② GD가 최신 상태인지 확인(특히 `03_답사_전시_세미나기록`에 새 폴더가 들어왔는지)
- 세션 종료 시: ① 변경사항 `git commit` + `push` ② `data/state.json` 갱신 내용이 커밋에 포함됐는지 확인
- 같은 폴더를 집/사무실에서 동시에 편집하지 않는다

## 참고

- 이 프로젝트의 에이전트 제작 과정 전문: [agent_buildup_process.md](agent_buildup_process.md)
- 범용 가이드(템플릿, 수정하지 않음): GD `00_Operating_Standards/에이전트_제작가이드/에이전트_제작_가이드_v02.md`
