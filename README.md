# B5-1: 미션 정보를 깔끔하게 정리하는 디지털 서랍장 만들기

순수 SQL로 만든 **스마트 테이블 오더 SQLite 데이터베이스**다. 도메인 선택, ERD, DDL, seed, 핵심 SQL 15개, 무결성 실험, 보너스 분석, 실행 증거를 한 저장소에서 재현한다.

## 과제 정보

| 항목 | 내용 |
|---|---|
| 분야 | AI/SW 기초 |
| 구분 | 데이터베이스와 백엔드 |
| 공식 학습 시간 | 40시간 |
| DBMS | SQLite 3 |
| 핵심 테이블 | 4개 |
| 핵심 SQL | 15개 |
| 보너스 SQL | 5개 |
| 제한 | 백엔드 프레임워크·View·프로시저·트리거 미사용 |

## 학습 목표

1. 테이블, 행, 열, PK, FK를 설명한다.
2. ERD를 보고 SQLite DDL을 작성한다.
3. NOT NULL·UNIQUE·FK·CHECK로 잘못된 데이터를 막는다.
4. 기본 조회, JOIN, GROUP BY, 서브쿼리, UPDATE, DELETE, 인덱스를 실행한다.
5. 설명이 아니라 실제 실행 결과로 구현을 검증한다.

## 데이터 모델

| 테이블 | 역할 | seed 행 수 |
|---|---|---:|
| `menu_categories` | 메뉴 카테고리 | 10 |
| `store_tables` | 매장 좌석과 수용 인원 | 12 |
| `menus` | 메뉴명·가격·카테고리 | 16 |
| `orders` | 좌석별 주문 항목·수량·상태·시각 | 25 |

관계는 모두 1:N이다.

- `menu_categories → menus`
- `store_tables → orders`
- `menus → orders`

![스마트 테이블 오더 ERD](erd_diagram.png)

상세 설계: [`architecture_design.md`](architecture_design.md)

## 파일 구성

```text
.
├── 1_schema.sql                 # 4개 테이블과 제약조건
├── 2_data.sql                   # 10/12/16/25행 seed
├── 3_queries.sql                # 핵심 Query 1~15
├── 4_bonus_queries.sql          # 동치 비교 2개 + KPI 3개
├── QUEST.md                     # 공식 PDF 기준 요구사항 정리
├── architecture_design.md       # 데이터 모델·스키마 설명
├── bonus_report.md              # 보너스 SQL과 실제 결과 분석
├── erd_diagram.png              # 현재 스키마 ERD
├── requirements-dev.txt         # 증거 이미지 생성 의존성
├── docs/
│   ├── complex-query-analysis.md
│   ├── development-log.md
│   ├── learning-journal.md
│   ├── decision-log.md
│   └── issue-handling-log.md
├── scripts/
│   ├── verify_project.py
│   ├── generate_screenshots.py
│   ├── generate_erd.py
│   └── check_all.sh
└── evidence/
    ├── query_01_result.txt ~ query_15_result.txt
    ├── bonus_01_compare_methods.txt
    ├── bonus_02_fk_error_test.txt
    ├── bonus_03_kpi_metrics.txt
    ├── verification_summary.txt
    └── screenshots/
        ├── query_01.png ~ query_15.png
        └── bonus_fk_error.png
```

## 가장 빠른 검증

Python 3만 있으면 핵심 검증을 실행할 수 있다.

```bash
python scripts/verify_project.py
```

성공 시 마지막에 다음 문구가 나온다.

```text
B5-1 AUTOMATED VERIFICATION: ALL PASS
```

이미지와 ERD까지 모두 다시 만들려면 Pillow를 설치하고 전체 검사를 실행한다.

```bash
python -m pip install -r requirements-dev.txt
scripts/check_all.sh
```

`check_all.sh`는 새 DB 검증 → 결과 이미지 → ERD → `git diff --check` 순서로 실행한다.

## SQLite CLI로 수동 실행

항상 새 DB에서 파일명 순서대로 실행한다.

```bash
rm -f table_order.db
sqlite3 table_order.db < 1_schema.sql
sqlite3 table_order.db < 2_data.sql
sqlite3 -header -column table_order.db < 3_queries.sql
sqlite3 -header -column table_order.db < 4_bonus_queries.sql
```

주의:

- `PRAGMA foreign_keys = ON`은 **SQLite 연결마다** 켜야 한다.
- SQLite에는 별도 DATETIME 저장 클래스가 없다. 이 프로젝트는 `order_time`에 `YYYY-MM-DD HH:MM:SS` 문자열을 일관되게 넣는다.
- `3_queries.sql`에는 UPDATE와 DELETE가 있으므로 실행 전 DB를 새로 만드는 것이 재현에 안전하다.

## 핵심 Query 15개

| 번호 | 범주 | 질문 | 결과 증거 |
|---:|---|---|---|
| 1 | 기본 조회 | 20,000원 이상 메뉴 상위 5개 | [`txt`](evidence/query_01_result.txt) · [`png`](evidence/screenshots/query_01.png) |
| 2 | 기본 조회 | 이름에 전골 또는 철판이 있는 메뉴 | [`txt`](evidence/query_02_result.txt) · [`png`](evidence/screenshots/query_02.png) |
| 3 | 기본 조회 | 현재 COOKING 주문 | [`txt`](evidence/query_03_result.txt) · [`png`](evidence/screenshots/query_03.png) |
| 4 | 기본 조회 | 6명 이상 좌석 | [`txt`](evidence/query_04_result.txt) · [`png`](evidence/screenshots/query_04.png) |
| 5 | INNER JOIN | 취소 제외 주문과 좌석·메뉴 | [`txt`](evidence/query_05_result.txt) · [`png`](evidence/screenshots/query_05.png) |
| 6 | INNER JOIN | 주류 카테고리 3종 메뉴 | [`txt`](evidence/query_06_result.txt) · [`png`](evidence/screenshots/query_06.png) |
| 7 | LEFT JOIN | 주문 이력이 없는 메뉴 | [`txt`](evidence/query_07_result.txt) · [`png`](evidence/screenshots/query_07.png) |
| 8 | LEFT JOIN | 주문 이력이 없는 좌석 | [`txt`](evidence/query_08_result.txt) · [`png`](evidence/screenshots/query_08.png) |
| 9 | 집계 | 카테고리별 메뉴 수·평균 단가 | [`txt`](evidence/query_09_result.txt) · [`png`](evidence/screenshots/query_09.png) |
| 10 | 집계 | 좌석별 취소 제외 주문 금액 | [`txt`](evidence/query_10_result.txt) · [`png`](evidence/screenshots/query_10.png) |
| 11 | 집계 | SERVED 판매 수량 3개 이상 메뉴 | [`txt`](evidence/query_11_result.txt) · [`png`](evidence/screenshots/query_11.png) |
| 12 | 서브쿼리 | 최고가와 같은 메뉴의 주문 | [`txt`](evidence/query_12_result.txt) · [`png`](evidence/screenshots/query_12.png) |
| 13 | 수정 | COOKING인 18번 주문만 SERVED 변경 | [`txt`](evidence/query_13_result.txt) · [`png`](evidence/screenshots/query_13.png) |
| 14 | 삭제 | CANCELLED인 25번 주문만 삭제 | [`txt`](evidence/query_14_result.txt) · [`png`](evidence/screenshots/query_14.png) |
| 15 | 인덱스 | `orders(status)` 후보 인덱스 생성 | [`txt`](evidence/query_15_result.txt) · [`png`](evidence/screenshots/query_15.png) |

Query 13과 14는 ID만 확인하지 않고 예상 현재 상태도 함께 확인한다.

```sql
WHERE id = 18 AND status = 'COOKING'
WHERE id = 25 AND status = 'CANCELLED'
```

## 무결성 규칙과 실증

| 규칙 | 막는 잘못된 입력 | 자동 검증 결과 |
|---|---|---|
| PK | 중복 ID | PASS |
| NOT NULL | 필수값 누락 | 스키마 검사 PASS |
| UNIQUE | 중복 카테고리명·좌석 번호 | 중복 좌석 번호 차단 PASS |
| FK 3개 | 없는 카테고리·좌석·메뉴 참조 | 없는 좌석 참조 차단 PASS |
| CHECK | 음수 가격·좌석 번호·수용 인원·수량 | 음수 수량 차단 PASS |
| CHECK | COOKING/SERVED/CANCELLED 외 상태 | 잘못된 상태 차단 PASS |

![FK 무결성 오류 실증](evidence/screenshots/bonus_fk_error.png)

## 보너스 결과

1. **JOIN과 서브쿼리 비교**: 같은 질문을 두 방식으로 실행하고 5개 행의 값까지 비교해 집합 동치 PASS
2. **무결성 깨뜨리기**: FK·CHECK·UNIQUE 위반이 실제로 차단되는지 확인
3. **KPI 3종**:
   - 카테고리별 매출 비중 10행
   - 좌석 수용 인원별 물리 테이블당 평균 매출 4행
   - 주방 혼잡도 20.8%

`EXPLAIN QUERY PLAN`은 현재 seed와 SQLite 실행 계획만 설명한다. 특정 방식이 언제나 더 빠르다고 단정하지 않는다.

상세 결과: [`bonus_report.md`](bonus_report.md)

## 컬럼 타입을 이렇게 고른 이유

| 값 | SQLite 선언 | 이유 |
|---|---|---|
| ID·가격·수량·수용 인원 | INTEGER | 원화와 개수는 정수로 계산 |
| 이름·상태 | TEXT | 사람이 읽는 문자열 |
| 주문 시각 | DATETIME 선언 | ISO 형식 문자열을 일관되게 저장하기 위한 의도 표시 |

SQLite의 타입 선언은 다른 DBMS보다 유연하므로, 올바른 값 범위는 CHECK와 일관된 입력 형식으로 보완한다.

## INNER JOIN과 LEFT JOIN

- `INNER JOIN`: 양쪽에 연결되는 행만 반환한다. Query 5·6에서 사용한다.
- `LEFT JOIN`: 왼쪽 행은 모두 남기고 오른쪽에 연결이 없으면 NULL로 둔다. Query 7·8에서 `WHERE 오른쪽.id IS NULL`과 함께 미매칭 행을 찾는다.

현재 seed에서:

- Query 7: 미주문 메뉴 `유자차` 1개
- Query 8: 미주문 좌석 2번, 11번, 12번 3개

## 정규화와 PK/FK

- 카테고리명은 `menu_categories` 한 곳에 저장한다.
- 좌석 정보는 `store_tables` 한 곳에 저장한다.
- 주문에는 메뉴명·좌석 번호를 복사하지 않고 FK를 저장한다.
- PK는 한 행의 고유한 신분증이고, FK는 다른 테이블 행을 가리키는 연결 번호다.

이 구조는 중복 수정을 줄이고 존재하지 않는 부모를 참조하는 실수를 막는다.

## 검증된 현재 결과

- 테이블: 4개
- seed: 10/12/16/25행
- PK: 모든 테이블 PASS
- FK: 3개, 1:N 관계 3개 PASS
- 핵심 SQL: 15개 모두 실행 PASS
- 보너스 SQL: 5개 모두 실행 PASS
- 자동 검증: `B5-1 AUTOMATED VERIFICATION: ALL PASS`

검증 요약 원본: [`evidence/verification_summary.txt`](evidence/verification_summary.txt)

## 데이터베이스 모델링 및 설계 분석

### 1. 테이블 분리 및 역할

- `menu_categories`: 메뉴 분류 이름을 한 곳에서 관리한다.
- `store_tables`: 실제 좌석 번호와 수용 인원을 관리한다.
- `menus`: 메뉴명·가격과 소속 카테고리를 관리한다.
- `orders`: 어느 좌석이 어떤 메뉴를 몇 개 주문했고 현재 상태가 무엇인지 기록한다.

한 주문마다 카테고리명·메뉴명·좌석 번호를 복사하면 같은 값이 여러 곳에 중복 저장된다. 값을 한 테이블에 한 번만 저장하고 주문은 ID로 참조하면 데이터 중복과 수정 불일치(Update Anomaly)를 원천적으로 방지할 수 있다.

### 2. 1:N 외래키(FK) 관계와 데이터 무결성

- `menu_categories → menus` (카테고리 1 : N 메뉴): 카테고리 하나에 여러 메뉴가 속한다. 예: 메뉴 ID 1 `한우 곱창 전골`의 `category_id=2`는 카테고리 ID 2 `탕/전골 요리`를 가리킨다.
- `store_tables → orders` (좌석 1 : N 주문): 특정 좌석에서 여러 번 주문할 수 있다. 예: 주문 ID 1의 `table_id=3`은 3번 좌석을 가리킨다.
- `menus → orders` (메뉴 1 : N 주문): 특정 메뉴가 여러 테이블/주문에서 반복 주문될 수 있다. 예: 주문 ID 1의 `menu_id=1`은 한우 곱창 전골을 가리킨다.

외래키 제약조건(`PRAGMA foreign_keys = ON`)을 통해 부모 테이블에 존재하지 않는 좌석 ID나 메뉴 ID를 참조하는 잘못된 주문 입력을 엔진 레벨에서 차단한다.

### 3. 데이터 타입 및 제약조건 선택 근거

| 컬럼 종류 | 타입 | 선택 이유 및 제약조건 |
|---|---|---|
| ID, 가격, 수량, 좌석 번호, 수용 인원 | `INTEGER` | 원화와 개수는 소수점이 필요 없으며 정수형 연산과 대소 비교가 정확하다. `CHECK (price >= 0)`, `CHECK (quantity > 0)` 등을 적용해 유효 범위를 보장한다. |
| 이름, 상태 | `TEXT` | 사람이 읽는 문자열이다. 카테고리명과 좌석 번호에는 `UNIQUE`를 적용해 중복을 방지하며, 상태는 `CHECK (status IN ('COOKING','SERVED','CANCELLED'))`로 도메인 유효값을 엄격히 제한한다. |
| 주문 시각 | `DATETIME` 선언 | 저장 의도를 명확히 드러낸다. SQLite는 ISO-8601 문자열(`YYYY-MM-DD HH:MM:SS`)을 일관되게 사용하여 날짜 비교와 `strftime` 함수를 온전히 활용한다. |

### 4. 단일 진실 공급원(SSOT)과 ID 참조

관계의 방향은 "기준이 되는 부모 Entity → 그 기준을 사용하는 자식 Transaction"으로 설계했다. 주문 테이블에 `한우 곱창 전골`이라는 텍스트를 중복 저장하지 않고 `menu_id=1`로 참조하는 이유는 메뉴의 가격 인상이나 명칭 변경 시 원천 테이블(`menus`)만 수정하면 되기 때문이다.

---

## 핵심 SQL 구현 및 쿼리 개념 분석

### 1. 관계형 데이터베이스와 스프레드시트의 차이

엑셀 스프레드시트는 자유로운 2차원 장부이지만 데이터 중복, 관계 강제, 동시성 제어에 취약하다. 관계형 데이터베이스는 용도와 도메인 규칙에 따라 테이블을 나누어 저장하고, Primary Key와 Foreign Key를 통해 데이터 간의 관계를 엔진 레벨에서 강제함으로써 무결성을 보장한다.

### 2. Primary Key와 Foreign Key의 역할

- **Primary Key (PK):** 테이블 내에서 각 행(Row)을 유일하게 식별하는 고유 식별자다.
- **Foreign Key (FK):** 다른 테이블의 PK를 참조하여 테이블 간의 관계를 정의하고, 고아 데이터(Orphan Record) 발생을 차단한다.

### 3. INNER JOIN vs LEFT JOIN 동작 분석

- **INNER JOIN:** 양쪽 테이블에 모두 조건이 매칭되는 행만 반환한다. (예: Q05 — 취소되지 않고 좌석·메뉴와 정상 연결되는 주문 24행 조회)
- **LEFT JOIN:** 왼쪽 테이블의 모든 행을 보존하고, 매칭되는 오른쪽 테이블 데이터가 없으면 NULL로 반환한다. (예: Q07 — 전체 메뉴를 왼쪽에 두고 주문 연결이 NULL인 미주문 메뉴 `유자차` 1건 탐색, Q08 — 주문 이력이 없는 좌석 2·11·12번 탐색)

### 4. GROUP BY 집계와 HAVING 필터링

`GROUP BY`는 특정 컬럼을 기준으로 데이터를 그룹화하며, 집계 함수(`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)는 각 그룹별 요약 통계를 산출한다.

- **Q09:** 카테고리 10개 그룹을 생성하고 `COUNT`로 메뉴 수, `AVG`로 평균 단가를 계산한다.
- **Q10:** 주문이 존재하는 좌석 9개 그룹을 만들고 `SUM(price × quantity)`로 좌석별 총 주문 금액을 집계한다.
- **Q11:** `WHERE status = 'SERVED'`로 서빙 완료된 행을 먼저 필터링한 뒤, `GROUP BY`로 묶인 결과에 대해 `HAVING SUM(quantity) >= 3`으로 총 판매 수량이 3개 이상인 메뉴만 추출한다.

---

## 복잡 쿼리 단계별 설계 및 트러블슈팅

### 1. 복잡 쿼리 단계별 설계 (보너스 KPI 2)

좌석 수용 인원별 물리 테이블당 평균 매출 산출 쿼리 설계 과정:

1. `table_revenue` CTE에서 모든 물리 좌석(`store_tables`)을 기준 집합으로 설정한다.
2. 주문과 메뉴를 `LEFT JOIN`하여 주문이 없는 좌석도 0원으로 보존한다.
3. `CASE WHEN status <> 'CANCELLED'`를 적용해 취소 주문을 매출에서 제외한다.
4. 먼저 `store_tables.id`별로 매출을 합산하여 12개 물리 테이블 각각의 단일 매출 행을 생성한다.
5. 외부 메인 쿼리에서 `capacity`(2/4/6/8인석) 기준으로 다시 그룹화한다.
6. `COUNT(*)`로 해당 크기의 물리 좌석 수, `AVG(revenue)`로 좌석당 평균 매출을 계산한다.
7. 산출 결과: 2인석 13,667원, 4인석 30,333원, 6인석 51,500원, 8인석 138,000원으로 수용 인원별 비례적 매출 증가 양상을 정확히 도출했다.

### 2. 문제 해결 및 검증 자동화 트러블슈팅

SQL 파일, 설명 문서, 결과 스크린샷이 서로 다른 시점의 DB 상태를 가리켜 메뉴명과 수치가 불일치하는 문제를 해결하기 위해:

1. `verify_project.py`가 매 실행 시 clean SQLite 메모리/파일 DB를 새로 생성하여 Q01~Q15 및 보너스 쿼리를 순차 실행하도록 통합했다.
2. 쿼리 실행 결과를 텍스트 파일(`evidence/query_*.txt`)로 저장하고, `generate_screenshots.py`가 해당 텍스트로부터 스크린샷 PNG를 자동 렌더링하도록 일원화했다.
3. 전체 검사를 연속 실행하여 텍스트·PNG·ERD의 SHA-256 해시 일관성을 확보했다.
4. 잘못된 status 및 음수 quantity 입력을 방지하기 위해 CHECK 제약조건을 보강하고 무결성 차단 테스트를 추가했다.

---

## 보너스 과제 분석 요약

| 보너스 항목 | 구현 내용 및 결과 |
|---|---|
| **JOIN vs 서브쿼리 동일 요구 해결** | 특정 시간대 주문된 메뉴 목록 조회를 JOIN(DISTINCT 적용)과 IN 서브쿼리 두 가지 방식으로 구현. 5개 행의 반환 데이터가 100% 동치임을 자동 검증. |
| **무결성 제약조건 강제 테스트** | 부모 없는 FK 참조(`table_id=99`), 잘못된 status, 음수 quantity, 중복 table_number 입력을 시도하여 모두 성공적으로 차단됨을 확인. |
| **핵심 비즈니스 KPI 3종 도출** | (1) 카테고리별 매출 비중, (2) 수용인원별 테이블당 평균 매출, (3) 실시간 주방 혼잡도(조리 중 비율 20.8%) 산출 쿼리 완료. |

상세 SQL과 실행 결과는 [`bonus_report.md`](bonus_report.md) 및 `evidence/bonus_*.txt`에서 확인할 수 있다.

---

## 프로젝트 종합 검증 실행

```bash
scripts/check_all.sh
```

주요 자동 검증 출력:

```text
tables=4 PASS: menu_categories, menus, orders, store_tables
menu_categories rows=10 PASS
store_tables rows=12 PASS
menus rows=16 PASS
orders rows=25 PASS
column_names_and_types=15 PASS
NOT_NULL_columns=11 PASS
UNIQUE_indexes=2 PASS
foreign_keys=3 PASS
PRAGMA foreign_keys=ON PASS
core_queries=15 PASS
query_numbers_and_descriptions=15 PASS
query_distribution=basic:4,join:4,aggregate:3,subquery:1,mutation:2,index:1 PASS
core_text_evidence=15 PASS
screenshots=16 PASS
B5-1 AUTOMATED VERIFICATION: ALL PASS
B5-1 CHECK ALL: PASS
```

## 기술 및 학습 기록 문서

- 복합 쿼리 상세 분석: [`docs/complex-query-analysis.md`](docs/complex-query-analysis.md)
- 개발 및 트러블슈팅 기록: [`docs/development-log.md`](docs/development-log.md)
- 단계별 학습 일지: [`docs/learning-journal.md`](docs/learning-journal.md)
- 의사결정 기록: [`docs/decision-log.md`](docs/decision-log.md)
- 이슈 처리 기록: [`docs/issue-handling-log.md`](docs/issue-handling-log.md)
- Git 이력 관리 기록: [`docs/history-rewrite.md`](docs/history-rewrite.md)
- Commit SHA 매핑: [`docs/email-rewrite-map.tsv`](docs/email-rewrite-map.tsv)
- 프로젝트 최종 검증 기록: [`docs/final-audit-verification.md`](docs/final-audit-verification.md)
