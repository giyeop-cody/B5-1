# B5-1 eval 브랜치 안내

## 목적

이 브랜치는 최신 스마트 테이블 오더 구현을 평가할 때 필요한 자료만 추가한다. 학습 본문은 `LEARNING.md`와 `docs/learning-journal.md`를 링크하고 중복 복사하지 않는다.

## 평가 자료

- `eval/peer-eval-scenario.md`: 학습·고찰·시도·수정·선택·트러블슈팅 설명 순서
- `eval/verbal-qa.md`: 현재 4-table 구현 기준 구두 질문과 답
- `eval/result.md`: 자동 검증 결과와 외부 평가 대기 상태
- `docs/peer-evaluation-request.md`: 외부 평가자가 작성할 빈 체크리스트

## 평가 실행

```bash
python scripts/verify_project.py
python -m pip install -r requirements-dev.txt
scripts/check_all.sh
```

기대 문구:

```text
B5-1 AUTOMATED VERIFICATION: ALL PASS
B5-1 CHECK ALL: PASS
```

## 정직한 결과 구분

- 자동 검증 PASS는 저장소의 스크립트가 확인한 구현 결과다.
- 외부 동료평가 PASS는 실제 외부 평가자가 실행하고 의견을 남긴 뒤에만 기록한다.
- 점수·평가자·평가 날짜를 예상해서 채우지 않는다.
