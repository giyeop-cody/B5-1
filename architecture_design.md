# 스마트 테이블 오더 데이터 모델링 및 스키마 설계서

## 1. 설계 범위

- DBMS: SQLite 3
- 테이블: 4개
- 1:N 관계: 3개
- 한 `orders` 행의 의미: 한 좌석에서 주문한 메뉴 한 항목
- 고급 View·프로시저·트리거: 사용하지 않음

SQLite는 별도 DATETIME 저장 클래스가 없고 선언형이 유연하다. 이 프로젝트는 `order_time`에 `YYYY-MM-DD HH:MM:SS` ISO 형식 문자열을 일관되게 입력한다. 연결마다 `PRAGMA foreign_keys = ON`을 실행해야 FK 검사가 활성화된다.

## 2. 테이블 역할

1. `menu_categories`: 메뉴 분류 이름
2. `store_tables`: 매장 좌석 번호와 수용 인원
3. `menus`: 메뉴명·가격·카테고리
4. `orders`: 좌석·메뉴·수량·시간·조리 상태

주문 행에는 메뉴명·가격·좌석 번호를 복사하지 않고 FK만 저장해 중복을 줄인다.

## 3. 관계

- `menu_categories(1) → menus(N)`
- `store_tables(1) → orders(N)`
- `menus(1) → orders(N)`

FK는 존재하지 않는 카테고리·좌석·메뉴 참조를 차단한다.

## 4. 스키마 명세

| 테이블 | 컬럼 | 타입 | 제약조건 | 의미 |
|---|---|---|---|---|
| menu_categories | id | INTEGER | PK | 카테고리 ID |
| | name | TEXT | NOT NULL, UNIQUE | 카테고리명 |
| store_tables | id | INTEGER | PK | 좌석 ID |
| | table_number | INTEGER | NOT NULL, UNIQUE, CHECK > 0 | 실제 좌석 번호 |
| | capacity | INTEGER | NOT NULL, CHECK > 0 | 수용 인원 |
| menus | id | INTEGER | PK | 메뉴 ID |
| | name | TEXT | NOT NULL | 메뉴명 |
| | price | INTEGER | NOT NULL, CHECK >= 0 | 원화 가격 |
| | category_id | INTEGER | NOT NULL, FK | 카테고리 참조 |
| orders | id | INTEGER | PK | 주문 항목 ID |
| | table_id | INTEGER | NOT NULL, FK | 좌석 참조 |
| | menu_id | INTEGER | NOT NULL, FK | 메뉴 참조 |
| | quantity | INTEGER | NOT NULL, CHECK > 0 | 수량 |
| | order_time | DATETIME | NOT NULL | ISO 형식 주문 시각 |
| | status | TEXT | NOT NULL, CHECK IN | COOKING/SERVED/CANCELLED |

## 5. 무결성 방어선

- PK: 행 식별과 중복 방지
- UNIQUE: 카테고리명·좌석 번호 중복 방지
- FK: 존재하지 않는 부모 참조 차단
- CHECK: 음수 가격·수용 인원·수량, 잘못된 상태 차단
- NOT NULL: 필수값 누락 차단

자동 검증은 FK, CHECK, UNIQUE 위반 입력이 모두 `sqlite3.IntegrityError`로 거절되는지 확인한다.

## 6. 실행 순서

```text
1_schema.sql → 2_data.sql → 3_queries.sql → 4_bonus_queries.sql(선택)
```

- `1_schema.sql`: 기존 테이블을 자식부터 제거하고 재생성
- `2_data.sql`: 부모 → 자식 순서로 데이터 입력
- `3_queries.sql`: 필수 15개
- `4_bonus_queries.sql`: JOIN/서브쿼리 비교와 KPI 3개

## 7. ERD

![스마트 테이블 오더 ERD](erd_diagram.png)

이미지는 `python scripts/generate_erd.py`로 현재 스키마 설명에 맞춰 다시 생성할 수 있다.

## 8. 장기 확장 시 고려

현재 `orders`는 주문 메뉴 한 줄을 뜻한다. 실제 결제 한 건에 여러 메뉴를 묶고 결제 상태를 관리해야 한다면 다음 단계에서 `orders`(주문 헤더)와 `order_items`(주문 항목)로 나눈다. 이는 현재 B5-1 최소 범위에는 포함하지 않는다.
