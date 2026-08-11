# B5-1 동료평가 시나리오

## 1. 학습
- 테이블 설계 (PK/FK, 제약조건)
- 1:N 관계 (고객→주문, 메뉴→주문상세)
- JOIN (INNER, LEFT)
- GROUP BY (집계)
- 인덱스 (성능)

## 2. 고찰
- "엑셀과 DB의 차이는 관계" — 테이블 간 연결이 핵심
- "ORM이 해주는 일" — SQL 생성, 객체 매핑

## 3. 시도
- 도메인: 스마트 테이블 오더 시스템 (4개 테이블, 1:N 2개)
- CREATE TABLE + PK/FK/제약조건
- INSERT: 각 테이블 10행+
- 15개 쿼리: SELECT, JOIN, GROUP BY, 서브쿼리, UPDATE, DELETE

## 4. 수정
- 가격 TEXT → INTEGER (정렬/집계 정확)
- INNER JOIN만 → LEFT JOIN도 추가 (모든 고객 조회)

## 5. 선택과 선정
- SQLite vs MySQL: SQLite (설치 불필요, 파일 기반)
- INNER vs LEFT: 상황별 (모든 고객은 LEFT)
- 컬럼 타입: 가격=INTEGER, 이름=TEXT, 날짜=TEXT(ISO)

## 6. 트러블슈팅
- FK 제약 오류 → 부모 테이블 먼저 INSERT
- GROUP BY 오류 → 집계 안 된 컬럼 SELECT 금지
- 문자열 정렬 "10" < "2" → INTEGER로 변경

## 7. 평가 예상 질문
- PK/FK 필요성? → 무결성, 관계 연결
- 1:N 설명? → 한 고객→여러 주문
- JOIN 차이? → INNER=교집합, LEFT=왼쪽 전체
- 인덱스? → 조회 많고 삽입 적은 컬럼
