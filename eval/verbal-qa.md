# B5-1 동료평가 대비 가이드

## 1. 이 과제가 뭔가요?
프레임워크 없이 SQL을 직접 작성하여 도메인 DB(식당 키오스크 주문 시스템)를 설계하는 과제.

## 2. 평가 예상 질문

### 학습 목표 #1: 관계형 DB 기본 개념 (테이블, 관계, 정규화)

Q1. 정규화가 왜 필요한가요?
A. 데이터 중복을 제거하고 무결성을 보장하기 위함입니다. 예를 들어 메뉴 이름과 가격을 주문 테이블에 직접 넣으면, 메뉴 가격이 바뀔 때 모든 주문 기록을 수정해야 합니다. 정규화를 하면 메뉴는 menus 테이블에 한 번만 저장하고, 주문은 menu_id(FK)로 참조합니다. 가격이 바뀌면 menus 테이블 한 곳만 수정하면 됩니다. 이 프로젝트에서는 4개 테이블(menu_categories, store_tables, menus, orders)로 정규화했습니다.

Q2. PK/FK가 왜 필요한가요?
A. PK는 각 행을 고유하게 식별하고, FK는 테이블 간 관계를 연결하며 참조 무결성을 보장합니다. 예: orders.menu_id → menus.id (FK). 존재하지 않는 메뉴를 주문할 수 없게 막아줍니다.

### 학습 목표 #2: ERD 설계 + SQL CREATE TABLE

Q3. ERD를 어떻게 설계했나요?
A. 식당 키오스크 주문 시스템으로 4개 테이블을 설계했습니다:
- **menu_categories** (메뉴 카테고리): id, name
- **store_tables** (매장 좌석): id, table_number, capacity
- **menus** (판매 메뉴): id, name, price, category_id(FK)
- **orders** (주문 기록): id, table_id(FK), menu_id(FK), quantity, order_time, status

관계:
- menu_categories 1:N menus (한 카테고리에 여러 메뉴)
- store_tables 1:N orders (한 테이블이 여러 주문)
- menus 1:N orders (한 메뉴가 여러 주문에 포함)

ERD 다이어그램은 `erd_diagram.png` 파일로 저장했습니다.

### 학습 목표 #3: JOIN, 집계, 서브쿼리 핵심 SQL

Q4. JOIN의 종류와 차이?
A. INNER JOIN=교집합(매칭되는 것만), LEFT JOIN=왼쪽 전체+오른쪽 매칭(없으면 NULL). 이 프로젝트에서:
- INNER JOIN: 주문 내역에 테이블 번호와 메뉴명 결합 (실시간 주방 모니터)
- LEFT JOIN: 전체 메뉴 기준으로 주문 결합 → "한 번도 주문되지 않은 메뉴" 탐색

Q5. 집계 쿼리를 어떻게 작성했나요?
A. GROUP BY + COUNT/SUM/AVG를 사용했습니다:
- `COUNT(m.id)` + `GROUP BY c.id`: 카테고리별 메뉴 개수
- `SUM(m.price * o.quantity)` + `GROUP BY t.id`: 테이블별 누적 매출
- `SUM(o.quantity)` + `HAVING SUM(o.quantity) >= 3`: 베스트셀러 메뉴 (3개 이상 팔린)

Q6. 서브쿼리를 어떻게 사용했나요?
A. 서브쿼리로 "가장 비싼 메뉴가 포함된 주문 내역"을 조회했습니다:
```sql
SELECT * FROM orders WHERE menu_id = (
    SELECT id FROM menus ORDER BY price DESC LIMIT 1
);
```
안쪽 쿼리가 가장 비싼 메뉴의 id를 찾고, 바깥 쿼리가 그 메뉴가 포함된 주문을 조회합니다.

### 학습 목표 #4: 순수 SQL로 데이터 관리

Q7. 백엔드 프레임워크를 금지한 이유가 뭔가요?
A. SQL을 직접 써서 원리를 이해하게 하기 위함입니다. ORM(SQLAlchemy, Django ORM 등)이 내부적으로 어떤 SQL을 만드는지 체득해야, 나중에 ORM을 쓸 때도 성능 문제를 이해할 수 있습니다. 이 프로젝트에서는 15개 쿼리를 순수 SQL로 작성했습니다.

### 기타

Q8. 인덱스는 언제 적용하나요?
A. 조회가 많고 삽입이 적은 컬럼에 적용합니다. 이 프로젝트에서는 `orders.status`에 인덱스를 만들었습니다 — 실시간 주방 디스플레이에서 조리 중인 주문을 주기적으로 필터링 조회하므로, status 컬럼 인덱스로 Full Scan을 방지합니다.
