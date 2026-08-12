# B5-1 학습 노트: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기

> 문과 중졸도 이해할 수 있게

## 📖 목차

1. 초심자를 위한 용어집
2. 과제 해석 및 분석
3. DB와 DBMS
4. SQL 개념 (DDL, DML, DCL, TCL)
5. 쿼리 문의 의미와 동작과 사용
6. DB 정규화
7. ORM이란?
8. 과제를 진행하기 위한 기초
9. 각 기초를 익히기 위한 간단한 체험 예제
10. 과제를 작게 쪼개기
11. 워크플로우별 트레이드오프, 이슈, 트러블슈팅
12. 과제 완료 후 학습한 내용 정리

---

## 1. 초심자를 위한 용어집

| 용어 | 설명 | 비유 |
|------|------|------|
| 데이터베이스 (DB) | 데이터를 체계적으로 저장하는 공간 | 큰 서랍장 |
| DBMS | DB를 관리하는 소프트웨어 | 서랍장 관리사 |
| 테이블 | 같은 종류의 데이터를 모아둔 곳 | 서랍장의 한 칸 |
| 행(Row) | 하나의 데이터 단위 | 서랍 안의 한 장의 카드 |
| 열(Column) | 데이터의 속성 | 카드의 "이름", "가격" 항목 |
| PK (기본키) | 각 행을 고유하게 식별하는 키 | 주민등록번호 |
| FK (외래키) | 다른 테이블을 가리키는 키 | "작성자: 홍길동" 표시 |
| 1:N 관계 | 한 쪽이 하나, 다른 쪽이 여럿 | 한 명 작성자 → 여러 글 |
| JOIN | 두 테이블을 연결하여 조회 | 두 서랍의 내용을 합쳐서 보기 |
| GROUP BY | 그룹별로 집계 | 반별 평균 계산 |
| 인덱스 | 빠른 검색을 위한 색인 | 책의 색인 페이지 |
| SQL | 데이터베이스에 명령하는 언어 | 서랍장 관리사에게 주문 |
| 정규화 | 데이터 중복을 제거하는 과정 | 서랍을 정리해서 같은 물건이 여러 군데 흩어지지 않게 함 |
| ORM | SQL을 직접 안 쓰고 코드로 DB 조작 | 번역기를 써서 외국어를 모르고도 소통 |

---

## 2. 과제 해석

한 줄: 프레임워크 없이 SQL을 직접 작성하여 도메인 DB를 설계하라.
핵심: "ORM이 무엇을 해주는지 이해하기 위해 먼저 SQL을 직접 써보기"

---

## 3. DB와 DBMS

### DB (Database)란?

**데이터를 체계적으로 저장하고 관리하는 공간**입니다.

엑셀과 비슷해 보이지만 핵심 차이는 **관계**입니다. 엑셀은 시트마다 독립적이지만, DB는 테이블 간에 관계(FK)를 맺어 데이터가 중복되지 않게 합니다.

| | 엑셀 | DB |
|---|------|-----|
| 저장 | 시트 | 테이블 |
| 관계 | 수동으로 VLOOKUP | FK로 자동 연결 |
| 중복 | 복사붙여넣기 → 중복 발생 | 정규화 → 중복 제거 |
| 동시성 | 한 명만 편집 | 여러 명 동시 접근 |
| 검색 | Ctrl+F | SQL (정확한 조건 검색) |

### DBMS (Database Management System)란?

**DB를 관리하는 소프트웨어**입니다. 사용자가 SQL로 명령을 내리면 DBMS가 실제로 데이터를 저장/조회/수정/삭제합니다.

| DBMS | 특징 | 용도 |
|------|------|------|
| **SQLite** | 파일 기반, 설치 불필요, 가벼움 | 개발/소규모 (이 과제에서 사용) |
| **MySQL** | 서버 기반, 동시성 강함 | 웹 서비스 |
| **PostgreSQL** | 서버 기반, 기능 풍부, 표준 준수 | 대규모/복잡한 서비스 |
| **Oracle** | 상용, 엔터프라이즈 | 대기업 |

비유: DB는 "서랍장", DBMS는 "서랍장 관리사"입니다. 관리사에게 "가격 2만원 이상 메뉴 찾아줘"라고 명령(SQL)하면, 관리사가 직접 뒤져서 가져다 줍니다.

---

## 4. SQL 개념 (DDL, DML, DCL, TCL)

SQL은 4가지 종류로 나뉩니다:

### DDL (Data Definition Language) — 데이터 구조 정의

"서랍장의 칸을 만들고, 고치고, 없애는" 명령입니다.

| 명령 | 의미 | 예시 |
|------|------|------|
| `CREATE TABLE` | 테이블 생성 | `CREATE TABLE menus (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);` |
| `ALTER TABLE` | 테이블 구조 변경 | `ALTER TABLE menus ADD COLUMN description TEXT;` |
| `DROP TABLE` | 테이블 삭제 | `DROP TABLE menus;` |

```sql
-- 이 과제에서 사용한 DDL
CREATE TABLE menu_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE menus (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    CONSTRAINT fk_menu_category FOREIGN KEY (category_id)
        REFERENCES menu_categories(id)
);
```

### DML (Data Manipulation Language) — 데이터 조작

"서랍 안의 카드를 넣고, 찾고, 고치고, 빼는" 명령입니다. **가장 많이 쓰는 SQL**입니다.

| 명령 | 의미 | 예시 |
|------|------|------|
| `INSERT` | 데이터 삽입 | `INSERT INTO menus (name, price) VALUES ('비빔밥', 15000);` |
| `SELECT` | 데이터 조회 | `SELECT name, price FROM menus WHERE price >= 20000;` |
| `UPDATE` | 데이터 수정 | `UPDATE orders SET status = 'SERVED' WHERE id = 18;` |
| `DELETE` | 데이터 삭제 | `DELETE FROM orders WHERE status = 'CANCELLED';` |

```sql
-- 이 과제에서 사용한 DML
INSERT INTO menu_categories (id, name) VALUES (1, '소주');
INSERT INTO menus (id, name, price, category_id) VALUES (1, '새로주 원본', 4500, 1);

SELECT name, price FROM menus WHERE price >= 20000 ORDER BY price DESC LIMIT 5;

UPDATE orders SET status = 'SERVED' WHERE id = 18;
DELETE FROM orders WHERE id = 25;
```

### DCL (Data Control Language) — 권한 제어

"누가 서랍장을 열 수 있는지" 제어합니다. 이 과제에서는 사용하지 않습니다.

| 명령 | 의미 |
|------|------|
| `GRANT` | 권한 부여 |
| `REVOKE` | 권한 회수 |

### TCL (Transaction Control Language) — 트랜잭션 제어

"여러 명령을 하나의 작업 단위로 묶어서, 전부 성공하거나 전부 취소"합니다.

| 명령 | 의미 |
|------|------|
| `BEGIN` | 트랜잭션 시작 |
| `COMMIT` | 변경사항 확정 |
| `ROLLBACK` | 변경사항 취소 |

비유: "계좌이체" = 돈 빼기 + 돈 넣기. 하나라도 실패하면 전체 취소(ROLLBACK).

---

## 5. 쿼리 문의 의미와 동작과 사용

### SELECT — 데이터 조회

```sql
-- 기본: 모든 메뉴 조회
SELECT * FROM menus;

-- 조건: 2만원 이상 메뉴만
SELECT name, price FROM menus WHERE price >= 20000;

-- 정렬 + 제한: 비싼 순 상위 5개
SELECT name, price FROM menus WHERE price >= 20000 ORDER BY price DESC LIMIT 5;

-- 패턴 검색: '전골'이 포함된 메뉴
SELECT name, price FROM menus WHERE name LIKE '%전골%';
```

### JOIN — 테이블 연결

```sql
-- INNER JOIN: 양쪽 다 매칭되는 것만
SELECT t.table_number, m.name, o.quantity
FROM orders o
INNER JOIN store_tables t ON o.table_id = t.id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED';
-- 의미: "취소되지 않은 주문의 테이블번호, 메뉴명, 수량을 합쳐서 보여줘"

-- LEFT JOIN: 왼쪽은 전부, 오른쪽은 매칭되는 것만
SELECT m.id, m.name, m.price
FROM menus m
LEFT JOIN orders o ON m.id = o.menu_id
WHERE o.id IS NULL;
-- 의미: "한 번도 주문되지 않은 메뉴를 찾아줘"
```

**INNER vs LEFT 차이**:
- INNER: 교집합 (매칭되는 것만)
- LEFT: 왼쪽 전체 + 오른쪽 매칭 (없으면 NULL)

### GROUP BY + 집계 — 그룹별 통계

```sql
-- 카테고리별 메뉴 개수와 평균 가격
SELECT c.name AS category_name, COUNT(m.id) AS menu_count, ROUND(AVG(m.price), 0) AS avg_price
FROM menu_categories c
INNER JOIN menus m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY menu_count DESC;
-- 의미: "카테고리별로 메뉴가 몇 개 있고 평균 가격은 얼마인가?"

-- 테이블별 누적 매출
SELECT t.table_number, SUM(m.price * o.quantity) AS total_bill
FROM store_tables t
INNER JOIN orders o ON t.id = o.table_id
INNER JOIN menus m ON o.menu_id = m.id
WHERE o.status != 'CANCELLED'
GROUP BY t.id, t.table_number
ORDER BY total_bill DESC;

-- HAVING: 그룹에 대한 조건 (WHERE는 행에 대한 조건)
SELECT m.name, SUM(o.quantity) AS total_sold
FROM menus m
INNER JOIN orders o ON m.id = o.menu_id
WHERE o.status = 'SERVED'
GROUP BY m.id, m.name
HAVING SUM(o.quantity) >= 3;
-- 의미: "3개 이상 팔린 메뉴만"
```

### 서브쿼리 — 쿼리 안의 쿼리

```sql
-- 가장 비싼 메뉴가 포함된 주문
SELECT * FROM orders
WHERE menu_id = (
    SELECT id FROM menus ORDER BY price DESC LIMIT 1
);
-- 안쪽: 가장 비싼 메뉴의 id 찾기
-- 바깥: 그 메뉴가 포함된 주문 조회
```

### UPDATE — 데이터 수정

```sql
UPDATE orders SET status = 'SERVED' WHERE id = 18;
-- 의미: "18번 주문의 상태를 서빙 완료로 바꿔줘"
```

### DELETE — 데이터 삭제

```sql
DELETE FROM orders WHERE id = 25;
-- 의미: "25번 주문 기록을 삭제해줘"
```

### CREATE INDEX — 검색 속도 향상

```sql
CREATE INDEX idx_order_status ON orders (status);
-- 의미: orders 테이블의 status 컬럼에 색인(인덱스)을 만들어서
-- "status = 'COOKING'" 같은 조회를 빠르게 함
```

---

## 6. DB 정규화

### 정규화란?

**데이터 중복을 제거하고 무결성을 보장하기 위해 테이블을 나누는 과정**입니다.

비유: "양말이 옷장, 서랍, 현관에 각각 흩어져 있으면 찾기 어렵다. 양말은 양말 칸에 모아두자."

### 왜 하는가?

**문제 상황** (정규화 안 함):
```
orders 테이블에 메뉴 이름과 가격을 직접 넣는 경우:
주문1: 비빔밥, 15000원
주문2: 비빔밥, 15000원
주문3: 비빔밥, 15000원
→ "비빔밥"이 3번 중복됨

메뉴 가격이 15000 → 16000으로 오르면?
→ 3곳을 다 수정해야 함 (하나라도 빠지면 데이터 불일치)
```

**정규화 후**:
```
menus 테이블: id=1, 비빔밥, 15000원 (한 번만 저장)
orders 테이블: menu_id=1 (참조만)
→ 가격이 오르면 menus 1곳만 수정하면 됨
```

### 어떻게 하는가?

**중복되는 데이터를 별도 테이블로 분리하고, 원래 테이블은 FK로 참조**합니다.

이 과제에서:
- 메뉴 카테고리명이 중복 → `menu_categories` 테이블로 분리
- 메뉴 정보가 주문마다 중복 → `menus` 테이블로 분리, `orders`는 `menu_id`로 참조

### 정규화 종류

| 단계 | 이름 | 규칙 | 예시 |
|------|------|------|------|
| **1NF** | 제1정규형 | 하나의 칸에는 하나의 값만 | "전골, 철판" → 행 2개로 분리 |
| **2NF** | 제2정규형 | 부분 종속 제거 (복합키의 일부에만 종속되는 컬럼 제거) | 주문_메뉴 복합키에서 메뉴명은 메뉴id에만 종속 → menus 테이블로 분리 |
| **3NF** | 제3정규형 | 이행 종속 제거 (A→B→C 제거) | 회원id → 우편번호 → 주소 → 주소 테이블로 분리 |

**이 과제에서 달성한 정규화 수준**: 3NF (모든 비키 컬럼이 기본키에만 직접 종속)

### 정규화 트레이드오프

| | 정규화 (분리) | 비정규화 (합침) |
|---|---|---|
| 장점 | 중복 제거, 무결성 보장 | 조회 속도 빠름 (JOIN 감소) |
| 단점 | JOIN 많아짐 → 조회 느려질 수 있음 | 중복 발생, 수정 시 여러 곳 변경 |
| 언제? | 기본 (트랜잭션 무결성 중요) | 읽기 많은 서비스 (성능 중요) |

비유: 정규화는 "물건을 종류별로 정리" (찾을 때 여러 서랍 뒤져야 함), 비정규화는 "자주 쓰는 물건은 책상 위" (빠르지만 정리가 안 됨).

---

## 7. ORM이란?

### ORM (Object-Relational Mapping)

**SQL을 직접 안 쓰고, 코드(객체)로 DB를 조작하는 기술**입니다.

비유: "외국어(SQL)를 모르고도 번역기(ORM)를 쓰면 소통할 수 있다."

### SQL vs ORM 비교

```python
# SQL (직접 작성 — 이 과제에서 한 방식)
SELECT name, price FROM menus WHERE price >= 20000 ORDER BY price DESC LIMIT 5;

# ORM (SQLAlchemy — B5-2에서 사용할 방식)
db.query(Menu).filter(Menu.price >= 20000).order_by(Menu.price.desc()).limit(5).all()
```

```python
# SQL
INSERT INTO menus (name, price, category_id) VALUES ('비빔밥', 15000, 1);

# ORM
menu = Menu(name='비빔밥', price=15000, category_id=1)
db.add(menu)
db.commit()
```

### ORM의 장단점

| | ORM | SQL 직접 작성 |
|---|-----|-------------|
| 장점 | 코드가 직관적, SQL 모를 때도 가능, 자동 검증 | 정확한 제어, 복잡한 쿼리 쉬움 |
| 단점 | 복잡한 쿼리는 어려움, 성능 튜닝 제한 | SQL 문법 알아야 함 |
| 비유 | 자동변속기 (쉽지만 제한적) | 수동변속기 (어렵지만 정밀) |

### 왜 이 과제에서 ORM을 금지했는가?

**ORM이 내부적으로 어떤 SQL을 만드는지 이해하려면, 먼저 SQL을 직접 써봐야 하기 때문**입니다.

나중에 SQLAlchemy(Django ORM, JPA 등)를 쓸 때:
- ORM이 만든 SQL이 느리면 → 원인을 이해하고 최적화할 수 있음
- N+1 문제(쿼리가 너무 많이 나가는 문제) → JOIN으로 해결할 수 있음
- 이 과제에서 SQL을 직접 작성한 경험이 이해의 기초가 됨

### 대표적인 ORM

| 언어 | ORM | 프레임워크 |
|------|-----|-----------|
| Python | SQLAlchemy | FastAPI, Flask |
| Python | Django ORM | Django |
| Java | JPA/Hibernate | Spring |
| JavaScript | Prisma, Sequelize | Node.js |
| Ruby | ActiveRecord | Ruby on Rails |

---

## 8. 과제를 진행하기 위한 기초

1. 도메인 선택 (식당 키오스크)
2. 테이블 설계 (4개, 1:N 관계 3개)
3. CREATE TABLE (PK, FK, 제약조건)
4. INSERT (샘플 데이터 각 10행+)
5. SELECT (기본 조회, WHERE, ORDER BY)
6. JOIN (INNER, LEFT)
7. 집계 (GROUP BY, COUNT, SUM, AVG)
8. 서브쿼리, UPDATE, DELETE, 인덱스

## 9. 체험 예제

### 테이블 생성
```sql
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id));
```

### JOIN
```sql
SELECT c.name, o.id FROM customers c
JOIN orders o ON c.id = o.customer_id;
```

## 10. 잡/워크
- Job 1: 도메인 선택 + 테이블 설계 (4개, 1:N 2개)
- Job 2: 스키마 생성 (CREATE TABLE)
- Job 3: 샘플 데이터 입력 (각 10행+)
- Job 4: 핵심 쿼리 15개 작성

## 11. 트레이드오프
- SQLite vs MySQL: SQLite (설치 불필요, 파일 기반)
- INNER vs LEFT JOIN: 상황별 (모든 고객은 LEFT)
- 컬럼 타입: 가격=INTEGER (정렬/집계 정확)
- 정규화 vs 비정규화: 기본은 정규화, 읽기 성능 필요시 비정규화

## 12. 학습 정리
- "엑셀과 DB의 차이는 관계" — 테이블 간 연결이 핵심
- "ORM이 해주는 일" — SQL 생성, 객체 매핑, 자동 검증
- "정규화는 중복 제거" — 데이터 무결성을 위해 테이블을 나눔
- "DDL은 구조, DML은 데이터" — CREATE/ALTER/DROP vs INSERT/SELECT/UPDATE/DELETE
- "JOIN은 테이블 연결" — INNER(교집합), LEFT(왼쪽 전체)
- "GROUP BY는 그룹별 통계" — COUNT/SUM/AVG + HAVING
- "인덱스는 색인" — 조회 빠르게, 삽입 느려질 수 있음
