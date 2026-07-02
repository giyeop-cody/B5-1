-- ============================================================================
-- 파일명: 1_schema.sql
-- 설명: 스마트 테이블 오더 시스템 스키마 정의 스크립트 (DDL)
-- 도메인: 식당/술집 스마트 키오스크 주문 DB (Table Order Management DB)
-- 설계 기준: 각 테이블의 역할을 명확히 분리하고 참조 무결성 제약조건 적용
-- 대상 DB: SQLite 표준 문법 준수
-- ============================================================================

-- [SQLite 필수 설정]: 외래키 제약조건 검사 활성화
PRAGMA foreign_keys = ON;

-- 기존 테이블 삭제 (재현 가능성 보장: 관계 자식 테이블 -> 부모 테이블 순서로 삭제)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menus;
DROP TABLE IF EXISTS store_tables;
DROP TABLE IF EXISTS menu_categories;

-- ----------------------------------------------------------------------------
-- 1. 메뉴 카테고리 테이블 (menu_categories)
-- 역할: 메뉴 분류 체계 관리 및 명칭 중복 방지
-- ----------------------------------------------------------------------------
CREATE TABLE menu_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- 2. 매장 좌석 테이블 (store_tables)
-- 역할: 매장 내 좌석 번호 및 최대 수용 인원 관리
-- ----------------------------------------------------------------------------
CREATE TABLE store_tables (
    id INTEGER PRIMARY KEY,
    table_number INTEGER NOT NULL UNIQUE,
    capacity INTEGER NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. 판매 메뉴 테이블 (menus)
-- 역할: 메뉴 고유 명칭과 가격 정보 관리 (1:N 관계 ①)
-- ----------------------------------------------------------------------------
CREATE TABLE menus (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    CONSTRAINT fk_menu_category FOREIGN KEY (category_id) 
        REFERENCES menu_categories(id)
);

-- ----------------------------------------------------------------------------
-- 4. 주문 기록 테이블 (orders)
-- 역할: 좌석별 주문 시간, 수량, 조리 상태 기록 (1:N 관계 ②, ③)
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    table_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_time DATETIME NOT NULL,
    status TEXT NOT NULL, -- 상태 값: 'COOKING'(조리중), 'SERVED'(서빙완료), 'CANCELLED'(주문취소)
    CONSTRAINT fk_order_table FOREIGN KEY (table_id) 
        REFERENCES store_tables(id),
    CONSTRAINT fk_order_menu FOREIGN KEY (menu_id) 
        REFERENCES menus(id)
);
