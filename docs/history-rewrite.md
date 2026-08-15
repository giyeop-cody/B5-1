# Git 이메일 이력 정리 기록

## 목적

모든 보관 브랜치의 Git author/committer 이메일을 `cody.giyeop@gmail.com`으로 통일하고, rewrite 전후 SHA를 추적한다.

## rewrite 범위

2026-08-15 원격 확인 결과:

- 기존 원격 브랜치: `main`, `eval`
- 준비한 최종 브랜치: `main`, `fix/mission-audit-remediation`, `learning`, `eval`
- 원격 태그: 0개
- rewrite 대상 고유 commit: 31개

legacy eval 이력은 새 eval tip에 `ours` merge로 연결해 파일은 최신 상태로 바꾸되 과거 commit 자체는 추적 가능하게 했다.

## 로컬 rewrite 검증

| 항목 | 전 | 후 |
|---|---:|---:|
| 고유 commit | 31 | 31 |
| author+committer의 기존 이메일 출현 | 40 | 0 |
| author+committer의 목표 이메일 출현 | 22 | 62 |
| 변경된 commit SHA | 31 | 31 |

부모 commit SHA가 바뀌면 내용과 이메일이 이미 올바른 자식 commit의 SHA도 연쇄적으로 바뀐다. 따라서 31개가 모두 변경되는 것은 예상된 결과다.

## ref 변경

| ref | rewrite 전 | rewrite 후 |
|---|---|---|
| main | `18980a31e1929eb3cb29246011c5658025885a95` | `d4c808a1037f7392e50a0abad7348e24052b3337` |
| fix/mission-audit-remediation | `25fa9288eedd12c4b752d059c68a79e767e640c7` | `7747e94c3f0c750c45904ae5eab4e7768fd329f1` |
| learning | `01a77b6d781975418f759a7355179af5cac6ce41` | `bd1362df09a4541f8a76d4fd8c16baf37e482d44` |
| eval | `45989a329e67da4c48fa9cc5ee28cc884a9c759d` | `fad53269525fff53f8cc10a5b3a1391fb6113062` |

전체 commit 단위 매핑은 `docs/email-rewrite-map.tsv`에 있다.

## 복구 자료

- rewrite 전 bundle: `/home/user/B5-1-before-email-rewrite.bundle`
- SHA-256: `a4f863610dcd7acb435edbcd398fd20ced0b6621c7fae628597ae3cf261e71ab`
- 전체 old→new 매핑 원본: `/home/user/email-rewrite-b5-1/commit-map.txt`
- rewrite 전 refs: `/home/user/email-rewrite-b5-1/pre-rewrite-refs.txt`

bundle은 별도 보관 자료라 Git 저장소 안에 넣지 않는다.

## 남은 원격 검증

로컬 rewrite와 매핑은 완료했다. 다음 항목은 GitHub 인증 후 force push와 PR 병합이 끝나면 갱신한다.

- [ ] 전체 브랜치 force push
- [ ] GitHub API의 기존 이메일 0개
- [ ] GitHub API의 commit author 계정 연결 확인
- [ ] fresh clone에서 전체 검사 PASS
