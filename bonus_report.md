# B5-1 보너스 과제 실증 보고서

보너스도 이번 수정 범위에 포함했다. 실행 SQL은 `4_bonus_queries.sql`, 실제 결과는 `evidence/bonus_*.txt`에 있다.

## 1. 같은 질문을 JOIN과 서브쿼리로 해결

### 질문

2025-06-03 18:00:00부터 20:00:00까지 주문된 메뉴의 중복 없는 목록은 무엇인가?

### JOIN 방식

```sql
SELECT DISTINCT m.id, m.name, m.price
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.order_time BETWEEN '2025-06-03 18:00:00' AND '2025-06-03 20:00:00'
ORDER BY m.id;
```

### 서브쿼리 방식

```sql
SELECT m.id, m.name, m.price
FROM menus m
WHERE m.id IN (
    SELECT o.menu_id
    FROM orders o
    WHERE o.order_time BETWEEN '2025-06-03 18:00:00' AND '2025-06-03 20:00:00'
)
ORDER BY m.id;
```

### 실제 동치 검증

두 결과를 `[(id, name, price), ...]` 튜플 목록으로 만든 뒤 정렬하여 비교했다.

- JOIN 결과: 5행
- 서브쿼리 결과: 5행
- 집합 비교: PASS
- 메뉴 ID: 1, 4, 5, 9, 10

따라서 **현재 질문과 데이터에서는 실제 결과 집합이 같다.** 단지 행 수만 같은 것이 아니라 각 행의 값까지 비교했다.

## 2. EXPLAIN QUERY PLAN 범위의 성능 설명

현재 검증 DB에서 저장한 계획은 다음과 같다.

```text
JOIN:
SCAN o
SEARCH m USING INTEGER PRIMARY KEY (rowid=?)
USE TEMP B-TREE FOR DISTINCT
USE TEMP B-TREE FOR ORDER BY

SUBQUERY:
SEARCH m USING INTEGER PRIMARY KEY (rowid=?)
LIST SUBQUERY 1
SCAN o
```

해석:

- JOIN 방식은 `orders`를 읽고 PK로 `menus`를 찾으며 DISTINCT와 정렬용 임시 B-Tree를 사용했다.
- 서브쿼리 방식은 먼저 주문의 메뉴 ID 목록을 만들고 `menus`의 PK를 찾았다.
- seed가 작고 실행 시간 벤치마크를 하지 않았으므로 어느 방식이 항상 더 빠르다고 결론 내리지 않는다.
- 실제 성능은 데이터 크기와 분포, 통계, 인덱스, SQLite 버전에 따라 달라질 수 있다.

선택 기준:

| 방식 | 장점 | 주의점 |
|---|---|---|
| JOIN | 양쪽 테이블 컬럼을 함께 꺼내기 쉽다 | 중복 때문에 DISTINCT가 필요할 수 있다 |
| 서브쿼리 | “해당 목록에 포함되는가”라는 질문을 그대로 표현하기 쉽다 | 복잡한 상관 서브쿼리는 별도 계획 확인이 필요하다 |

## 3. KPI 1 — 카테고리별 매출 비중

```sql
WITH category_revenue AS (
    SELECT c.id,
           c.name,
           SUM(CASE WHEN o.status <> 'CANCELLED'
                    THEN m.price * o.quantity ELSE 0 END) AS revenue
    FROM menu_categories c
    LEFT JOIN menus m ON m.category_id = c.id
    LEFT JOIN orders o ON o.menu_id = m.id
    GROUP BY c.id, c.name
),
total_revenue AS (
    SELECT SUM(revenue) AS total FROM category_revenue
)
SELECT cr.name AS category_name,
       cr.revenue AS category_revenue,
       ROUND(cr.revenue * 100.0 / NULLIF(tr.total, 0), 1)
           AS revenue_share_percentage
FROM category_revenue cr
CROSS JOIN total_revenue tr
ORDER BY category_revenue DESC, cr.id;
```

### 결과 요약

10개 카테고리의 매출과 비중을 반환한다. 상위 3개는 다음과 같다.

| 카테고리 | 매출 | 비중 |
|---|---:|---:|
| 탕/전골 요리 | 128,000원 | 27.6% |
| 시그니처 메인 | 102,000원 | 22.0% |
| 소주/맥주 | 85,000원 | 18.3% |

취소 주문은 매출에서 제외한다. 전체 결과는 `evidence/bonus_03_kpi_metrics.txt`에 있다.

## 4. KPI 2 — 좌석 수용 인원별 물리 테이블당 평균 매출

```sql
WITH table_revenue AS (
    SELECT st.id,
           st.capacity,
           SUM(CASE WHEN o.status <> 'CANCELLED'
                    THEN m.price * o.quantity ELSE 0 END) AS revenue
    FROM store_tables st
    LEFT JOIN orders o ON o.table_id = st.id
    LEFT JOIN menus m ON m.id = o.menu_id
    GROUP BY st.id, st.capacity
)
SELECT capacity,
       COUNT(*) AS table_count,
       ROUND(AVG(revenue), 0) AS avg_revenue_per_table
FROM table_revenue
GROUP BY capacity
ORDER BY capacity;
```

### 결과

| 수용 인원 | 물리 테이블 수 | 테이블당 평균 매출 |
|---:|---:|---:|
| 2 | 3 | 13,667원 |
| 4 | 6 | 30,333원 |
| 6 | 2 | 51,500원 |
| 8 | 1 | 138,000원 |

먼저 실제 좌석 ID별 매출을 만든 후 같은 수용 인원끼리 평균을 내므로, 주문 행이 많은 좌석이 평균 계산에서 중복 가중되지 않는다.

## 5. KPI 3 — 주방 혼잡도

```sql
SELECT COUNT(*) AS active_orders,
       SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END)
           AS cooking_orders,
       ROUND(
           SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) * 100.0
           / NULLIF(COUNT(*), 0),
           1
       ) AS kitchen_congestion_rate
FROM orders;
```

### 결과

- 활성 주문 행: 24개
- COOKING 주문 행: 5개
- 주방 혼잡도: 20.8%

Query 14가 취소 주문 ID 25를 삭제한 뒤의 같은 실행 상태에서 계산한다. 이 데이터 모델에서 한 주문 행은 메뉴 한 항목이므로, 이 수치는 주문서 수가 아니라 **주문 항목 행 비율**이다.

## 6. 상태 기준에 관한 선택

- 매출 KPI는 `CANCELLED`를 제외한다.
- 혼잡도 분모는 Query 14 이후 DB에 남은 전체 주문 항목이다.
- 실제 운영 환경에서는 결제 완료 여부, 환불, 조회 기간, 영업일 경계를 추가해야 한다.

## 7. 재현

```bash
python scripts/verify_project.py
```

생성 파일:

- `evidence/bonus_01_compare_methods.txt`
- `evidence/bonus_02_fk_error_test.txt`
- `evidence/bonus_03_kpi_metrics.txt`
