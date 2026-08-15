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
│   ├── issue-handling-log.md
│   └── peer-evaluation-request.md
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

## 첨부 평가표 기준 재검증과 답변

아래는 제공된 **평가항목 1~5**를 현재 과제에 맞춰 다시 확인한 결과다. `PASS`는 외부 평가자의 점수를 대신 적은 것이 아니라, 저장소와 SQLite 실행 결과를 대조한 **자체 재검증 판정**이다.

### 평가 1 — 필수 산출물과 수량

**질문 의도:** 파일이 있다는 사실만 보는 것이 아니라, 과제의 최소 구조·SQL 범주·결과 증거가 빠짐없이 실제로 연결되는지 확인한다.

| 평가 항목 | 이 과제의 답과 근거 | 자체 판정 |
|---|---|---:|
| 최소 4개 이상의 테이블이 존재하고 각 테이블에 PK가 정의되어 있는가? | `menu_categories`, `store_tables`, `menus`, `orders` 4개이며 모두 `id INTEGER PRIMARY KEY`가 있다. `PRAGMA table_info` 자동 검사도 4개 모두 PASS다. | PASS |
| FK를 사용한 1:N 관계가 최소 2개 이상 존재하며 각 관계가 명확한가? | `menu_categories → menus`, `store_tables → orders`, `menus → orders`의 3개 관계가 있다. 자식의 `category_id`, `table_id`, `menu_id`가 부모 PK를 참조한다. | PASS |
| 각 테이블에 최소 10행 이상의 샘플 데이터가 입력되어 있는가? | 실제 COUNT는 카테고리 10, 좌석 12, 메뉴 16, 주문 25행이다. | PASS |
| 기본 조회 4개, 조인 4개, 집계 3개, 서브쿼리 1개, 수정·삭제 2개, 인덱스 1개를 포함한 총 15개 쿼리가 있는가? | Q1~Q15의 자동 분포 검사는 `basic:4, join:4, aggregate:3, subquery:1, mutation:2, index:1 PASS`다. JOIN은 INNER 2개와 LEFT 2개다. | PASS |
| 각 쿼리 실행 결과가 스크린샷 또는 텍스트로 첨부되어 있는가? | `evidence/query_01_result.txt`~`query_15_result.txt`와 대응 PNG 15개가 있다. 같은 자동 실행에서 텍스트를 만들고 그 텍스트로 PNG를 만든다. | PASS |

**말로 답한다면:** “테이블은 4개이고 모두 PK가 있습니다. FK 관계는 최소 2개보다 많은 3개입니다. 각 테이블은 10행 이상이고, 필수 범주에 맞춘 Q1~Q15와 각 결과 텍스트·PNG가 있습니다.”

### 평가 2 — 모델링 선택을 설명하는 능력

**질문 의도:** 남이 만든 DDL을 실행만 한 것이 아니라, 왜 테이블을 나눴고 왜 그 이름·타입·관계를 선택했는지 설명할 수 있는지 확인한다.

#### 2-1. 테이블을 왜 이렇게 나눴고, 각 테이블의 역할은 무엇인가?

- `menu_categories`: 메뉴 분류 이름을 한 곳에서 관리한다.
- `store_tables`: 실제 좌석 번호와 수용 인원을 관리한다.
- `menus`: 메뉴명·가격과 소속 카테고리를 관리한다.
- `orders`: 어느 좌석이 어떤 메뉴를 몇 개 주문했고 현재 상태가 무엇인지 기록한다.

한 주문마다 카테고리명·메뉴명·좌석 번호를 복사하면 같은 값이 여러 곳에 생긴다. 값을 한 테이블에 한 번만 저장하고 주문은 ID로 참조하면 중복과 수정 불일치를 줄일 수 있다.

#### 2-2. FK로 연결된 1:N 관계가 실제 데이터에서 어떤 의미인지 예를 들 수 있는가?

- 메뉴 ID 1 `한우 곱창 전골`의 `category_id=2`는 카테고리 ID 2 `탕/전골 요리`를 가리킨다. 카테고리 하나에 여러 메뉴가 속할 수 있다.
- 주문 ID 1의 `table_id=3`은 3번 좌석을, `menu_id=1`은 한우 곱창 전골을 가리킨다.
- 같은 좌석이나 메뉴 ID가 여러 주문 행에 반복될 수 있으므로 부모 1개와 자식 여러 개의 1:N 관계다.

FK가 있기 때문에 존재하지 않는 좌석이나 메뉴 ID로 주문을 만들면 `FOREIGN KEY constraint failed`로 차단된다.

#### 2-3. 컬럼 타입을 왜 그렇게 선택했는가?

| 컬럼 종류 | 타입 | 선택 이유 |
|---|---|---|
| ID, 가격, 수량, 좌석 번호, 수용 인원 | `INTEGER` | 원화와 개수는 소수점이 필요 없고 비교·합계 계산이 분명하다. |
| 이름, 상태 | `TEXT` | 사람이 읽는 문자열이다. 상태는 CHECK로 허용값을 제한한다. |
| 주문 시각 | `DATETIME` 선언 | 저장 의도를 드러낸다. SQLite에는 별도 DATETIME 저장 클래스가 없으므로 ISO 문자열 형식을 일관되게 사용한다. |

자동 검증은 현재 15개 컬럼의 이름과 선언 타입이 설계값과 같은지 확인한다.

#### 2-4. 관계 방향과 ID 컬럼이 하나의 도메인 값을 대표하는 이유는 무엇인가?

관계의 방향은 “기준이 되는 부모 → 그 기준을 사용하는 자식”으로 잡았다. 주문에 `한우 곱창 전골`이라는 글자를 다시 쓰지 않고 `menu_id=1`을 쓰는 이유는 메뉴 ID 1이 `menus`의 한 행을 유일하게 가리키기 때문이다. 메뉴명과 가격의 원본은 `menus` 한 곳에 남고 주문은 그 원본을 참조한다. 좌석과 카테고리도 같은 원리다.

**자체 판정:** 평가 2의 네 질문 모두 현재 DDL·seed·ERD의 실제 예로 설명할 수 있으므로 PASS다.

### 평가 3 — 관계형 DB와 SQL 개념 이해

**질문 의도:** 외운 정의가 아니라 자신의 말과 실제 Query 결과를 이용해 관계형 DB, 키, JOIN, 집계를 설명할 수 있는지 확인한다.

#### 3-1. DB는 엑셀과 무엇이 다르고 왜 테이블을 나눠 저장하는가?

엑셀을 한 장의 자유로운 장부라고 하면 관계형 DB는 **서랍마다 용도와 연결 규칙이 있는 서랍장**이다. 주문 장부에 메뉴명과 가격을 매번 복사하면 메뉴명이 바뀔 때 여러 행을 고쳐야 한다. 메뉴 서랍에는 메뉴를 한 번만 저장하고 주문 서랍은 메뉴 ID로 연결하면 한 곳이 원본이 되고 DB가 잘못된 연결도 막아 준다.

#### 3-2. PK와 FK의 역할, 1:N 관계를 자신의 말로 설명할 수 있는가?

PK는 한 서랍 안에서 카드 한 장을 찾는 겹치지 않는 번호다. FK는 다른 서랍의 카드 번호를 적은 연결표다. 카테고리 ID 2 하나를 여러 메뉴가 FK로 가리킬 수 있으므로 카테고리 1개 대 메뉴 여러 개, 즉 1:N이다.

#### 3-3. INNER JOIN과 LEFT JOIN의 차이를 실행 결과로 설명할 수 있는가?

- INNER JOIN은 양쪽에 연결된 행만 남긴다. Q5는 취소되지 않고 좌석·메뉴와 연결되는 주문 24행을 보여 준다.
- LEFT JOIN은 왼쪽 행을 먼저 모두 남긴다. Q7은 전체 메뉴를 왼쪽에 두고 주문 연결이 NULL인 `유자차` 1개를 찾는다. Q8도 같은 방식으로 주문 이력이 없는 좌석 2·11·12번을 찾는다.

#### 3-4. GROUP BY와 COUNT·SUM·AVG는 어떻게 동작하는가?

`GROUP BY`는 같은 기준의 행을 바구니처럼 묶고 집계 함수는 각 바구니를 계산한다.

- Q9: 카테고리 10개 그룹을 만들고 `COUNT`로 메뉴 수, `AVG`로 평균 단가를 구한다.
- Q10: 주문이 있는 좌석 9개 그룹을 만들고 `SUM(price × quantity)`로 좌석별 금액을 구한다.
- Q11: 메뉴별 SERVED 수량을 합친 뒤 `HAVING`으로 합계 3 이상인 메뉴 2개만 남긴다.

**자체 판정:** 실제 결과 행 수와 값을 근거로 네 개념을 설명할 수 있으므로 PASS다.

### 평가 4 — 복잡한 문제 해결과 트러블슈팅

**질문 의도:** 완성된 코드만 제시하는 것이 아니라, 복잡한 요구를 작은 단계로 나누고 문제의 재현·원인·해결·재검증 과정을 설명할 수 있는지 확인한다.

#### 4-1. 가장 복잡했던 쿼리 하나를 어떻게 단계별로 풀었는가?

가장 복잡했던 쿼리로 **보너스 KPI 2: 좌석 수용 인원별 물리 테이블당 평균 매출**을 선택한다.

1. `table_revenue` CTE에서 모든 물리 좌석을 시작점으로 잡는다.
2. 주문과 메뉴를 LEFT JOIN해 주문이 없는 좌석도 남긴다.
3. `CASE WHEN status <> 'CANCELLED'`로 취소 주문을 매출에서 제외한다.
4. 먼저 `store_tables.id`별 매출을 합쳐 좌석 하나당 한 행을 만든다.
5. 바깥 쿼리에서 같은 `capacity`끼리 다시 묶는다.
6. `COUNT(*)`로 물리 좌석 수, `AVG(revenue)`로 좌석당 평균 매출을 계산한다.
7. 결과는 2·4·6·8인석의 4개 그룹이며 평균은 13,667원·30,333원·51,500원·138,000원이다.

주문 행을 바로 수용 인원별로 평균 내면 주문이 많은 좌석이 여러 번 반영된다. 그래서 좌석별 합계를 먼저 만든 뒤 평균을 내는 두 단계 방식을 선택했다.

#### 4-2. 미션 수행 중 가장 어려웠던 부분과 해결 방법은 무엇인가?

가장 어려웠던 부분은 **SQL·문서·스크린샷이 서로 다른 실행 시점의 결과를 보여 준 문제**였다.

1. 현재 Q1/Q5/Q9/Q12와 기존 PNG의 메뉴명·수치가 다름을 재현했다.
2. 사람이 각 화면을 따로 저장한 것이 원인임을 확인했다.
3. `verify_project.py`가 새 DB 한 개에서 Q1~Q15를 순서대로 실행하도록 만들었다.
4. SQL과 결과를 텍스트로 저장하고, `generate_screenshots.py`가 바로 그 텍스트를 PNG로 바꾸게 했다.
5. 전체 검사를 연속 두 번 실행해 텍스트·PNG·ERD의 SHA-256이 같음을 확인했다.

이 과정에서 잘못된 status와 음수 quantity가 허용되는 문제도 발견해 CHECK를 추가하고 실패 입력이 실제로 차단되는지 재검증했다.

**자체 판정:** 단계별 쿼리 풀이와 구체적인 트러블슈팅을 실행 증거로 설명할 수 있으므로 PASS다.

### 평가 5 — 보너스 문제

**질문 의도:** 필수 수량을 넘어서 같은 문제의 다른 풀이, 무결성 실패 실험, 실제 지표 설계까지 수행했는지 확인한다.

| 보너스 항목 | 구현과 결과 | 자체 판정 |
|---|---|---:|
| 같은 요구를 JOIN과 서브쿼리로 풀기 | 두 방법 모두 같은 5개 메뉴를 반환하며 전체 행 값 동치 PASS다. | PASS |
| 데이터 정합성을 일부러 깨뜨리기 | 없는 FK, 잘못된 status, 음수 quantity, 중복 table number가 모두 차단된다. | PASS |
| 핵심 지표 3개 만들기 | 카테고리 매출 비중, 물리 테이블당 평균 매출, 주방 혼잡도 SQL과 결과가 있다. | PASS |

상세 SQL과 결과는 [`bonus_report.md`](bonus_report.md) 및 `evidence/bonus_*.txt`에서 확인한다.

### 평가표 재검증 명령

```bash
scripts/check_all.sh
```

평가표와 직접 연결되는 자동 확인 문구:

```text
column_names_and_types=15 PASS
NOT_NULL_columns=11 PASS
UNIQUE_indexes=2 PASS
foreign_keys=3 PASS
rubric_query_numbers_and_descriptions=15 PASS
rubric_query_distribution=basic:4,join:4,aggregate:3,subquery:1,mutation:2,index:1 PASS
core_text_evidence=15 PASS
screenshots=16 PASS
```

## 학습·선택·문제 기록

- 복합 쿼리 학습: [`docs/complex-query-analysis.md`](docs/complex-query-analysis.md)
- 개발·트러블슈팅: [`docs/development-log.md`](docs/development-log.md)
- 단계별 학습 일지: [`docs/learning-journal.md`](docs/learning-journal.md)
- 선택지와 트레이드오프: [`docs/decision-log.md`](docs/decision-log.md)
- GitHub Issue 처리: [`docs/issue-handling-log.md`](docs/issue-handling-log.md)
- Git 이메일 rewrite 기록: [`docs/history-rewrite.md`](docs/history-rewrite.md)
- old→new commit SHA 전체 매핑: [`docs/email-rewrite-map.tsv`](docs/email-rewrite-map.tsv)
- 감사 지적 최종 처리: [`docs/final-audit-verification.md`](docs/final-audit-verification.md)
- 외부 동료평가 요청서: [`docs/peer-evaluation-request.md`](docs/peer-evaluation-request.md)

외부 동료평가 결과는 평가자가 직접 검증한 뒤 기록한다. 구현자가 실제 평가를 받은 것처럼 임의 작성하지 않는다.
