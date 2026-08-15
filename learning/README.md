# B5-1 learning 브랜치 안내

## 목적

이 브랜치는 최종 구현과 함께 입문 학습 과정을 검토하기 위한 브랜치다. 외부 평가 결과나 오래된 평가 시나리오는 넣지 않는다.

## 읽는 순서

1. [`../QUEST.md`](../QUEST.md) — 공식 미션에서 무엇을 요구하는가
2. [`../LEARNING.md`](../LEARNING.md) — SQL과 관계형 DB 기초
3. [`../docs/learning-journal.md`](../docs/learning-journal.md) — 40시간 배분과 단계별 확인
4. [`../docs/decision-log.md`](../docs/decision-log.md) — 선택지·장단점·결정
5. [`../docs/development-log.md`](../docs/development-log.md) — 문제 재현·원인·해결
6. [`../docs/complex-query-analysis.md`](../docs/complex-query-analysis.md) — Query 5/9/12 분석
7. [`../docs/issue-handling-log.md`](../docs/issue-handling-log.md) — GitHub Issue 연결

## 직접 해볼 순서

```bash
python scripts/verify_project.py
```

그다음 아래 질문에 답해 본다.

1. PK와 FK는 각각 무엇을 막는가?
2. INNER JOIN과 LEFT JOIN 결과가 왜 다른가?
3. WHERE와 HAVING은 언제 쓰는가?
4. Q13은 왜 ID와 현재 상태를 함께 확인하는가?
5. 인덱스가 항상 빠르다고 말할 수 없는 이유는 무엇인가?

## 학습 완료 확인

- [ ] 네 테이블과 세 관계를 말로 설명할 수 있다.
- [ ] FK를 켜지 않았을 때의 위험을 설명할 수 있다.
- [ ] Query 1~15의 목적을 한 줄씩 설명할 수 있다.
- [ ] 잘못된 FK·상태·수량이 왜 차단되는지 설명할 수 있다.
- [ ] 자동 검증 결과를 실제 증거 파일과 연결할 수 있다.

학습자 자체 확인과 외부 동료평가는 다르다. 외부 평가 기록은 eval 브랜치와 `docs/peer-evaluation-request.md`에서 관리한다.
