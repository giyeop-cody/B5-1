# B5-1 동료평가 설명 시나리오

## 1. 학습

처음에는 다음 순서로 배웠다.

1. 테이블·행·열
2. PK·FK
3. 1:N 관계
4. WHERE·ORDER BY·LIMIT
5. INNER JOIN·LEFT JOIN
6. COUNT·SUM·AVG·GROUP BY
7. 서브쿼리
8. UPDATE·DELETE·인덱스
9. 무결성 실패 실험

## 2. 고찰

- 엑셀과 DB의 핵심 차이를 단순 데이터 크기가 아니라 관계와 규칙으로 이해했다.
- 문서에 CHECK가 있다고 쓰는 것보다 잘못된 값을 직접 넣어 차단되는지 확인하는 것이 중요했다.
- 스크린샷은 SQL이 바뀌면 낡을 수 있어 같은 새 DB 실행에서 다시 만들어야 했다.

## 3. 시도

스마트 테이블 오더 도메인에 현재 존재하는 테이블은 네 개다.

- `menu_categories`
- `store_tables`
- `menus`
- `orders`

실제 1:N 관계는 세 개다.

- `menu_categories → menus`
- `store_tables → orders`
- `menus → orders`

각 테이블에 10행 이상을 넣고 핵심 SQL 15개와 보너스 SQL 5개를 실행했다.

## 4. 수정

감사 뒤 다음을 실제 코드에 반영했다.

- 40시간·실제 파일명·SQLite 타입 설명 정정
- 가격·좌석·수용 인원·수량·상태 CHECK 추가
- Query 7/8의 의미와 seed 일치
- Query 13/14에 예상 현재 상태 조건 추가
- Query 1~15 결과 텍스트와 PNG 재생성
- Query 5/9/12 문서와 실제 SQL 일치
- ERD 오기 수정
- JOIN/서브쿼리 전체 결과 값 비교
- KPI 3종 SQL과 결과 생성

## 5. 선택과 선정

- SQLite: 서버 없이 재현하기 쉬워 입문 실습에 선택
- 주문 한 행: 현재 과제에서는 메뉴 한 항목으로 유지
- 날짜: ISO 형식 문자열을 일관되게 사용
- Q12의 `IN`: 최고가 동률 메뉴도 처리
- 물리 테이블 평균: 좌석별 매출을 먼저 만든 뒤 수용 인원별 평균 계산
- 외부 평가: 실제 평가 전에는 대기 상태로 유지

상세 장단점은 `docs/decision-log.md`에 있다.

## 6. 트러블슈팅

- FK가 연결마다 꺼질 수 있음 → `PRAGMA foreign_keys = ON`
- 음수 quantity와 잘못된 status가 허용됨 → CHECK 추가
- LEFT JOIN 미매칭 메뉴가 없음 → 미주문 `유자차` seed 추가
- UPDATE가 ID만 확인함 → 현재 상태도 조건에 추가
- 증거의 임시 DB 경로가 매번 바뀜 → 무작위 경로를 결과에서 제거

상세 재현과 검증은 `docs/development-log.md`에 있다.

## 7. 시연 순서

1. `erd_diagram.png`로 네 테이블·세 관계 설명
2. `1_schema.sql`에서 PK·FK·CHECK 확인
3. Q5로 INNER JOIN 설명
4. Q7로 LEFT JOIN 미매칭 설명
5. Q9로 GROUP BY 설명
6. Q12로 서브쿼리 설명
7. Q13/Q14로 안전한 변경 설명
8. `evidence/bonus_02_fk_error_test.txt`로 무결성 실패 설명
9. `scripts/check_all.sh` 실행
10. 평가자가 `docs/peer-evaluation-request.md`를 직접 작성
