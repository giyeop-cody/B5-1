-- ============================================================================
-- 파일명: 4_bonus_queries.sql
-- 설명: B5-1 보너스 1·3 검증용 SQL
-- 대상 DB: SQLite 3
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
