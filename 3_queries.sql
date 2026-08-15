-- ============================================================================
-- 파일명: 3_queries.sql
-- 설명: 스마트 테이블 오더 시스템 핵심 요구사항 쿼리 15개
-- 대상 DB: SQLite 3
-- SQLite 전용/차이: LIMIT, PRAGMA, 유연한 DATETIME 저장 방식을 사용한다.
-- 실행 전 1_schema.sql → 2_data.sql 순서로 새 DB를 준비한다.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- [Q01][기본조회] 20,000원 이상 메뉴를 높은 가격순으로 최대 5개 조회한다.
SELECT name, price
FROM menus
WHERE price >= 20000
ORDER BY price DESC
LIMIT 5;

-- [Q02][기본조회] 이름에 '전골' 또는 '철판'이 포함된 메뉴를 조회한다.
SELECT name, price
FROM menus
WHERE name LIKE '%전골%' OR name LIKE '%철판%'
ORDER BY id;

-- [Q03][기본조회] 현재 COOKING 상태인 주문을 오래된 주문순으로 조회한다.
SELECT id, table_id, menu_id, order_time
FROM orders
WHERE status = 'COOKING'
ORDER BY order_time ASC;

-- [Q04][기본조회] 수용 인원이 6명 이상인 좌석을 번호순으로 조회한다.
SELECT table_number, capacity
FROM store_tables
WHERE capacity >= 6
ORDER BY table_number;

-- [Q05][INNER JOIN] 취소되지 않은 주문에 좌석 번호와 메뉴 정보를 결합한다.
SELECT t.table_number, m.name AS menu_name, o.quantity, o.status, o.order_time
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
ORDER BY o.order_time;

-- [Q06][INNER JOIN] 주류 카테고리 3종의 카테고리명·메뉴명·가격을 조회한다.
SELECT c.name AS category_name, m.name AS menu_name, m.price
FROM menus m
INNER JOIN menu_categories c ON m.category_id = c.id
WHERE c.name IN ('소주/맥주', '하이볼/칵테일', '프리미엄 전통주')
ORDER BY c.id, m.id;

-- [Q07][LEFT JOIN] 전체 샘플 기간에 주문 이력이 한 번도 없는 메뉴를 찾는다.
SELECT m.id, m.name, m.price
FROM menus m
LEFT JOIN orders o ON m.id = o.menu_id
WHERE o.id IS NULL
ORDER BY m.id;

-- [Q08][LEFT JOIN] 전체 샘플 기간에 주문 이력이 한 번도 없는 좌석을 찾는다.
SELECT t.table_number, t.capacity
FROM store_tables t
LEFT JOIN orders o ON t.id = o.table_id
WHERE o.id IS NULL
ORDER BY t.table_number;

-- [Q09][집계] 카테고리별 메뉴 수와 평균 단가를 메뉴 수가 많은 순으로 조회한다.
SELECT c.name AS category_name,
       COUNT(m.id) AS menu_count,
       ROUND(AVG(m.price), 0) AS avg_menu_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY menu_count DESC, c.id;

-- [Q10][집계] 좌석별 취소 제외 주문 금액을 높은 순으로 조회한다.
SELECT t.table_number,
       SUM(m.price * o.quantity) AS total_bill_amount
FROM store_tables t
INNER JOIN orders o ON t.id = o.table_id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
GROUP BY t.id, t.table_number
ORDER BY total_bill_amount DESC;

-- [Q11][집계] SERVED 판매 수량이 3개 이상인 메뉴를 조회한다.
SELECT m.name AS menu_name,
       SUM(o.quantity) AS total_sold_qty
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'SERVED'
GROUP BY m.id, m.name
HAVING SUM(o.quantity) >= 3
ORDER BY total_sold_qty DESC, m.id;

-- [Q12][서브쿼리] 최고 가격과 같은 모든 메뉴가 포함된 주문을 조회한다.
SELECT *
FROM orders
WHERE menu_id IN (
    SELECT id
    FROM menus
    WHERE price = (SELECT MAX(price) FROM menus)
)
ORDER BY id;

-- [Q13][수정] 18번 주문이 아직 COOKING일 때만 SERVED로 변경한다.
UPDATE orders
SET status = 'SERVED'
WHERE id = 18 AND status = 'COOKING';

-- [Q14][삭제] 25번 주문이 CANCELLED 상태일 때만 삭제한다.
DELETE FROM orders
WHERE id = 25 AND status = 'CANCELLED';

-- [Q15][인덱스] 반복되는 status 필터의 후보 인덱스를 만들고 효과는 실행 계획으로 확인한다.
CREATE INDEX IF NOT EXISTS idx_order_status ON orders (status);
