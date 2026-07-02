# 보너스 과제 심화 분석 리포트

> **도메인 주제**: 스마트 테이블 오더 시스템 데이터베이스 (Table Order DB)  
> **리포트 범위**: 조인 vs 서브쿼리 문법 비교, 외래키 위반 에러 테스트, 외식업 매장 운영 핵심 KPI 도출

---

## 1. 조인 1개를 두 가지 방식으로 풀기 및 구조 비교

### 비즈니스 요구사항
> *"현재 주방에서 조리 중('COOKING')인 주문에 포함된 '메뉴 이름'과 '가격'을 조회하시오."*

#### 방식 A. INNER JOIN을 활용한 해결
```sql
SELECT m.name, m.price
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'COOKING';
```

#### 방식 B. WHERE 절 서브쿼리(IN)를 활용한 해결
```sql
SELECT name, price
FROM menus
WHERE id IN (
    SELECT menu_id 
    FROM orders 
    WHERE status = 'COOKING'
);
```

### 작성 관점 및 실행 차이 비교
1. **작성 구조 관점**: `JOIN` 방식은 메뉴 정보 테이블과 주문 테이블을 수평적으로 나란히 연결하여 두 테이블의 데이터를 동시에 검증할 때 가독성이 좋습니다. 반면 서브쿼리 방식은 최종적으로 조회하고자 하는 대상 테이블(`menus`)을 명확히 고정하고, 조건 필터링에 필요한 테이블(`orders`)을 괄호 안으로 분리하므로 쿼리의 목적어 대상이 더 뚜렷하게 보입니다.
2. **실행 엔진 관점**: SQLite 및 최신 RDBMS의 쿼리 최적화 기능(Optimizer)은 `IN (SELECT...)` 형태의 서브쿼리를 내부적으로 `JOIN` 실행 계획으로 재정렬하여 처리합니다. 따라서 두 쿼리의 실제 데이터 검색 속도는 동일합니다. 다만 실무에서 주문 기록이 수백만 건 이상 쌓였을 때는 서브쿼리로 필터링 대상을 먼저 좁힌 뒤 메뉴 테이블을 조회하는 것이 메모리 부하를 줄이는 데 도움을 줄 수 있습니다.

---

## 2. 데이터 정합성(무결성) 위반 실험 기록

### 실험 시도
매장에 등록되지 않은 가상의 테이블 좌석 번호 ID(`9999`)로 강제 주문 입력을 시도했습니다.

```sql
INSERT INTO orders (id, table_id, menu_id, quantity, order_time, status) 
VALUES (999, 9999, 1, 2, '2026-06-24 21:00:00', 'COOKING');
```

### 실행 결과 (에러 메시지 발생)
```text
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

### 차단 원인 및 정상화 방법
* **차단 원인**: `orders.table_id` 컬럼에 설정된 `FOREIGN KEY REFERENCES store_tables(id)` 참조 규칙 때문입니다. 데이터베이스 엔진은 데이터를 입력하기 직전 부모 테이블인 `store_tables`에 `9999`번 좌석이 존재하는지 먼저 확인하며, 존재하지 않을 경우 정산 오류를 막기 위해 입력을 강제 거부하고 Rollback 처리합니다.
* **해결 방법**: 
  1. 매장에 신규 테이블이 추가된 것이 맞다면 `store_tables` 테이블에 `id = 9999` 좌석을 먼저 `INSERT` 하거나,
  2. 통신 오류로 잘못 입력된 좌석 ID를 기존에 존재하는 정상 좌석 범위(`id = 1 ~ 12`)로 정정한 후 다시 입력해야 합니다.

---

## 3. 매장 운영 관점 핵심 KPI 지표 도출 리포트

스마트 테이블 오더 데이터베이스에서 추출하여 매장 매출 관리와 주방 운영 효율화를 돕는 **핵심 지표(KPI) 3개**를 설계했습니다.

### ① [KPI 1] 메뉴 카테고리별 매출 비중 분석 (Revenue Share by Category)
* **정의**: 매장의 카테고리별 총매출액과 전체 매출에서 차지하는 비중(%). 어떤 카테고리 상품이 주력 매출원인지 파악하는 지표.
* **SQL 쿼리**:
  ```sql
  SELECT 
      c.name AS category_name,
      SUM(m.price * o.quantity) AS category_revenue,
      ROUND(SUM(m.price * o.quantity) * 100.0 / (
          SELECT SUM(m2.price * o2.quantity) 
          FROM orders o2 
          JOIN menus m2 ON o2.menu_id = m2.id 
          WHERE o2.status != 'CANCELLED'
      ), 1) AS revenue_share_percentage
  FROM menu_categories c
  INNER JOIN menus m ON c.id = m.category_id
  INNER JOIN orders o ON m.id = o.menu_id
  WHERE o.status != 'CANCELLED'
  GROUP BY c.id, c.name
  ORDER BY category_revenue DESC;
  ```

### ② [KPI 2] 좌석 인원수 규모별 평균 주문 금액 (Average Spend per Table Capacity)
* **정의**: 2인석, 4인석, 단체석 등 테이블 수용 규모에 따른 평균 테이블 정산 금액. 효율적인 매장 좌석 배치 구성을 위한 지표.
* **SQL 쿼리**:
  ```sql
  SELECT 
      t.capacity || '인석' AS table_type,
      COUNT(DISTINCT t.id) AS total_tables_of_type,
      COUNT(o.id) AS total_order_count,
      ROUND(SUM(m.price * o.quantity) * 1.0 / COUNT(DISTINCT t.id), 0) AS avg_revenue_per_table
  FROM store_tables t
  LEFT JOIN orders o ON t.id = o.table_id AND o.status != 'CANCELLED'
  LEFT JOIN menus m ON o.menu_id = m.id
  GROUP BY t.capacity
  ORDER BY avg_revenue_per_table DESC;
  ```

### ③ [KPI 3] 주방 조리 대기 집중도 분석 (Kitchen Bottleneck Index)
* **정의**: 전체 활성 주문 중 현재 주방에서 조리 중(`COOKING`)인 티켓이 차지하는 비율. 주방 인력 추가 투입 필요성을 판단하는 지표.
* **SQL 쿼리**:
  ```sql
  SELECT 
      COUNT(*) AS total_live_orders,
      SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) AS cooking_orders,
      ROUND(SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS kitchen_congestion_rate
  FROM orders
  WHERE status != 'CANCELLED';
  ```
