-- ============================================================================
-- 파일명: 4_bonus_queries.sql
-- 설명: B5-1 보너스 1·2·3 검증용 SQL
--       보너스 2(일부러 무결성 깨뜨리기)는 이 파일의 [F01]~[F04]에 있다.
-- 대상 DB: SQLite 3
-- 실행 순서: 1_schema.sql → 2_data.sql → 3_queries.sql → 4_bonus_queries.sql
--            Q13(UPDATE)·Q14(DELETE)가 적용된 DB에서 실행한다. `evidence/bonus_*.txt`도
--            스크립트에서 같은 순서·같은 DB로 생성되므로 수동 실행 결과와 증거가 짝을 이룬다.
--            새 데이터로 다시 보려면 `python scripts/verify_project.py`가 매 단계 새 DB를 만든다.
-- ============================================================================

-- [B01][JOIN] COOKING 주문에 포함된 메뉴 집합을 중복 없이 조회한다.
SELECT DISTINCT m.id, m.name, m.price
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'COOKING'
ORDER BY m.id;

-- [B02][서브쿼리] B01과 같은 메뉴 집합을 IN 서브쿼리로 조회한다.
SELECT m.id, m.name, m.price
FROM menus m
WHERE m.id IN (
    SELECT o.menu_id
    FROM orders o
    WHERE o.status = 'COOKING'
)
ORDER BY m.id;

-- [B03][KPI 1] 취소 제외 주문의 카테고리별 매출액과 전체 매출 비중을 계산한다.
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

-- [B04][KPI 2] 좌석 수용 인원별 물리적 테이블 한 개당 평균 누적 주문 금액을 계산한다.
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

-- [B05][KPI 3] 취소 제외 활성 주문 중 COOKING 주문 비율을 계산한다.
SELECT COUNT(*) AS active_orders,
       SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) AS cooking_orders,
       ROUND(
           SUM(CASE WHEN status = 'COOKING' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           1
       ) AS kitchen_congestion_rate
FROM orders
WHERE status != 'CANCELLED';

-- ----------------------------------------------------------------------------
-- [보너스 2] 일부러 무결성 깨뜨리기: 아래 4문은 "반드시 실패해야 하는" 입력이다.
-- sqlite3 CLI로 이 파일을 실행하면 각 문이 Runtime error(FOREIGN KEY / CHECK /
-- UNIQUE constraint failed)를 출력하는데, 그 오류가 곧 차단 증거다.
-- scripts/verify_project.py는 이 4문을 파일에서 읽어 그대로 실행하고
-- sqlite3.IntegrityError가 발생하는지 assert한 뒤 rollback하므로 DB는 깨지지 않는다.
-- ----------------------------------------------------------------------------

-- [F01][FK 위반] 존재하지 않는 좌석 9999를 참조하는 주문 → FOREIGN KEY constraint failed 기대
INSERT INTO orders VALUES (999, 9999, 1, 1, '2026-06-24 21:00:00', 'COOKING');

-- [F02][CHECK 위반] 허용되지 않은 상태 'INVALID' 입력 → CHECK constraint failed: status IN (...) 기대
INSERT INTO orders VALUES (998, 1, 1, 1, '2026-06-24 21:00:00', 'INVALID');

-- [F03][CHECK 위반] 음수 수량 -1 입력 → CHECK constraint failed: quantity > 0 기대
INSERT INTO orders VALUES (997, 1, 1, -1, '2026-06-24 21:00:00', 'COOKING');

-- [F04][UNIQUE 위반] 이미 있는 좌석 번호 101 재입력 → UNIQUE constraint failed: store_tables.table_number 기대
INSERT INTO store_tables VALUES (999, 101, 4);
