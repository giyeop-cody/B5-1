-- ============================================================================
-- 파일명: 1_schema.sql
-- 설명: 스마트 테이블 오더 시스템 스키마 정의 스크립트 (DDL)
-- 대상 DB: SQLite 3
-- 주의: PRAGMA와 SQLite의 유연한 DATETIME 타입은 SQLite 전용 동작이다.
-- ============================================================================

-- SQLite는 연결마다 외래키 검사가 기본 비활성일 수 있으므로 명시적으로 켠다.
PRAGMA foreign_keys = ON;

-- 자식에서 부모 순서로 삭제해 스크립트를 처음부터 다시 실행할 수 있게 한다.
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menus;
DROP TABLE IF EXISTS store_tables;
DROP TABLE IF EXISTS menu_categories;

-- 메뉴 카테고리: 하나의 카테고리에 여러 메뉴가 속한다.
CREATE TABLE menu_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 매장 좌석: table_number는 실제 매장 안에서 중복될 수 없다.
CREATE TABLE store_tables (
    id INTEGER PRIMARY KEY,
    table_number INTEGER NOT NULL UNIQUE CHECK (table_number > 0),
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

-- 판매 메뉴: 가격은 원화 정수이며 음수가 될 수 없다.
CREATE TABLE menus (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    category_id INTEGER NOT NULL,
    CONSTRAINT fk_menu_category
        FOREIGN KEY (category_id) REFERENCES menu_categories(id)
);

-- 주문 기록: 이 과제에서는 한 행을 하나의 메뉴 주문 항목으로 다룬다.
-- SQLite DATETIME은 별도 저장 클래스가 아니므로 ISO 8601 문자열을 일관되게 입력한다.
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    table_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    order_time DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('COOKING', 'SERVED', 'CANCELLED')),
    CONSTRAINT fk_order_table
        FOREIGN KEY (table_id) REFERENCES store_tables(id),
    CONSTRAINT fk_order_menu
        FOREIGN KEY (menu_id) REFERENCES menus(id)
);
