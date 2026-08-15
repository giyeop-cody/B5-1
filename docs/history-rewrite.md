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

## 원격 반영 및 API 검증

2026-08-15에 기존 원격 `main`·`eval`은 예상 이전 SHA를 지정한 `--force-with-lease`로 갱신하고, `fix/mission-audit-remediation`·`learning`을 새로 push했다.

| 원격 브랜치 | push 후 SHA |
|---|---|
| main | `d4c808a1037f7392e50a0abad7348e24052b3337` |
| fix/mission-audit-remediation | `044ce65309de3dae4208c7194630c31d1f45c21a` |
| learning | `6e32b8a1097d4aa300ed9fcda40bd49ccbe4242c` |
| eval | `085d578de744c226f2214df2acc5c82fc05b1a70` |

GitHub Commit API로 네 브랜치에서 도달 가능한 35개 고유 commit을 합쳐 검사했다.

- target이 아닌 author/committer 이메일: 0개
- `giyeop-cody` 계정에 연결되지 않은 author/committer 역할: 0개

rewrite 이후 추가한 문서·브랜치 동기화 commit도 처음부터 목표 이메일로 작성했기 때문에 31개 rewrite 매핑에는 들어가지 않지만 API 검사 범위에는 들어간다.

- [x] 전체 브랜치 force push
- [x] GitHub API의 기존 이메일 0개
- [x] GitHub API의 commit author/committer 계정 연결 확인
- [x] PR #5 병합 후 `main@708ff2c` fresh clone 전체 검사 PASS
