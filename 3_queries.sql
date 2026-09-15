-- ============================================================================
-- 파일명: 3_queries.sql
-- 설명: 스마트 테이블 오더 시스템 핵심 요구사항 쿼리 15개
-- 대상 DB: SQLite 3
-- 실행 증거: 각 쿼리 마커 아래의 -- [증거] 주석은 verify_project.py가 실제 실행
--            결과(행 수·결과 표·rows_affected·실행 계획)로 재생성한다. 손으로 고치지 않는다.
-- SQLite 전용/차이: LIMIT, PRAGMA, 유연한 DATETIME 저장 방식, `CREATE INDEX IF NOT EXISTS`를 사용한다.
--                  `ROUND(값, 자리)`는 SQLite·MySQL 서식이고 PostgreSQL은 `ROUND(numeric)`만 받아 자리수를 쓰지 않는다.
-- 실행 전 1_schema.sql → 2_data.sql 순서로 새 DB를 준비한다.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- [Q01][기본조회] 20,000원 이상 메뉴를 높은 가격순으로 최대 5개 조회한다.
-- [증거] rows=4
-- [증거] name	price
-- [증거] ----------------------------------------
-- [증거] 한우 곱창 전골	32000
-- [증거] 화요 25	28000
-- [증거] 매콤 철판 쭈꾸미	24000
-- [증거] 모둠 수제 꼬치	22000
SELECT name, price
FROM menus
WHERE price >= 20000
ORDER BY price DESC
LIMIT 5;

-- [Q02][기본조회] 이름에 '전골' 또는 '철판'이 포함된 메뉴를 최대 10개 조회한다.
-- [증거] rows=2
-- [증거] name	price
-- [증거] ----------------------------------------
-- [증거] 한우 곱창 전골	32000
-- [증거] 매콤 철판 쭈꾸미	24000
SELECT name, price
FROM menus
WHERE name LIKE '%전골%' OR name LIKE '%철판%'
ORDER BY id
LIMIT 10;

-- [Q03][기본조회] 현재 COOKING 상태인 주문을 오래된 주문순으로 최대 10개 조회한다.
-- [증거] rows=5
-- [증거] id	table_id	menu_id	order_time
-- [증거] -------------------------------------------
-- [증거] 18	10	4	2026-06-24 20:15:00
-- [증거] 20	6	9	2026-06-24 20:20:00
-- [증거] 21	6	5	2026-06-24 20:21:00
-- [증거] 22	9	1	2026-06-24 20:30:00
-- [증거] 23	9	10	2026-06-24 20:31:00
SELECT id, table_id, menu_id, order_time
FROM orders
WHERE status = 'COOKING'
ORDER BY order_time ASC
LIMIT 10;

-- [Q04][기본조회] 수용 인원이 6명 이상인 좌석 번호를 번호순으로 최대 10개 조회한다.
-- [증거] rows=3
-- [증거] table_number	capacity
-- [증거] ----------------------------------------
-- [증거] 201	6
-- [증거] 202	6
-- [증거] 203	8
SELECT table_number, capacity
FROM store_tables
WHERE capacity >= 6
ORDER BY table_number
LIMIT 10;

-- [Q05][INNER JOIN] 취소되지 않은 주문에 좌석 번호와 메뉴 정보를 결합한다.
-- [증거] rows=24
-- [증거] table_number	menu_name	quantity	status	order_time
-- [증거] -----------------------------------------------------------------
-- [증거] 103	한우 곱창 전골	1	SERVED	2026-06-24 18:10:00
-- [증거] 103	참이슬 후레쉬	2	SERVED	2026-06-24 18:11:00
-- [증거] 103	테라 생맥주 500ml	1	SERVED	2026-06-24 18:11:30
-- [증거] 104	차돌 떡볶이	1	SERVED	2026-06-24 18:15:00
-- [증거] 104	참치 마요 주먹밥	1	SERVED	2026-06-24 18:15:20
-- [증거] 104	제로 콜라	2	SERVED	2026-06-24 18:16:00
-- [증거] 201	모둠 수제 꼬치	1	SERVED	2026-06-24 18:25:00
-- [증거] 201	화요 25	1	SERVED	2026-06-24 18:26:00
-- [증거] 201	바삭 감자전	1	SERVED	2026-06-24 18:40:00
-- [증거] 101	매콤 철판 쭈꾸미	1	SERVED	2026-06-24 19:00:00
-- [증거] 101	산토리 얼그레이 하이볼	2	SERVED	2026-06-24 19:02:00
-- [증거] 105	한우 곱창 전골	1	SERVED	2026-06-24 19:15:00
-- [증거] 105	참이슬 후레쉬	3	SERVED	2026-06-24 19:16:00
-- [증거] 105	해물 라면	1	SERVED	2026-06-24 19:45:00
-- [증거] 202	해물 파전	1	SERVED	2026-06-24 20:00:00
-- [증거] 202	테라 생맥주 500ml	4	SERVED	2026-06-24 20:01:00
-- [증거] 103	파인애플 샤베트	1	SERVED	2026-06-24 20:10:00
-- [증거] 204	치즈 계란말이	1	COOKING	2026-06-24 20:15:00
-- [증거] 204	참이슬 후레쉬	1	SERVED	2026-06-24 20:15:10
-- [증거] 106	차돌 떡볶이	1	COOKING	2026-06-24 20:20:00
-- [증거] 106	참치 마요 주먹밥	2	COOKING	2026-06-24 20:21:00
-- [증거] 203	한우 곱창 전골	2	COOKING	2026-06-24 20:30:00
-- [증거] 203	모둠 수제 꼬치	2	COOKING	2026-06-24 20:31:00
-- [증거] 203	참이슬 후레쉬	6	SERVED	2026-06-24 20:32:00
SELECT t.table_number, m.name AS menu_name, o.quantity, o.status, o.order_time
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
ORDER BY o.order_time;

-- [Q06][INNER JOIN] 주류 카테고리 3종의 카테고리명·메뉴명·가격을 조회한다.
-- [증거] rows=4
-- [증거] category_name	menu_name	price
-- [증거] ----------------------------------------
-- [증거] 소주/맥주	참이슬 후레쉬	5000
-- [증거] 소주/맥주	테라 생맥주 500ml	5000
-- [증거] 하이볼/칵테일	산토리 얼그레이 하이볼	8500
-- [증거] 프리미엄 전통주	화요 25	28000
SELECT c.name AS category_name, m.name AS menu_name, m.price
FROM menus m
INNER JOIN menu_categories c ON m.category_id = c.id
WHERE c.name IN ('소주/맥주', '하이볼/칵테일', '프리미엄 전통주')
ORDER BY c.id, m.id;

-- [Q07][LEFT JOIN] 전체 샘플 기간에 주문 이력이 한 번도 없는 메뉴를 찾는다.
-- [증거] rows=1
-- [증거] id	name	price
-- [증거] ----------------------------------------
-- [증거] 16	유자차	4500
SELECT m.id, m.name, m.price
FROM menus m
LEFT JOIN orders o ON m.id = o.menu_id
WHERE o.id IS NULL
ORDER BY m.id;

-- [Q08][LEFT JOIN] 전체 샘플 기간에 주문 이력이 한 번도 없는 좌석을 찾는다.
-- [증거] rows=3
-- [증거] table_number	capacity
-- [증거] ----------------------------------------
-- [증거] 102	2
-- [증거] 107	2
-- [증거] 108	4
SELECT t.table_number, t.capacity
FROM store_tables t
LEFT JOIN orders o ON t.id = o.table_id
WHERE o.id IS NULL
ORDER BY t.table_number;

-- [Q09][집계] 카테고리별 메뉴 수와 평균 단가를 메뉴 수가 많은 순으로 조회한다.
-- [증거] rows=10
-- [증거] category_name	menu_count	avg_menu_price
-- [증거] -------------------------------------------------
-- [증거] 시그니처 메인	2	20000.0
-- [증거] 튀김/안주류	2	16500.0
-- [증거] 가벼운 사이드	2	10000.0
-- [증거] 식사류	2	6000.0
-- [증거] 소주/맥주	2	5000.0
-- [증거] 음료/탄산	2	3500.0
-- [증거] 탕/전골 요리	1	32000.0
-- [증거] 볶음/철판 요리	1	24000.0
-- [증거] 하이볼/칵테일	1	8500.0
-- [증거] 프리미엄 전통주	1	28000.0
SELECT c.name AS category_name,
       COUNT(m.id) AS menu_count,
       ROUND(AVG(m.price), 0) AS avg_menu_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY menu_count DESC, c.id;

-- [Q10][집계] 좌석별 취소 제외 주문 금액을 높은 순으로 조회한다.
-- [증거] rows=9
-- [증거] table_number	total_bill_amount
-- [증거] ----------------------------------------
-- [증거] 203	138000
-- [증거] 201	65000
-- [증거] 103	55000
-- [증거] 105	54000
-- [증거] 101	41000
-- [증거] 202	38000
-- [증거] 104	28000
-- [증거] 106	28000
-- [증거] 204	17000
SELECT t.table_number,
       SUM(m.price * o.quantity) AS total_bill_amount
FROM store_tables t
INNER JOIN orders o ON t.id = o.table_id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
GROUP BY t.id, t.table_number
ORDER BY total_bill_amount DESC;

-- [Q11][집계] SERVED 판매 수량이 3개 이상인 메뉴를 조회한다.
-- [증거] rows=2
-- [증거] menu_name	total_sold_qty
-- [증거] ----------------------------------------
-- [증거] 참이슬 후레쉬	12
-- [증거] 테라 생맥주 500ml	5
SELECT m.name AS menu_name,
       SUM(o.quantity) AS total_sold_qty
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'SERVED'
GROUP BY m.id, m.name
HAVING SUM(o.quantity) >= 3
ORDER BY total_sold_qty DESC, m.id;

-- [Q12][서브쿼리] 최고 가격과 같은 모든 메뉴가 포함된 주문을 조회한다.
-- [증거] rows=3
-- [증거] id	table_id	menu_id	quantity	order_time	status
-- [증거] -----------------------------------------------------------------
-- [증거] 1	3	1	1	2026-06-24 18:10:00	SERVED
-- [증거] 12	5	1	1	2026-06-24 19:15:00	SERVED
-- [증거] 22	9	1	2	2026-06-24 20:30:00	COOKING
SELECT *
FROM orders
WHERE menu_id IN (
    SELECT id
    FROM menus
    WHERE price = (SELECT MAX(price) FROM menus)
)
ORDER BY id;

-- [Q13][수정] 18번 주문이 아직 COOKING일 때만 SERVED로 변경한다.
-- [증거] rows_affected=1
-- [증거] orders.id=18 status=SERVED PASS
UPDATE orders
SET status = 'SERVED'
WHERE id = 18 AND status = 'COOKING';

-- [Q14][삭제] 25번 주문이 CANCELLED 상태일 때만 삭제한다.
-- [증거] rows_affected=1
-- [증거] orders.id=25 remaining=0 PASS
DELETE FROM orders
WHERE id = 25 AND status = 'CANCELLED';

-- [Q15][인덱스] 반복되는 status 필터를 위해 `orders(status)` 인덱스를 만들고 근거를 실행 계획으로 남긴다.
-- [증거] rows=1
-- [증거] statement
-- [증거] ----------------------------------------
-- [증거] CREATE 성공 · 반환 행 없음
-- [증거] idx_order_status exists PASS
-- [증거] query_plan=SEARCH orders USING INDEX idx_order_status (status=?)
-- 적용 이유: Q03·B01·B02처럼 `status`로 자르는 조회가 파일마다 반복되고, 주문 테이블은 계속 커지는 쓰기보다 읽기가 많은 쪽이다.
-- 효과의 범위: 아래 실행 계획은 SQLite가 인덱스를 "선택"했다는 사실까지 말한다. 25행에서는 행이 적어 실제 시간 차이가 체감되지 않으므로 빠르다고 주장하지 않는다.
-- 실제 운영 후보: `status`만으로는 선택도가 낮아(허용값 3종) `orders(status, order_time)` 복합 인덱스나 "아직 서빙 전" 부분 인덱스가 더 자연스럽다.
-- SQLite 전용: `CREATE INDEX ... IF NOT EXISTS`는 MySQL에 없고, PostgreSQL은 부분 인덱스(`WHERE status='COOKING'`)를 지원한다.
CREATE INDEX IF NOT EXISTS idx_order_status ON orders (status);
