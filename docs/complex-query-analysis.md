# 복합 쿼리 3개 단계별 분석

이 문서는 현재 `3_queries.sql`의 Query 5, 9, 12를 실제 SQL과 실행 결과에 맞춰 설명한다. 이전 자료에 있던 고객·주문상세 같은 존재하지 않는 도메인은 사용하지 않는다.

## Query 5: INNER JOIN으로 취소 제외 주문 조회

### 목적

주문의 FK 숫자 대신 좌석 번호와 메뉴명을 함께 보여 주되 취소 주문은 제외한다.

### SQL

```sql
SELECT t.table_number, m.name AS menu_name, o.quantity, o.status, o.order_time
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
ORDER BY o.order_time;
```

### 단계

1. `orders o`를 시작점으로 잡는다.
2. `store_tables t`를 연결해 실제 `table_number`를 얻는다.
3. `menus m`을 연결해 메뉴명을 얻는다.
4. `status != 'CANCELLED'`로 취소 주문을 제외한다.
5. 오래된 주문부터 시간순으로 정렬한다.

### 실증 결과

seed 25행 중 취소 상태인 주문 ID 25를 제외한 24행이 반환된다. 실제 결과는 `evidence/query_05_result.txt`에 있다.

## Query 9: GROUP BY로 카테고리별 메뉴 통계

### 목적

카테고리별 메뉴 수와 평균 메뉴 가격을 구한다.

### SQL

```sql
SELECT c.name AS category_name,
       COUNT(m.id) AS menu_count,
       ROUND(AVG(m.price), 0) AS avg_menu_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY menu_count DESC, c.id;
```

### 단계

1. 카테고리와 메뉴를 `category_id`로 연결한다.
2. `GROUP BY c.id, c.name`으로 카테고리별 묶음을 만든다.
3. `COUNT(m.id)`로 메뉴 개수를 센다.
4. `AVG(m.price)`로 평균 가격을 계산하고 반올림한다.
5. 메뉴 수가 많은 카테고리부터 정렬하고, 동률은 카테고리 ID 순으로 정렬한다.

### 실증 결과

10개 카테고리가 반환된다. 메뉴 수가 2개인 카테고리는 6개이고 1개인 카테고리는 4개다. `음료/탄산`은 미주문 검증용 `유자차`를 포함해 2개, 평균 3,500원이다. 전체 값은 `evidence/query_09_result.txt`에 있다.

## Query 12: 서브쿼리로 최고가 메뉴 주문 조회

### 목적

가장 비싼 가격과 같은 모든 메뉴 ID를 먼저 찾고, 그 메뉴가 포함된 주문을 조회한다. 최고가 동률 메뉴가 생겨도 모두 처리할 수 있도록 `=`가 아닌 `IN`을 사용한다.

### SQL

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

### 단계

1. 가장 안쪽 `SELECT MAX(price)`가 최고 가격 32,000원을 찾는다.
2. 중간 서브쿼리가 그 가격과 같은 메뉴 ID를 모두 찾는다.
3. 바깥 쿼리가 해당 메뉴 ID를 가진 주문을 선택한다.
4. 주문 ID 순서로 정렬한다.

### 실증 결과

현재 최고가 메뉴는 ID 1의 `한우 곱창 전골`이다. 이 메뉴를 참조하는 주문 ID 1, 12, 22의 3행이 반환된다. Query 12는 주문 테이블의 6개 컬럼을 그대로 반환하며 실제 값은 `evidence/query_12_result.txt`에 있다.

## 선택과 트레이드오프

| 선택 | 장점 | 단점 | 이번 결정 |
|---|---|---|---|
| 여러 INNER JOIN | 필요한 표시 정보를 한 번에 얻음 | 관계가 늘면 SQL이 길어짐 | Query 5에 사용 |
| `GROUP BY id, name` | ID 기준을 분명히 하고 이름도 출력 가능 | 묶는 컬럼이 늘어남 | Query 9에 사용 |
| 최고가 검색에 `IN` | 최고가 동률 메뉴도 안전하게 처리 | 단일 결과만 확실할 때보다 표현이 길음 | Query 12에 사용 |
| Query 12의 `SELECT *` | 주문 원본 전체를 빠르게 확인 | 스키마가 바뀌면 결과 컬럼도 바뀜 | 과제 조회 예시로만 사용 |

## 재현 방법

```bash
python scripts/verify_project.py
```

이 명령은 새 SQLite DB에서 SQL을 실행하고 위 결과 파일을 다시 만든다.
