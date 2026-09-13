# B5-1 감사 지적 처리 보고서

- 공식 원문: 2026-08-15 제공 PDF 6쪽 (요구사항 정리는 [`../QUEST.md`](../QUEST.md))
- 기능 PR: <https://github.com/giyeop-cody/B5-1/pull/5>
- 검사 기준 브랜치: `main`
- 기록 원칙: 근거는 이 저장소 안의 파일·PR·커밋만 링크한다. 보는 사람이 열 수 없는 경로는 근거로 쓰지 않는다(근거: [`decision-log.md`](decision-log.md) D14).

## 권장 순서 1~13 처리 결과

| 순서 | 감사 지적 | 처리 | 저장소 안 근거 |
|---:|---|---|---|
| 1 | 40분 → 40시간 | 완료 | `QUEST.md`, README |
| 2 | 실행 파일명 정정 | 완료 | README의 `1_schema.sql → 2_data.sql → 3_queries.sql` 안내 |
| 3 | 오래된 결과 이미지 재생성 | 완료 | `evidence/captures/query_01.png` ~ `query_15.png`, `bonus_fk_error.png` |
| 4 | Q5/9/12 분석 일치 | 완료 | [`complex-query-analysis.md`](complex-query-analysis.md) |
| 5 | UPDATE 조건·개발 로그 일치 | 완료 | Q13/Q14의 ID+현재 상태 가드, 영향 1행 검증 |
| 6 | `order_time`·SQLite 타입 설명 | 완료 | DDL 주석, [`../architecture_design.md`](../architecture_design.md) §1 |
| 7 | Q7/8 의미 일치 | 완료 | 전체 기간 미주문 메뉴·좌석으로 통일 |
| 8 | JOIN DISTINCT·성능 설명 | 완료 | 행 값 동치 + `EXPLAIN QUERY PLAN` 기록, 우위 주장 회피 |
| 9 | CHECK·실패 테스트 | 완료 | price/table/capacity/quantity/status CHECK와 차단 실증 |
| 10 | 15개 결과 일괄 재생성 | 완료 | `scripts/verify_project.py`, `scripts/check_all.sh` |
| 11 | 스키마·쿼리 정합성 정정 | 완료 | 실제 4-table 스키마와 15개 쿼리 일치 |
| 12 | 학습 문서와 브랜치 안내 | 완료 | [`../LEARNING.md`](../LEARNING.md), [`learning-journal.md`](learning-journal.md) |
| 13 | commit 작성자 이메일 정리 | 완료 | [`email-rewrite-map.tsv`](email-rewrite-map.tsv), [`history-rewrite.md`](history-rewrite.md) |

## 2026-09-13 재감사 지적과 처리

문서·증거가 SQL과 어긋나기 시작한 지점을 다시 찾아 처리했다.

| 지적 | 처리 |
|---|---|
| `bonus_report.md`가 존재하지 않는 SQL(`order_time BETWEEN`)을 설명 | 실제 `4_bonus_queries.sql` 본문으로 보고서 재생성. 인용문이 파일과 다르면 검증이 실패하도록 검사 추가 |
| README 수동 순서(스키마→seed→Q1~Q15→보너스)로 치면 증거와 숫자가 다름 | `verify_project.py`가 같은 순서·같은 DB로 보너스를 실행하도록 변경. 증거가 수동 실행 결과를 따름 |
| 기본 조회 4개 중 `LIMIT`이 1개 | Q02·Q03·Q04에 `LIMIT` 추가 + 세 절 존재를 자동 검사로 승격 |
| `evidence/screenshots`가 실제 캡처로 오인될 수 있음 | `evidence/captures`로 이름 바꾸고 PNG 머리글·README에 "스크립트가 텍스트 증거를 렌더링"임을 명시 |
| 저장소 밖 절대 경로를 근거로 인용 | 전부 삭제하고 markdown 검사로 금지 |
| 과거 실행 계획·행 수치 등재(5행, 20.8%) | 변경 후 상태 기준(4행, 16.7%)으로 문서 전체 동기화 |

## 자동 검증 결과

```text
B5-1 AUTOMATED VERIFICATION: ALL PASS
B5-1 CHECK ALL: PASS
```

- 테이블: 4개, seed: 10/12/16/25행
- PK: 모든 테이블 PASS, FK: 3개, `PRAGMA foreign_keys=ON` PASS
- 핵심 SQL: 15개 PASS, 보너스 SQL: 5개 PASS
- 기본 조회 4개가 `WHERE`·`ORDER BY`·`LIMIT`을 모두 포함 PASS
- FK·status·quantity·UNIQUE 위반 차단 PASS
- JOIN/서브쿼리: 4행 전체 값 동치 PASS
- KPI: 카테고리 10행, 수용 인원 4행, 혼잡도 1행(16.7%) PASS
- 결과 이미지 16개, ERD 재생성 PASS
- 문서 동기화(`bonus_report.md` 인용 SQL, README 설명·링크, 저장소 밖 경로 금지) PASS
- `check_all.sh` 재생성 후 `git status`가 깨끗함 → 커밋된 증거와 산출물이 동일

## fresh clone 검증

`main`을 새 디렉터리에 clone해 아래를 확인하는 절차를 기준으로 삼는다.

- `scripts/check_all.sh` PASS
- 검사 후 working tree clean
- 모든 markdown 링크가 저장소 안 파일을 가리킴
