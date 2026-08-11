# B5-1 학습 노트: 정보를 깔끔하게 정리하는 디지털 서랍장 만들기

> 문과 중졸도 이해할 수 있게

## 📖 목차
1. 초심자를 위한 용어집
2. 과제 해석 및 분석
3. 과제를 진행하기 위한 기초
4. 각 기초를 익히기 위한 간단한 체험 예제
5. 과제를 작게 쪼개기
6. 워크플로우별 트레이드오프, 이슈, 트러블슈팅
7. 과제 완료 후 학습한 내용 정리

## 1. 초심자를 위한 용어집

| 용어 | 설명 | 비유 |
|------|------|------|
| 데이터베이스 | 데이터를 체계적으로 저장하는 공간 | 큰 서랍장 |
| 테이블 | 같은 종류의 데이터를 모아둔 곳 | 서랍장의 한 칸 |
| PK (기본키) | 각 행을 고유하게 식별하는 키 | 주민등록번호 |
| FK (외래키) | 다른 테이블을 가리키는 키 | "작성자: 홍길동" 표시 |
| 1:N 관계 | 한 쪽이 하나, 다른 쪽이 여럿 | 한 명 작성자 → 여러 글 |
| JOIN | 두 테이블을 연결하여 조회 | 두 서랍의 내용을 합쳐서 보기 |
| GROUP BY | 그룹별로 집계 | 반별 평균 계산 |
| 인덱스 | 빠른 검색을 위한 색인 | 책의 색인 페이지 |
| SQL | 데이터베이스에 명령하는 언어 | 서랍장 관리사에게 주문 |

## 2. 과제 해석
한 줄: 프레임워크 없이 SQL을 직접 작성하여 도메인 DB를 설계하라.
핵심: "ORM이 무엇을 해주는지 이해하기 위해 먼저 SQL을 직접 써보기"

## 3. 기초
1. DB 개념 (테이블, 행, 열, 관계)
2. SQL 기본 (CREATE, INSERT, SELECT)
3. 관계 (PK, FK, 1:N)
4. JOIN (INNER, LEFT)
5. 집계 (GROUP BY, COUNT, SUM)
6. 서브쿼리, 인덱스

## 4. 체험 예제
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

## 5. 잡/워크
- Job 1: 도메인 선택 + 테이블 설계 (4개, 1:N 2개)
- Job 2: 스키마 생성 (CREATE TABLE)
- Job 3: 샘플 데이터 입력 (각 10행+)
- Job 4: 핵심 쿼리 15개 작성

## 6. 트레이드오프
- SQLite vs MySQL: SQLite (설치 불필요, 파일 기반)
- INNER vs LEFT JOIN: 상황별 (모든 고객은 LEFT)
- 컬럼 타입: 가격=INTEGER (정렬/집계 정확)

## 7. 학습 정리
- "엑셀과 DB의 차이는 관계" — 테이블 간 연결이 핵심
- "ORM이 해주는 일" — SQL 생성, 객체 매핑
