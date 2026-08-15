# GitHub Issue 처리 기록

저장소: `giyeop-cody/B5-1`

이 문서는 감사 중 발견한 문제를 “발견 → 원인 → 수정 → 검증” 순서로 연결한다. 실제 Issue 상태는 GitHub를 기준으로 한다.

## Issue #1 — 미션 메타데이터·실행 안내 불일치

- URL: <https://github.com/giyeop-cody/B5-1/issues/1>
- 발견:
  - 공식 PDF는 학습 시간 40시간인데 기존 설명이 달랐다.
  - 안내 파일명과 실제 `1_schema.sql`·`2_data.sql`·`3_queries.sql`이 달랐다.
  - SQLite DATETIME과 FK 동작 설명이 부족했다.
- 원인: 파일과 문서를 따로 수정해 동기화가 깨졌다.
- 처리:
  - README·QUEST를 공식 PDF와 실제 파일명 기준으로 수정
  - SQLite 타입·실행 순서·FK 연결 단위 설명 추가
- 관련 커밋: `b12c0bd`
- 검증: README의 명령과 자동 검증 진입점 확인

## Issue #2 — SQL·결과 이미지·분석 문서 불일치

- URL: <https://github.com/giyeop-cody/B5-1/issues/2>
- 발견:
  - 과거 스크린샷이 현재 Query 1/5/9/12와 맞지 않았다.
  - Query 5/9/12 분석이 실제 SQL과 다른 도메인·조건을 설명했다.
  - ERD에 `DATETTME` 오기가 있었다.
- 원인: SQL 변경 뒤 증거와 문서를 같은 실행에서 다시 만들지 않았다.
- 처리:
  - 새 DB 한 개에서 Query 1~15 결과 텍스트 재생성
  - 텍스트 기반 PNG 16개 재생성
  - 현재 스키마 기준 ERD 재생성
  - 복합 쿼리 문서를 현재 Q5/Q9/Q12 기준으로 다시 작성
  - 무작위 임시 DB 경로를 증거에서 제거해 연속 실행 결과를 안정화
- 관련 커밋: `cc3be36`, `93ab42e`, `99b5251`
- 검증: `scripts/check_all.sh`, 이미지 표본 직접 확인

## Issue #3 — SQL 의미·무결성·보너스 검증 부족

- URL: <https://github.com/giyeop-cody/B5-1/issues/3>
- 발견:
  - 잘못된 status와 음수 quantity가 저장됐다.
  - Q7/8 설명·seed가 LEFT JOIN 미매칭 질문과 맞지 않았다.
  - Q13 UPDATE가 현재 상태를 확인하지 않았다.
  - JOIN/서브쿼리 동치와 성능 설명이 실증 범위를 넘었다.
  - KPI SQL·결과가 완전하게 연결되지 않았다.
- 처리:
  - 가격·좌석·수용 인원·수량·status CHECK 추가
  - 미주문 메뉴 `유자차` 추가
  - Q7/8 의미 수정, Q13/14 상태 가드, Q15 멱등 인덱스 적용
  - 보너스 SQL 5개와 결과 집합 비교·KPI 자동 검증 추가
- 관련 커밋: `e4e2289`, `cc3be36`, `99b5251`
- 검증:
  - FK·status·quantity·UNIQUE 위반 차단 PASS
  - Query 1~15 PASS
  - JOIN/서브쿼리 5행 전체 값 동치 PASS
  - KPI 10/4/1행 PASS

## Issue #4 — 학습·평가·Git 이력 정리

- URL: <https://github.com/giyeop-cody/B5-1/issues/4>
- 발견:
  - 학습 순서·선택 근거·문제 처리 연결이 부족했다.
  - eval 자료에 실제 스키마에 없는 도메인이 섞일 위험이 있었다.
  - 외부 동료평가와 자체 검증을 구분해야 했다.
  - 전체 원격 브랜치·태그의 작성자 이메일 통일과 SHA 추적이 필요했다.
- 처리 진행:
  - 학습 일지·선택 기록·Issue 처리 기록 작성 완료
  - 실제 4-table 도메인만 쓰는 외부 평가 요청서 작성 완료
  - learning/eval 브랜치를 목적에 맞춰 로컬에서 최신화하고 전체 검사 완료
  - rewrite 전 bundle 보관 완료
  - 로컬 전체 refs 이메일 rewrite와 31개 old→new SHA 매핑 완료
  - 원격 네 브랜치 force push 완료
  - GitHub API에서 35개 고유 commit의 목표 이메일·계정 연결 확인 완료
  - PR #5 병합 완료
  - `main@708ff2c` fresh clone 전체 검사·링크·이메일 검증 PASS
  - 최종 상태 문서는 별도 후속 PR로 기록, fresh clone 검증
- 외부 평가: 대기 중. 실제 평가를 임의 작성하지 않음.
- 완료 조건: PR 병합, 브랜치 정리, rewrite·SHA·fresh-clone 검증까지 끝난 뒤 Issue에 최종 증거 게시

## 공통 종료 체크리스트

- [x] 기능 수정은 별도 브랜치에서 수행
- [x] 변경 종류별 커밋 분리
- [x] 실제 SQLite 실행 기반 자동 검증
- [x] 텍스트·이미지 증거 재생성
- [x] `scripts/check_all.sh` 최종 전체 PASS
- [x] Pull Request #5 검증과 main 병합
- [x] learning/eval 브랜치 정리
- [x] 전체 원격 브랜치·태그 이메일 rewrite
- [x] SHA 매핑·복구 bundle 보관
- [x] fresh clone·GitHub API 최종 확인
- [ ] 실제 외부 동료평가 수신
