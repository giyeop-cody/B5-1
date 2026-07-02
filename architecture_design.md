# 스마트 테이블 오더 데이터 모델링 및 스키마 설계서

> **프로젝트명**: 스마트 테이블 오더 시스템 데이터베이스 (Table Order Management DB)  
> **선정 도메인**: 외식 매장(식당/주점) 키오스크 및 태블릿 실시간 주문 데이터베이스  
> **설계 목표**: 각 테이블의 역할을 직관적으로 분리하고, 데이터 정합성과 참조 무결성을 보장하는 관계형 구조 설계

---

## 1. 데이터베이스 설계 기준 및 방향성

본 실습에서는 실제 매장 운영 서비스의 데이터 흐름을 반영하기 위해 아래의 기준을 바탕으로 스키마를 구성했습니다.

### ① 테이블의 역할에 따른 명확한 분리 (정규화)
하나의 표에 너무 많은 정보가 쏠려 중복 데이터나 수정 오류가 발생하지 않도록, 각 테이블이 **정확히 하나의 도메인 정보만 다루도록 구조화**했습니다.

* **`menu_categories` (메뉴 카테고리 테이블)**
  * 매장의 메뉴 분류 체계만 전담하여 관리하며, 카테고리 명칭 중복 가입을 막기 위해 `UNIQUE` 제약조건을 적용했습니다.
* **`store_tables` (매장 좌석 테이블)**
  * 매장 내 물리적인 좌석 번호와 최대 수용 인원수 정보만 다루며, 좌석 자체의 고유 속성만 유지합니다.
* **`menus` (판매 메뉴 테이블)**
  * 개별 상품의 고유 명칭과 판매 단가 정보를 관리하며, 소속 카테고리 ID를 외래키로 연결합니다.
* **`orders` (주문 기록 테이블)**
  * 좌석의 키오스크에서 주문이 들어오는 순간의 행위 기록(주문 시간, 주문 수량, 조리 상태)만 기록합니다. 메뉴 이름이나 좌석 정보를 중복 저장하지 않고 ID 참조만 수행합니다.

---

### ② 테이블 간 연관성 및 참조 무결성 유지
데이터베이스가 엑셀과 구분되는 핵심인 '테이블 간 관계'를 유기적으로 연결하기 위해 **1:N 관계 3개**를 수립했습니다.

1. `menu_categories(1) ───< menus(N)` : 하나의 카테고리에는 여러 개의 메뉴가 등록됩니다.
2. `store_tables(1) ───< orders(N)` : 하나의 매장 좌석에서는 시간 흐름에 따라 여러 번의 주문이 발생합니다.
3. `menus(1) ───< orders(N)` : 하나의 메뉴는 역대로 여러 좌석에서 중복 주문될 수 있습니다.

또한 외래키 제약조건(`FOREIGN KEY`)을 적용하여, 존재하지 않는 테이블 번호에서의 주문이나 삭제된 메뉴에 대한 비정상적인 주문 입력이 데이터베이스 엔진 단계에서 차단되도록 설계했습니다.

---

### ③ 목적에 따른 스크립트 파일 분리
실습 과제 가이드에 따라 파일 실행 순서와 목적을 엄격히 구분하여 3개의 `.sql` 스크립트로 분리 작성했습니다.

```text
[1_schema.sql] ──► 테이블 스키마 생성 및 PK/FK/NOT NULL 제약조건 정의 (DDL)
       │
[2_data.sql] ───► 각 테이블당 10행 이상의 초기 샘플 데이터 입력 (DML INSERT)
       │
[3_queries.sql] ──► 조회/조인/집계/서브쿼리/인덱스 등 핵심 요구 쿼리 15개 모음
```

---

## 2. 테이블 스키마 상세 명세표

| 테이블명 | 컬럼명 | 데이터 타입 | 제약조건 | 컬럼 설명 |
|:---|:---|:---|:---|:---|
| **menu_categories** | `id` | INTEGER | PK | 카테고리 고유 번호 |
| | `name` | TEXT | NOT NULL, UNIQUE | 카테고리명 (예: 시그니처 메인, 식사류) |
| **store_tables** | `id` | INTEGER | PK | 매장 좌석 고유 번호 |
| | `table_number` | INTEGER | NOT NULL, UNIQUE | 테이블 번호 (1번~12번 테이블) |
| | `capacity` | INTEGER | NOT NULL | 수용 가능 인원수 (2인석, 4인석 등) |
| **menus** | `id` | INTEGER | PK | 메뉴 고유 번호 |
| | `name` | TEXT | NOT NULL | 메뉴명 |
| | `price` | INTEGER | NOT NULL | 메뉴 단가 (원) |
| | `category_id` | INTEGER | NOT NULL, FK | 소속 카테고리 ID |
| **orders** | `id` | INTEGER | PK | 주문 번호 |
| | `table_id` | INTEGER | NOT NULL, FK | 주문한 좌석 ID |
| | `menu_id` | INTEGER | NOT NULL, FK | 주문된 메뉴 ID |
| | `quantity` | INTEGER | NOT NULL | 주문 수량 |
| | `order_time` | DATETIME | NOT NULL | 주문 일시 |
| | `status` | TEXT | NOT NULL | 주문 상태 ('COOKING', 'SERVED', 'CANCELLED') |

---

## 3. ERD 다이어그램 텍스트 명세 (dbdiagram.io DBML 문법)

아래의 DBML 코드를 `dbdiagram.io`에 복사하여 붙여넣으시면 시각화된 테이블 관계도를 확인하실 수 있습니다.

```dbml
Table menu_categories {
  id integer [primary key]
  name text [not null, unique]
}

Table store_tables {
  id integer [primary key]
  table_number integer [not null, unique]
  capacity integer [not null]
}

Table menus {
  id integer [primary key]
  name text [not null]
  price integer [not null]
  category_id integer [not null, ref: > menu_categories.id]
}

Table orders {
  id integer [primary key]
  table_id integer [not null, ref: > store_tables.id]
  menu_id integer [not null, ref: > menus.id]
  quantity integer [not null]
  order_time datetime [not null]
  status text [not null]
}
```
