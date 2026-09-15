# B5-1 개발 및 트러블슈팅 기록

## 1. 작업 방식

공식 미션 PDF를 기준으로 요구사항을 작은 단계로 나눴다.

1. 요구사항과 기존 파일 비교
2. SQL을 새 메모리 DB에서 직접 실행
3. 한 종류의 변경을 적용
4. 자동 검증 추가
5. 결과 텍스트·이미지 재생성
6. 문서와 실제 구현을 다시 대조

검토 중 발견한 문제는 GitHub Issue #1~#4에서 추적한다.

## 2. 처음 확인한 문제와 해결

### 2.1 실행 파일명이 실제 파일과 달랐음 — Issue #1

- 문제: 안내에는 `schema.sql`, `data.sql`, `queries.sql`이라고 적혀 있었지만 실제 파일은 `1_schema.sql`, `2_data.sql`, `3_queries.sql`이었다.
- 원인: 문서를 작성한 뒤 파일명 변경이 반영되지 않았다.
- 해결: README와 요구사항 문서의 실행 명령을 실제 파일명으로 통일했다.
- 재발 방지: `sqlite3` 실행 예시와 Python 대체 명령을 모두 실제 파일명으로 실행해 본다.

### 2.2 DDL 설명과 SQLite 동작이 어긋났음 — Issue #1, #3

- 문제: 설명은 일반적인 DB 타입처럼 읽혔고, `PRAGMA foreign_keys = ON`의 연결 단위 특성이 충분히 드러나지 않았다.
- 해결: SQLite에는 별도 DATETIME 저장 클래스가 없음을 설명하고 ISO 형식 문자열 사용 규칙을 기록했다. 모든 검증 연결에서 FK를 켠다.

### 2.3 CHECK 제약이 부족했음 — Issue #3

- 재현: 수정 전 스키마에서 `quantity=-1`과 `status='INVALID'` 입력이 허용됐다.
- 위험: SQL이 실행되더라도 업무 의미상 잘못된 데이터가 저장된다.
- 해결:
  - `menus.price >= 0`
  - `store_tables.table_number > 0`
  - `store_tables.capacity > 0`
  - `orders.quantity > 0`
  - `orders.status IN ('COOKING', 'SERVED', 'CANCELLED')`
- 검증: 음수 수량과 잘못된 상태 입력이 모두 `CHECK constraint failed`로 차단됐다.

### 2.4 Query 7/8 설명과 실제 조건이 달랐음 — Issue #3

- 문제: `LEFT JOIN`의 미매칭 행을 찾는 SQL인데 기존 설명이 다른 조건을 말하거나, 미주문 메뉴를 보여 줄 seed가 없었다.
- 해결: Query 7은 전체 기간의 미주문 메뉴, Query 8은 전체 기간의 미주문 좌석을 찾는다고 설명을 통일했다. 한 번도 주문되지 않은 `유자차`를 seed에 추가했다.
- 결과: Query 7은 `(16, '유자차', 4500)` 1행을 반환한다. Query 8은 주문 이력이 없는 `(2, 2)`, `(11, 2)`, `(12, 4)` 3행을 반환한다.

### 2.5 UPDATE/DELETE가 현재 상태를 확인하지 않았음 — Issue #3

- 문제: ID만 일치하면 이미 처리된 주문도 다시 변경할 수 있었다.
- 대안:
  1. `WHERE id = ?`만 사용: 간단하지만 안전성이 낮다.
  2. `WHERE id = ? AND status = ?` 사용: SQL이 조금 길지만 예상 상태일 때만 바뀐다.
- 결정: 두 번째 방식을 선택했다.
- 적용: Query 13은 주문 18이 `COOKING`일 때만 `SERVED`로 바꾸고, Query 14는 주문 25가 `CANCELLED`일 때만 삭제한다.
- 결과: 각각 정확히 1행만 변경됐다.

### 2.6 실행 결과 이미지와 SQL 결과가 서로 달랐음 — Issue #2

- 문제: 과거 실행 결과 이미지와 현재 SQL이 같은 실행에서 만들어졌다는 보장이 없었다.
- 해결: `scripts/verify_project.py`가 새 DB 하나에서 Query 1~15를 순서대로 실행해 텍스트를 만들고, `scripts/generate_captures.py`가 그 텍스트로 이미지를 만든다.
- 결과: Query 1~15 이미지 15개와 FK 오류 이미지 1개를 다시 만들었다.
- 추가 조치(2026-09-13): 사람이 DB 도구를 써서 찍은 화면과 구분되도록 디렉터리를 `evidence/screenshots`에서 `evidence/captures`로 이름을 바꾸고, 이미지 머리글에 "스크립트가 텍스트 증거를 렌더링"했다. 미션이 스크린샷 **또는** 결과 텍스트를 허용하므로 원본은 텍스트이고 이미지는 복제본이다.

### 2.7 Query 5/9/12 분석이 실제 SQL과 달랐음 — Issue #2

- 문제: 문서 일부가 현재 존재하지 않는 고객·주문상세 도메인 또는 다른 조건을 설명했다.
- 해결: 현재 Query 5의 3-table JOIN, Query 9의 카테고리 집계, Query 12의 최고가 메뉴 서브쿼리 기준으로 문서를 전부 다시 썼다.

### 2.8 ERD의 타입 오기 — Issue #2

- 문제: 주문 시각 타입에 `DATETTME` 오기가 있었다.
- 해결: 현재 4개 테이블, 컬럼, CHECK 요약, 3개 FK를 읽을 수 있도록 ERD를 재생성했다.

### 2.9 JOIN과 서브쿼리 성능을 단정할 수 없음 — Issue #3

- 문제: 작은 seed 결과만 보고 어느 방법이 항상 빠르다고 말할 수 없다.
- 해결: 두 SQL의 결과를 정렬된 튜플 집합으로 비교하고 SQLite `EXPLAIN QUERY PLAN`도 함께 저장했다.
- 결론: Q13·Q14가 지난 뒤의 상태(§2.14)에서 두 결과 집합은 같은 4행이다. 성능 우위는 DB, 통계, 인덱스, 데이터 분포에 따라 달라지므로 단정하지 않는다.

### 2.10 인덱스 효과 설명 범위 — Issue #3

- 문제: 실제 측정 없이 일반적인 성능 향상을 확정할 수 없다.
- 해결: `idx_order_status`를 멱등 생성하고 현재 검증 DB의 실행 계획이 `SEARCH orders USING INDEX idx_order_status (status=?)`인지까지만 확인한다.

### 2.11 검증할 때마다 임시 DB 경로가 달라졌음 — Issue #2

- 발견: `scripts/check_all.sh`를 다시 실행하자 내용은 같지만 `evidence/verification_summary.txt`의 `/tmp/...` 경로만 바뀌었다.
- 원인: 임시 디렉터리의 무작위 이름을 영구 증거 파일에 기록했다.
- 해결: 경로 대신 `fresh SQLite database created for this run`이라는 안정된 설명을 기록한다.
- 검증: 전체 검사를 연속 두 번 실행하고 모든 텍스트·PNG·ERD의 SHA-256 목록이 같은지 비교해 PASS를 확인했다.

### 2.12 공식 요구사항의 SQL 범주 및 스키마 검증 자동화 — Issue #7

- 발견: 실제 구현은 공식 요구사항의 SQL 분포와 컬럼 타입 조건을 충족했지만, 기존 요약은 `core_queries=15`만 표시해 기본 조회·JOIN·집계 등의 개별 범주 수량을 한눈에 확인하기 어려웠다.
- 해결:
  - 15개 컬럼 이름·타입 일치 검사
  - NOT NULL 컬럼과 UNIQUE 인덱스 개수 검사
  - Q01~Q15 연속 번호와 한 줄 설명 검사
  - 기본 4·JOIN 4·집계 3·서브쿼리 1·수정삭제 2·인덱스 1 분포 검사
  - 결과 텍스트 15개 생성 검사
- 문서: README에 데이터 모델링 분석, SQL 개념 분석, 단계별 풀이 및 문제 해결 과정을 상세히 보강했다.

### 2.13 재검증 환경에서 실행 권한과 Git 작성자 설정 복원 — Issue #7

- 증상 1: 작업공간 복원 뒤 스크립트 모드가 `0755`에서 `0644`로 보이며 `Permission denied`가 발생했다.
- 해결 1: Git에 기록된 실행 모드와 같도록 네 스크립트에 실행 권한을 다시 적용한 뒤 전체 검사를 통과했다.
- 증상 2: 새 커밋 직전 로컬 `.git/config`의 작성자 설정이 없어 커밋이 중단됐다.
- 해결 2: 작성자와 커미터를 `giyeop-cody <cody.giyeop@gmail.com>`으로 다시 설정하고 실제 commit metadata를 확인했다.
- 증상 3: 기능 브랜치를 push할 때 로컬 `origin` 정보가 없어 `does not appear to be a git repository` 오류가 발생했다.
- 해결 3: 토큰이 들어가지 않은 공개 HTTPS 원격 주소를 `origin`으로 다시 등록한 뒤 push를 재실행했다.

### 2.14 문서가 SQL과 어긋나기 시작한 지점 전량 처리 — 2026-09-13

- 발견: `bonus_report.md`가 `4_bonus_queries.sql`에 없는 SQL(`order_time BETWEEN '2025-06-03 ...'`)을 설명하고 있었다. KPI 1도 보고서엔 CTE 버전, 파일엔 JOIN 버전으로 SQL 자체가 달랐다.
- 발견: README의 sqlite3 CLI 순서(스키마 → seed → Q1~Q15 → 보너스)로 실행하면 보너스 1이 4행·혼잡도 16.7%가 되는데, 증거는 새 DB 기준(5행·20.8%)이었다. "SQL과 결과 파일의 데이터가 일치해야 함"에 걸리는 종류다.
- 발견: 기본 조회 4개 중 `LIMIT`이 Q01에만 있었다. 루브릭의 "WHERE·ORDER BY·LIMIT 포함"을 좁게 읽으면 감점 항목이다.
- 발견: `store_tables`는 12행 전부 `id == table_number`라 자연키/대리키와 `UNIQUE`의 역할을 데이터로 보여주지 못했다.
- 해결:
  - 보너스·KPI를 Q1~Q15와 같은 연결·같은 순서로 실행하도록 `verify_project.py`를 바꿨다. 이제 문서·증거·수동 실행이 같은 상태를 본다(근거: `decision-log.md` D13).
  - README와 `bonus_report.md`를 현재 SQL 본문으로 다시 썼다.
  - Q02·Q03·Q04에 `LIMIT`을 넣고, 기본 조회 4개가 세 절을 모두 포함하는지 자동 검사로 승격했다.
  - 좌석 번호를 1층 `1xx`·2층 `2xx`로 입력해 `id`와 분리했다. UNIQUE 차단 테스트도 실제 값(`101`)을 쓰도록 고쳤다.
  - 저장소 밖 절대 경로를 문서에서 전부 제거하고, markdown에 그런 경로·끊긴 링크가 있으면 검증이 실패하게 했다.
  - `verify_project.py`에 문서 동기화 검사를 넣어, 같은 종류의 어긋남이 다시 생기면 PASS가 나오지 않는다.

### 2.15 무결성 파괴 테스트를 SQL 스크립트로 이동 — 2026-09-15

- 발견: 보너스 2("일부러 FK 오류 입력을 시도하고 차단 이유 기록")의 위반 SQL 4발이 `scripts/verify_project.py` 안에만 하드코딩되어 있었다. SQL 산출물(`*.sql`)만 검토하는 채점자/리뷰어는 차단 시도의 원문을 찾을 수 없었다.
- 해결: `4_bonus_queries.sql` 끝부분에 `[F01]~[F04]` 섹션으로 위반 INSERT 4발을 옮기고, `verify_project.py`의 `verify_integrity()`가 마커를 파싱해 **파일 본문에서** SQL을 읽어 실행하도록 변경(SSOT 유지). Python 측에는 "어떤 오류로 차단되어야 하는가" 대응표만 남겼다.
- 검증: `scripts/check_all.sh` ALL PASS, `evidence/bonus_02_fk_error_test.txt`와 `evidence/captures/bonus_fk_error.png`가 새 SQL 본문으로 재생성됨.

### 2.16 실행 증거를 SQL 스크립트 주석으로 내장 — 2026-09-15

- 발견: 증거가 `evidence/*.txt`·PNG로 분리돼 있어, SQL 파일만 열면 각 쿼리의 실행 결과가 보이지 않았다. "SQL 스크립트에 실행 증거가 주석으로 포함됐으면 한다"는 검토 의견.
- 해결: `verify_project.py`가 각 쿼리 실행 직후 마커 줄 아래 `-- [증거]` 주석(행 수·결과 표·`rows_affected`·차단 오류·집합 동치·실행 계획)을 재생성해 삽입한다. 기존 증거 주석은 재생성 전 제거하므로 축적되지 않고, 타임스탬프를 배제해 연속 실행이 바이트 단위로 같다.
- 방어: `embed_evidence()`는 파일의 마커 집합과 증거 집합이 일치하는지 assert하므로, 쿼리가 추가·삭제되면 증거 주석 재생성이 실패한다.
- 검증: `scripts/check_all.sh` ALL PASS, 연속 2회 실행 시 SQL 파일 SHA-256 동일.

## 3. 자동 검증 범위

`python scripts/verify_project.py`는 다음을 검사한다.

- 테이블 4개와 각 PK
- seed 행 수 10/12/16/25
- 컬럼 이름·타입 15개, NOT NULL, UNIQUE
- FK 3개 및 `PRAGMA foreign_keys=ON`
- 공식 요구사항에 맞춘 핵심 SQL 범주 분포와 Query 15개 실행
- 결과 텍스트 15개 생성
- 안전 UPDATE/DELETE 영향 행 수
- JOIN/서브쿼리 결과 집합 동치
- KPI 3종 실행
- FK, status CHECK, quantity CHECK, table number UNIQUE 위반 차단
- 인덱스 존재와 현재 실행 계획
- `bonus_report.md`가 인용한 SQL이 `4_bonus_queries.sql` 본문과 문자 단위로 같은지
- README의 Query 설명·증거 링크가 SQL 주석과 실 파일에 대응하는지
- markdown 링크가 실재하고 저장소 밖 경로를 인용하지 않는지
- `evidence/captures` 이미지 16개 존재와 오래된 `evidence/screenshots` 잔존 여부

최종 문구는 `B5-1 AUTOMATED VERIFICATION: ALL PASS`다.

## 4. 전체 재생성 명령

```bash
scripts/check_all.sh
```

이 명령은 검증 → 실행 결과 캡처 → ERD → `git diff --check` 순서로 실행한다.

## 5. 프로젝트 유지보수 및 관리

- 자동 검증 파이프라인(`scripts/check_all.sh`)을 통해 스키마 변경 시 회귀 테스트를 수행한다.
- 검증 통과 후 PR을 통해 main에 안전하게 병합한다.
- learning 브랜치는 학습용 안내 문서를 포함하여 독립적으로 유지한다.
