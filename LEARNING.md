# B5-1 입문 학습 노트

> 관계형 데이터베이스를 처음 배우는 학생이 현재 프로젝트 SQL을 이해하기 위한 설명이다. 단계별 진행 기록은 `docs/learning-journal.md`, 선택 근거는 `docs/decision-log.md`에서 본다.

## 1. 가장 먼저 알아둘 말

| 말 | 쉬운 뜻 | 이 프로젝트 예 |
|---|---|---|
| DB | 규칙을 가진 데이터 저장소 | 스마트 테이블 오더 DB |
| DBMS | DB를 저장하고 SQL을 실행하는 프로그램 | SQLite |
| 테이블 | 같은 종류의 행을 모은 표 | `menus` |
| 행 | 데이터 한 건 | 유자차 메뉴 한 건 |
| 컬럼 | 행의 항목 | 이름, 가격 |
| PK | 행마다 겹치지 않는 신분증 | `menus.id` |
| FK | 다른 테이블의 PK를 가리키는 번호 | `orders.menu_id` |
| 1:N | 한 행에 여러 행이 연결되는 관계 | 메뉴 1개에 주문 여러 개 |
| 무결성 | 잘못되거나 연결이 끊긴 값을 막는 규칙 | FK, CHECK |
| SQL | DB에 내리는 명령 | SELECT, INSERT |
| JOIN | 연결된 표를 함께 조회 | 주문 + 좌석 + 메뉴 |
| 집계 | 개수·합계·평균 계산 | COUNT, SUM, AVG |
| 인덱스 | 특정 조건을 찾기 위한 별도 찾아보기 | `orders(status)` |

## 2. 엑셀과 관계형 DB

둘 다 표처럼 보이지만 관계형 DB는 테이블 사이의 연결과 입력 규칙을 DB가 검사할 수 있다.

예를 들어 주문마다 `한우 곱창 전골`, `32,000원`을 복사하면 메뉴 정보가 여러 곳에 중복된다. 이 프로젝트는 메뉴를 `menus`에 한 번 저장하고 주문에서는 `menu_id`만 참조한다.

## 3. 네 테이블과 세 관계

```text
menu_categories (1) ──< menus (N)
store_tables    (1) ──< orders (N)
menus           (1) ──< orders (N)
```

- 카테고리 하나에는 메뉴가 여러 개 있을 수 있다.
- 좌석 하나에는 주문 항목이 여러 개 있을 수 있다.
- 메뉴 하나도 여러 주문에 등장할 수 있다.

현재 모델에서 `orders` 한 행은 주문서 전체가 아니라 **메뉴 한 항목**을 뜻한다.

## 4. DDL과 DML

### DDL: 구조를 만든다

```sql
CREATE TABLE menus (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    price       INTEGER NOT NULL CHECK (price >= 0),
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES menu_categories(id)
);
```

- `CREATE TABLE`: 표 만들기
- `DROP TABLE`: 표 없애기
- PK: ID 중복 방지
- NOT NULL: 빈 필수값 방지
- CHECK: 음수 가격 방지
- FK: 없는 카테고리 참조 방지

### DML: 데이터를 다룬다

- `INSERT`: 넣기
- `SELECT`: 읽기
- `UPDATE`: 바꾸기
- `DELETE`: 지우기

```sql
SELECT name, price
FROM menus
WHERE price >= 20000
ORDER BY price DESC
LIMIT 5;
```

뜻: 가격이 20,000원 이상인 메뉴를 비싼 순으로 최대 5개 보여 준다.

## 5. SQLite에서 주의할 점

### FK 켜기

```sql
PRAGMA foreign_keys = ON;
```

SQLite는 연결마다 이 설정을 켜야 FK 위반을 차단한다.

### 날짜와 시간

SQLite에는 별도 DATETIME 저장 클래스가 없다. 이 프로젝트는 다음 ISO 형식 문자열로 통일한다.

```text
2025-06-03 18:05:00
```

같은 형식을 쓰면 시간순 문자열 정렬이 가능하다.

## 6. INNER JOIN과 LEFT JOIN

### INNER JOIN

연결되는 양쪽 행만 남긴다.

```sql
SELECT t.table_number, m.name, o.quantity
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED';
```

### LEFT JOIN

왼쪽 행을 전부 남긴다. 오른쪽 연결이 없으면 오른쪽 컬럼이 NULL이다.

```sql
SELECT m.id, m.name, m.price
FROM menus m
LEFT JOIN orders o ON m.id = o.menu_id
WHERE o.id IS NULL;
```

뜻: 주문과 연결되지 않은 메뉴를 찾는다. 현재 결과는 유자차 1개다.

## 7. GROUP BY와 집계

```sql
SELECT c.name,
       COUNT(m.id) AS menu_count,
       ROUND(AVG(m.price), 0) AS avg_menu_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name;
```

1. 카테고리와 메뉴를 연결한다.
2. 같은 카테고리끼리 묶는다.
3. 메뉴 수와 평균 가격을 계산한다.

- `WHERE`: 묶기 전 각 행을 거른다.
- `HAVING`: 묶은 뒤 집계 결과를 거른다.

## 8. 서브쿼리

SQL 안에 작은 SQL을 넣는다.

```sql
SELECT *
FROM orders
WHERE menu_id IN (
    SELECT id
    FROM menus
    WHERE price = (SELECT MAX(price) FROM menus)
)
ORDER BY id;
```

안쪽에서 최고 가격과 같은 메뉴 ID를 찾고, 바깥에서 해당 메뉴 주문을 찾는다. `IN`을 써서 최고가 동률 메뉴가 여러 개여도 처리한다.

## 9. UPDATE와 DELETE를 안전하게 쓰기

나쁜 예:

```sql
UPDATE orders SET status = 'SERVED' WHERE id = 18;
```

이 SQL은 주문 18의 현재 상태가 무엇인지 확인하지 않는다.

현재 프로젝트:

```sql
UPDATE orders
SET status = 'SERVED'
WHERE id = 18 AND status = 'COOKING';

DELETE FROM orders
WHERE id = 25 AND status = 'CANCELLED';
```

ID와 예상 상태가 모두 맞을 때만 변경한다. 실행 후 영향 행 수도 확인한다.

## 10. 인덱스

```sql
CREATE INDEX IF NOT EXISTS idx_order_status
ON orders (status);
```

status 조건이 자주 쓰여 후보 인덱스를 만들었다. 현재 검증 DB의 실행 계획은 다음과 같다.

```text
SEARCH orders USING INDEX idx_order_status (status=?)
```

주의:

- 인덱스는 저장 공간을 사용한다.
- INSERT/UPDATE/DELETE 때 인덱스도 관리해야 한다.
- 데이터와 통계에 따라 효과가 다르므로 항상 빠르다고 말하지 않는다.

## 11. 잘못된 값이 막히는지 직접 확인

자동 검증에서 다음 입력을 일부러 시도한다.

- 없는 좌석 9999를 참조 → FK 실패
- `status='INVALID'` → CHECK 실패
- `quantity=-1` → CHECK 실패
- 이미 있는 좌석 번호 1 재입력 → UNIQUE 실패

규칙을 DDL에 썼다는 사실만 보지 않고 실제 오류가 나는지 확인한다.

## 12. 정규화는 필요한 만큼만

이번 미션에서는 다음 정도로 이해한다.

- 카테고리는 카테고리 표에 한 번 저장한다.
- 메뉴는 메뉴 표에 한 번 저장한다.
- 주문은 메뉴와 좌석 ID를 참조한다.
- 같은 정보를 여러 행에 복사하지 않아 수정 불일치를 줄인다.

정규화 이론을 지나치게 확장하지 않고 관계가 자연스럽고 질문을 SQL로 풀 수 있는 구조를 목표로 한다.

## 13. ORM과 연결

ORM은 코드의 객체와 관계형 테이블을 연결하고 많은 SQL을 대신 만든다. 하지만 느린 쿼리나 잘못된 관계를 이해하려면 PK, FK, JOIN, GROUP BY를 먼저 알아야 한다. 이 과제에서 백엔드 프레임워크를 쓰지 않는 이유다.

## 14. 현재 구현을 확인하는 순서

```bash
python scripts/verify_project.py
```

그다음 아래 파일을 차례로 읽는다.

1. `1_schema.sql`
2. `2_data.sql`
3. `3_queries.sql`
4. `4_bonus_queries.sql`
5. `evidence/verification_summary.txt`
6. `docs/development-log.md`

성공 기준:

```text
B5-1 AUTOMATED VERIFICATION: ALL PASS
```
