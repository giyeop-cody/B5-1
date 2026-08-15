# B5-1 외부 동료평가 요청서

## 상태

**외부 평가 대기 중**

이 문서는 평가자가 직접 실행하고 의견을 남기기 위한 양식이다. 아래의 평가자·일시·의견 칸이 비어 있는 것은 의도한 상태이며, 구현자가 외부 평가를 받은 것처럼 대신 작성하지 않는다.

## 평가 대상

- 프로젝트: 스마트 테이블 오더 SQLite DB
- 범위: 테이블 4개, seed, 핵심 SQL 15개, 보너스, 증거, 학습·문제 처리 기록
- 제외: 백엔드 API/UI, View, 프로시저, 트리거
- 기준 브랜치/커밋: 평가 시작 시 평가자가 직접 기록

## 평가 전 읽을 자료

1. `QUEST.md` — 공식 미션 요구사항
2. `README.md` — 실행법과 결과 요약
3. `architecture_design.md` — 스키마와 관계
4. `docs/learning-journal.md` — 학습 순서
5. `docs/decision-log.md` — 선택지와 트레이드오프
6. `docs/development-log.md` — 트러블슈팅
7. `docs/issue-handling-log.md` — GitHub Issue 연결
8. `bonus_report.md` — 보너스 검증

## 평가자가 실행할 명령

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
python scripts/verify_project.py
python -m pip install -r requirements-dev.txt
scripts/check_all.sh
git status --short
```

기대 문구:

```text
B5-1 AUTOMATED VERIFICATION: ALL PASS
B5-1 CHECK ALL: PASS
```

## 미션 체크리스트

### 데이터 모델

- [ ] 테이블이 4개 이상이다.
- [ ] 모든 테이블에 PK가 있다.
- [ ] FK와 1:N 관계가 2개 이상이다.
- [ ] 테이블·컬럼 이름이 역할을 나타낸다.
- [ ] 현재 ERD와 DDL이 일치한다.

### 제약조건과 데이터

- [ ] 각 테이블 seed가 10행 이상이다.
- [ ] NOT NULL과 UNIQUE가 실제 DDL에 있다.
- [ ] FK가 없는 부모 참조를 차단한다.
- [ ] CHECK가 음수 수량과 잘못된 상태를 차단한다.

### 핵심 SQL

- [ ] 총 15개 SQL이 있다.
- [ ] 기본 조회 4개 이상이다.
- [ ] JOIN 4개 이상이며 INNER 2개, LEFT 1개 이상이다.
- [ ] 집계 3개 이상이며 COUNT/SUM/AVG 중 2개 이상을 사용한다.
- [ ] 서브쿼리 1개 이상이다.
- [ ] UPDATE와 DELETE가 있다.
- [ ] 인덱스 1개와 적용 이유가 있다.
- [ ] Q13/Q14가 현재 상태까지 확인한다.

### 결과와 보너스

- [ ] Q1~Q15 텍스트와 PNG가 실제 SQL·결과와 일치한다.
- [ ] JOIN/서브쿼리의 전체 결과 집합이 같다.
- [ ] FK 위반 실패 이유와 수정 방법이 설명되어 있다.
- [ ] KPI 3개의 SQL·이름·계산 단위·결과가 서로 맞는다.
- [ ] 성능 설명이 현재 EXPLAIN 결과 범위를 넘지 않는다.

### 학습 과정

- [ ] 입문자가 이해할 수 있는 순서로 개념이 기록되어 있다.
- [ ] 선택지의 장점·단점·결정 이유가 있다.
- [ ] 문제 재현·원인·수정·재검증이 연결되어 있다.
- [ ] GitHub Issue와 커밋으로 추적할 수 있다.
- [ ] 존재하지 않는 고객·주문상세 도메인을 현재 구현처럼 설명하지 않는다.

## 평가자 기록란

- 평가자 이름 또는 GitHub ID:
- 평가 일시:
- 평가한 브랜치:
- 평가한 전체 commit SHA:
- 운영체제:
- Python 버전:
- SQLite 버전:
- `verify_project.py` 결과:
- `check_all.sh` 결과:

## 의견

### 잘된 점

-

### 수정이 필요한 점

-

### 질문

-

### 최종 판단

- [ ] 통과
- [ ] 수정 후 재검토
- [ ] 미통과

평가자 서명 또는 확인 링크:
