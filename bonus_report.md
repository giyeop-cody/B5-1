# B5-1 보너스 과제 실증 보고서

- SQL 원본: [`4_bonus_queries.sql`](4_bonus_queries.sql)
- 실행 결과 원본: [`evidence/bonus_01_compare_methods.txt`](evidence/bonus_01_compare_methods.txt) · [`evidence/bonus_03_kpi_metrics.txt`](evidence/bonus_03_kpi_metrics.txt)
- 실행 상태: `1_schema.sql → 2_data.sql → 3_queries.sql → 4_bonus_queries.sql` 순서, **Q13·Q14의 변경이 적용된 뒤의 같은 DB**
- 이 문서의 SQL 인용문은 `python scripts/verify_project.py`가 `4_bonus_queries.sql`과 대조해 어긋나면 검사가 실패한다.

## 0. 실행 상태를 먼저 정하는 이유

Q13은 주문 18을 `COOKING → SERVED`로 바꾸고 Q14는 취소 주문 25를 삭제한다. `orders`는 상태가 계속 움직이는 테이블이라, 보너스 질문의 답은 **언제 재는가**에 따라 달라진다. 그래서 이 프로젝트는 문서·증거·수동 실행이 모두 같은 상태를 보도록 보너스를 변경 후 DB에서 실행한다.

- 새 데이터 기준으로 보면 `COOKING` 메뉴가 5개(메뉴 ID 1·4·5·9·10), 혼잡도 20.8%다.
- Q13·Q14가 지난 뒤 다시 보면 4개(ID 1·5·9·10), 혼잡도 16.7%다.
- 아래 모든 수치는 두 번째 상태다. 이 차이가 오류가 아니라 "지표가 쓰기 작업에 반응한다"는 사실의 증거라고 적어둔다.

## 1. 같은 질문을 JOIN과 서브쿼리로 해결 (보너스 1)

### 질문

지금 `COOKING` 상태인 주문에 포함된 메뉴의 중복 없는 목록은 무엇인가?

### JOIN 방식

```sql
SELECT DISTINCT m.id, m.name, m.price
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'COOKING'
ORDER BY m.id;
```

### 서브쿼리 방식

```sql
SELECT m.id, m.name, m.price
FROM menus m
WHERE m.id IN (
    SELECT o.menu_id
    FROM orders o
    WHERE o.status = 'COOKING'
)
ORDER BY m.id;
```

### 실제 동치 검증

두 결과를 `(id, name, price)` 튜플 목록으로 만들어 순서까지 비교한다. 행 수가 같은 것만 보지 않는다.

- JOIN 결과: 4행
- 서브쿼리 결과: 4행
- 비교: `SET EQUALITY: PASS` (`verify_project.py`가 두 결과 목록의 동치를 `assert`한다)
- 메뉴 ID: 1, 5, 9, 10

따라서 **현재 질문과 현재 상태에서는 결과 집합이 실제로 같다.** `IN` 서브쿼리는 중복을 만들지 않으므로 DISTINCT가 필요 없고, JOIN은 `orders` 행 수만큼 메뉴 행이 중복될 수 있으므로 DISTINCT가 필요하다는 차이가 SQL에만 남는다.

## 2. 실행 계획으로 말할 수 있는 범위

Q15가 만든 인덱스 이후 상태의 계획 원문(`evidence/bonus_01_compare_methods.txt`에 자동 기록된다).

```text
JOIN:     SEARCH o USING INDEX idx_order_status (status=?) | SEARCH m USING INTEGER PRIMARY KEY (rowid=?) | USE TEMP B-TREE FOR DISTINCT | USE TEMP B-TREE FOR ORDER BY
SUBQUERY: SEARCH m USING INTEGER PRIMARY KEY (rowid=?) | LIST SUBQUERY 1 | SEARCH o USING INDEX idx_order_status (status=?)
```

해석:

- 두 계획 모두 `orders`를 `idx_order_status`로 짚는다. Q15의 인덱스가 실제 조회에 쓰이는지 확인하는 근거가 여기 있다.
- JOIN 쪽에 `USE TEMP B-TREE FOR DISTINCT`가 남는다. 중복 제거 비용을 치르는 대신 두 테이블 컬럼을 한 번에 꺼낸다.
- 서브쿼리 쪽은 `LIST SUBQUERY 1`로 메뉴 ID 목록을 먼저 만들고 `menus`의 PK를 짚는다.
- 25행에서는 두 계획의 실행 시간을 재도 어느 쪽이 이겼다고 말할 근거가 없다. 벤치마크 없이 "언제나 빠르다"를 주장하지 않는다.

선택 기준:

| 방식 | 장점 | 주의점 |
|---|---|---|
| JOIN | 양쪽 테이블 컬럼을 함께 꺼내기 쉽다 | 관계 증식으로 중복이 생겨 DISTINCT가 필요할 수 있다 |
| 서브쿼리 | "목록에 포함되는가"라는 질문을 그대로 표현한다 | 중복 자체가 없어 DISTINCT가 필요 없지만, 다른 테이블 컬럼을 보여주려면 결국 다시 JOIN이 필요하다 |

## 3. KPI 1 — 카테고리별 매출 비중 (보너스 3)

```sql
SELECT c.name AS category_name,
       SUM(m.price * o.quantity) AS category_revenue,
       ROUND(
           SUM(m.price * o.quantity) * 100.0 /
           (SELECT SUM(m2.price * o2.quantity)
            FROM orders o2
            INNER JOIN menus m2 ON o2.menu_id = m2.id
            WHERE o2.status != 'CANCELLED'),
           1
       ) AS revenue_share_percentage
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status != 'CANCELLED'
GROUP BY c.id, c.name
ORDER BY category_revenue DESC;
```

### 결과 요약 (10행)

| 카테고리 | 매출 | 비중 |
|---|---:|---:|
| 탕/전골 요리 | 128,000원 | 27.6% |
| 시그니처 메인 | 102,000원 | 22.0% |
| 소주/맥주 | 85,000원 | 18.3% |

- 분모는 전체 스칼라 서브쿼리로 계산한다. `INNER JOIN` 체인을 두 번 쓰는 것보다 "전체 취소 제외 매출"이라는 의미가 SQL에 그대로 적힌다.
- 주문 행이 없는 카테고리는 `INNER JOIN` 때문에 0원으로 나타나지 않는다. 0원을 포함한 10개 카테고리가 모두 나오는 이유는 모든 카테고리가 최소 한 개의 주문을 갖고 있기 때문이다. 카테고리가 0원이 되는 설계 비교는 KPI 2가 `LEFT JOIN`으로 담당한다.
- 취소 주문은 분자·분모에서 동시에 제외해 비중의 합이 100%가 되도록 유지한다.

## 4. KPI 2 — 좌석 수용 인원별 물리 테이블당 평균 매출 (보너스 3)

```sql
WITH table_totals AS (
    SELECT t.id,
           t.capacity,
           COALESCE(SUM(CASE WHEN o.status != 'CANCELLED' THEN m.price * o.quantity END), 0) AS table_revenue
    FROM store_tables t
    LEFT JOIN orders o ON t.id = o.table_id
    LEFT JOIN menus m ON o.menu_id = m.id
    GROUP BY t.id, t.capacity
)
SELECT capacity,
       COUNT(*) AS table_count,
       ROUND(AVG(table_revenue), 0) AS avg_revenue_per_table
FROM table_totals
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

- 안쪽 CTE가 먼저 **좌석 ID별** 매출을 1행으로 만든다. 이 단계가 없으면 주문 행이 많은 좌석이 평균에서 두 번 세 번 가중된다.
- `LEFT JOIN`과 `COALESCE(..., 0)`으로 주문이 한 번도 없는 좌석(102·107·108번)도 0원으로 평균에 참여시킨다. Q08에서 찾은 그 좌석들이 여기서는 매출 0으로 집계된다.
- 수용 인원이 커질수록 테이블당 평균 매출이 오르는 모양이 나와 "단체석은 실제로 비싸게 쓰인다"는 해석까지 가능하다. 표본 12개 좌석이라 경향 확인용이지 의사결정 근거가 아니다.

## 5. KPI 3 — 주방 혼잡도 (보너스 3)

```sql
SELECT COUNT(*) AS active_orders,
       SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) AS cooking_orders,
       ROUND(
           SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           1
       ) AS kitchen_congestion_rate
FROM orders
WHERE status != 'CANCELLED';
```

### 결과

- 활성 주문 행: 24개
- `COOKING` 행: 4개
- 주방 혼잡도: **16.7%**

`WHERE status != 'CANCELLED'`가 분모를 정의한다. Q13이 주문 18을 `SERVED`로 바꾼 직후라서 18번은 더 이상 혼잡도에 잡히지 않는다. 이 모델에서 한 주문 행은 주문서가 아니라 **메뉴 한 항목**이므로, 이 수치는 "주문서 중 조리 중 비율"이 아니라 "주문 항목 중 조리 중 비율"이다.

## 6. 지표 기준에 관한 선택과 한계

- 매출 KPI는 `CANCELLED`를 제외한다. 환불·부분 취소는 이 스키마에 상태값이 없어 표현할 수 없다.
- 매출은 `menus.price × quantity`로 계산한다. 주문 시점 가격을 저장하지 않았기 때문에 메뉴 가격을 수정하면 과거 매출도 함께 다시 계산된다. 이번 미션 범위에서는 의도적으로 생략한 항목이고, 근거와 대안은 [`docs/decision-log.md`](docs/decision-log.md)의 D11에 적었다.
- 조회 기간·영업일 경계는 임의의 seed 전체 기간을 사용한다. 운영 지표라면 `order_time` 범위 인자가 반드시 필요하다.

## 7. 재현

```bash
python scripts/verify_project.py
```

`verify_project.py`는 새 DB를 만든 뒤 README와 같은 순서로 Q1~Q15와 보너스를 실행하고, 아래 파일을 다시 쓰며, 이 문서의 SQL 인용이 `4_bonus_queries.sql`과 같은지도 대조한다.

- `evidence/bonus_01_compare_methods.txt`
- `evidence/bonus_02_fk_error_test.txt`
- `evidence/bonus_03_kpi_metrics.txt`
- `evidence/verification_summary.txt`
