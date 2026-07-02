-- ============================================================================
-- 파일명: 3_queries.sql
-- 설명: 스마트 테이블 오더 시스템 핵심 서비스 요구사항 쿼리 (총 15개)
-- 작성 기준: 실제 매장에서 필요로 하는 데이터 도출 기능을 범주별로 모듈화 작성
-- ============================================================================

-- ============================================================================
-- [범주 A: 기본 조회] (WHERE, ORDER BY, LIMIT 활용)
-- ============================================================================

-- [기본조회 1] 단가가 20,000원 이상인 프리미엄 요리 메뉴들의 메뉴명과 가격을 가격이 높은 순으로 정렬하여 상위 5개 조회
SELECT name, price 
FROM menus 
WHERE price >= 20000 
ORDER BY price DESC 
LIMIT 5;

-- [기본조회 2] 메뉴명에 '전골' 또는 '철판' 키워드가 포함된 메인 요리들의 메뉴명과 가격 조회
SELECT name, price 
FROM menus 
WHERE name LIKE '%전골%' OR name LIKE '%철판%';

-- [기본조회 3] 현재 주방에서 조리 중인('COOKING') 주문 내역의 주문번호, 테이블 ID, 메뉴 ID, 주문시간 조회
SELECT id, table_id, menu_id, order_time 
FROM orders 
WHERE status = 'COOKING' 
ORDER BY order_time ASC;

-- [기본조회 4] 매장 내 좌석 중 수용 인원이 6명 이상인 다인석 및 단체석의 좌석 번호와 수용 인원수 조회
SELECT table_number, capacity 
FROM store_tables 
WHERE capacity >= 6;


-- ============================================================================
-- [범주 B: 테이블 결합 (JOIN)] (INNER JOIN 2개, LEFT JOIN 2개 포함)
-- ============================================================================

-- [조인 1 - INNER] 주문 내역에 대해 테이블 번호와 주문된 메뉴명, 수량, 주문 상태를 결합하여 실시간 주방 모니터 조회
SELECT t.table_number, m.name AS menu_name, o.quantity, o.status, o.order_time
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED';

-- [조인 2 - INNER] 주류 관련 카테고리에 속한 메뉴들의 카테고리명, 메뉴명, 가격 조회
SELECT c.name AS category_name, m.name AS menu_name, m.price
FROM menus m
INNER JOIN menu_categories c ON m.category_id = c.id
WHERE c.name LIKE '%소주%' OR c.name LIKE '%하이볼%';

-- [조인 3 - LEFT] 전체 매장 메뉴를 기준으로 주문 트랜잭션을 결합하여, 오늘 단 한 번도 주문되지 않은 판매 부진 메뉴 탐색
SELECT m.id, m.name, m.price
FROM menus m
LEFT JOIN orders o ON m.id = o.menu_id
WHERE o.id IS NULL;

-- [조인 4 - LEFT] 전체 매장 좌석을 기준으로 주문 내역을 결합하여, 현재 주문 내역이 전혀 없는 빈 테이블(공석) 탐색
SELECT t.table_number, t.capacity
FROM store_tables t
LEFT JOIN orders o ON t.id = o.table_id
WHERE o.id IS NULL;


-- ============================================================================
-- [범주 C: 집계 분석 (GROUP BY)] (COUNT, SUM, AVG 활용 및 GROUP BY 필수 포함)
-- ============================================================================

-- [집계 1] 메뉴 카테고리별 등록된 메뉴 종류 수(COUNT)와 평균 단가(AVG)를 그룹화 집계하여 메뉴 수가 많은 순으로 조회
SELECT c.name AS category_name, COUNT(m.id) AS menu_count, ROUND(AVG(m.price), 0) AS avg_menu_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY menu_count DESC;

-- [집계 2] 매장 좌석(테이블)별 누적 주문 총금액(SUM)을 정산 그룹화 집계하여 매출 기여도가 높은 테이블 순으로 조회
SELECT t.table_number, SUM(m.price * o.quantity) AS total_bill_amount
FROM store_tables t
INNER JOIN orders o ON t.id = o.table_id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
GROUP BY t.id, t.table_number
ORDER BY total_bill_amount DESC;

-- [집계 3] 판매 메뉴별 총 판매 수량(SUM)을 그룹화 집계하고, 총 판매량이 3개 이상인 인기 베스트셀러 메뉴 조회
SELECT m.name AS menu_name, SUM(o.quantity) AS total_sold_qty
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'SERVED'
GROUP BY m.id, m.name
HAVING SUM(o.quantity) >= 3;


-- ============================================================================
-- [범주 D: 서브쿼리 (Subquery)]
-- ============================================================================

-- [서브쿼리 1] 전체 메뉴 중 '가장 비싼 최고가 메뉴'가 포함된 주문 내역 전체 정보 조회
SELECT * 
FROM orders 
WHERE menu_id = (
    SELECT id 
    FROM menus 
    ORDER BY price DESC 
    LIMIT 1
);


-- ============================================================================
-- [범주 E: 데이터 수정 및 삭제 (UPDATE, DELETE)]
-- ============================================================================

-- [수정 1] 주방에서 조리가 끝난 18번 주문 건의 상태를 서빙 완료된 'SERVED' 상태로 업데이트
UPDATE orders 
SET status = 'SERVED' 
WHERE id = 18;

-- [삭제 1] 취소 처리된('CANCELLED') 25번 주문 건을 DB 트랜잭션 이력에서 삭제
DELETE FROM orders 
WHERE id = 25;


-- ============================================================================
-- [범주 F: 검색 최적화 인덱스 (CREATE INDEX)]
-- ============================================================================

-- [인덱스 적용 이유]: 실시간 주방 디스플레이에서 조리 대기 중인 상태의 주문을 주기적으로 필터링 조회하므로 Full Scan 방지를 위해 부여함
CREATE INDEX idx_order_status ON orders (status);
