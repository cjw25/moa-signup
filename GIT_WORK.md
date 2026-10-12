# Git 협업 실습 기록

저장소: https://github.com/cjw25/moa-signup

같은 저장소를 `git-practice-minsu`와 `git-practice-jiyun`에 각각 `git clone https://github.com/cjw25/moa-signup.git`으로 받았다. 두 폴더의 `git remote -v` 출력은 모두 `origin https://github.com/cjw25/moa-signup.git (fetch)`와 `(push)`였다. 한 계정으로 두 역할을 나누었고, 각 PR은 변경 파일을 직접 확인한 뒤 merge commit 방식으로 병합했다.

## 초기 작업 브랜치와 PR

| 역할 | 브랜치·커밋 | PR | Files changed 확인 | 병합 |
| --- | --- | --- | --- | --- |
| 민수 | `feature/minsu`, `57fa89b` | [#4](https://github.com/cjw25/moa-signup/pull/4) | `minsu.md` | `a78af93`, Create a merge commit |
| 지윤 | `feature/jiyun`, `de13f3c` | [#5](https://github.com/cjw25/moa-signup/pull/5) | `jiyun.md` | `927db9b`, Create a merge commit |
| 지윤 점검표 | `feature/checklist`, `8d4ef1e` | [#6](https://github.com/cjw25/moa-signup/pull/6) | `CHECKLIST.md`, `TEAM.md` | `4f7fe6a`, Create a merge commit |

민수 폴더에서 실행한 주요 명령과 출력:

```text
git switch -c feature/minsu
git add minsu.md
git commit -m "Add Minsu collaboration note"
[feature/minsu 57fa89b] ...
git switch main
git ls-files minsu.md
(출력 없음: main에는 아직 minsu.md가 없음)
git merge --no-ff feature/minsu
Merge made by the 'ort' strategy.
git switch feature/minsu
git push -u origin feature/minsu
* [new branch] feature/minsu -> feature/minsu
```

민수는 PR #4 제출 후 **같은** `feature/minsu`에 보완 커밋 `0d1fd17`을 더해 push했다. 새 PR을 만들지 않았고 #4의 Files changed에 보완 내용이 반영된 것을 확인했다.

지윤 폴더에서 실행한 주요 명령과 출력:

```text
git switch -c feature/jiyun
git add jiyun.md
git commit -m "Add Jiyun collaboration note"
[feature/jiyun de13f3c] ...
git switch main
git ls-files jiyun.md
(출력 없음: main에는 아직 jiyun.md가 없음)
git merge --no-ff feature/jiyun
Merge made by the 'ort' strategy.
git switch feature/jiyun
git push -u origin feature/jiyun
* [new branch] feature/jiyun -> feature/jiyun
```

이 로컬 merge는 각 폴더의 **main에서** 실행했으므로, 해당 폴더의 main이 자기 작업 브랜치 커밋을 받았다. 원격 main에는 push하지 않았다. PR #4·#5를 병합한 뒤 양쪽 폴더에서 `git switch main`, `git pull --no-rebase origin main`을 실행했다. 민수 폴더의 출력에는 `jiyun.md`와 민수 보완 내용이, 지윤 폴더의 출력에는 `minsu.md`가 추가되었다. 두 폴더 모두 `git ls-files minsu.md jiyun.md` 출력이 `jiyun.md`, `minsu.md`였다.

지윤 폴더의 최신 `origin/main`에서 `git switch -c feature/checklist origin/main`으로 새 브랜치를 만들고 `CHECKLIST.md`, `TEAM.md`를 커밋·push했다. PR #6의 두 변경 파일을 확인한 다음 병합했다. 두 폴더의 main에서 다시 pull했을 때 `CHECKLIST.md`, `TEAM.md`가 추가되었다. 완료한 로컬 `feature/minsu`, `feature/jiyun`, `feature/checklist`는 `git branch -d`로 정리했다.

## 선택 1: 같은 줄 충돌

두 폴더의 최신 main에서 각각 `feature/minsu-policy`, `feature/jiyun-policy`를 만들고 `TEAM.md`의 같은 마지막 줄을 수정했다. [민수 PR #7](https://github.com/cjw25/moa-signup/pull/7)의 문장은 `민수는 기능 동작을 확인하고 서로의 변경을 읽은 뒤 병합한다.`였고, [지윤 PR #8](https://github.com/cjw25/moa-signup/pull/8)은 `지윤은 화면 흐름을 확인하고 서로의 변경을 읽은 뒤 병합한다.`였다. 먼저 #7을 merge commit `819a8e4`로 병합했다.

지윤 작업 브랜치에서 `git pull --no-rebase origin main`을 실행한 실제 출력은 `CONFLICT (content): Merge conflict in TEAM.md`였다. 충돌 표시의 HEAD는 지윤 문장, incoming은 민수 문장이었다. 두 점검이 모두 필요하므로 최종 문장을 `민수는 기능 동작을, 지윤은 화면 흐름을 확인하고 서로의 변경을 읽은 뒤 병합한다.`로 정했다. 해결 커밋 `f5bbb92`를 **같은 PR #8**에 push했고, 변경 파일 `TEAM.md`를 확인한 다음 merge commit `7b03343`으로 병합했다. 양쪽 main에서 pull해 최종 문장을 받았고 두 policy 브랜치를 로컬에서 삭제했다.

## Next.js 브랜치 작업

| 내용 | 브랜치·커밋 | PR | 확인 |
| --- | --- | --- | --- |
| 필수 state 메모 앱 | `feature/next-practice`, `92d7d9d` | [#9](https://github.com/cjw25/moa-signup/pull/9) | `next-practice/` 20개 파일, `npm run build` 성공, 빌드 앱 홈·메모 동작 |
| 선택 2: 빈 목록 안내 개선 | `feature/notes-empty-copy`, `b85788a` | [#10](https://github.com/cjw25/moa-signup/pull/10) | `next-practice/components/Notes.js` 한 파일, 빌드 성공, 마지막 메모 삭제 후 새 안내 표시 |
| 선택 3·4: Flask API 연결 | `feature/next-monitor-api`, `d2b9094`·보완 `974db30` | [#11](https://github.com/cjw25/moa-signup/pull/11) | `monitor/next-frontend/`, 통합 테스트와 CI 설정, merge commit `67ef27b` |

각 PR은 base `main`, head는 표의 작업 브랜치로 만들고 Files changed를 확인했다. #9·#10·#11 모두 Create a merge commit으로 병합했다. 지윤 main은 #9 뒤와 #10 뒤에 각각 pull했고, 민수 main은 두 PR 병합 뒤 한 번 pull해 둘 다 받았다. #10의 지윤 로컬 pull 출력은 `next-practice/components/Notes.js | 2 +-`였다. #10의 빌드 화면에서 마지막 메모 삭제 후 `아직 메모가 없습니다. 위 입력칸에서 첫 메모를 등록해 보세요.`가 표시되었다. #11은 CI 성공 후 병합했고 두 폴더의 main에서 다시 pull했다. 두 pull 출력 모두 `monitor/next-frontend/`와 `tests/integration.py` 등 23개 파일 추가·수정을 보여 주었고, 양쪽의 `git ls-files monitor/next-frontend/app/page.js next-practice/components/Notes.js`는 두 경로를 출력했다. 완료한 지윤의 `feature/next-practice`, `feature/notes-empty-copy`, `feature/next-monitor-api`는 `git branch -d`로 정리했다.

## 확인한 명령·화면

`next-practice`에서 `npm run build`가 성공하여 `/`와 `/notes`가 정적 경로로 생성되었다. `npm run start -- --port 3001`의 출력은 `Ready`였고 두 URL은 HTTP 200이었다. 브라우저에서 숫자 증가로 1, 초기화로 0, Link 이동, 동일 내용 메모 2개 등록, 한쪽만 수정, 빈 입력 경고, 삭제 취소·확정, 새로고침 후 초기 메모 복귀를 확인했다. 마지막 항목 삭제 후 빈 목록 안내도 확인했다.

`monitor/next-frontend`에서 `npm run lint`와 `npm run build`가 성공했다. 첫 CI 실행은 서버 렌더링 첫 HTML에 아직 로그인 화면이 없는데도 그 문구를 검사해 실패했다. 실제 첫 HTML의 제목을 검사하도록 같은 PR에 보완 커밋 `974db30`을 올렸다. [다시 실행된 GitHub Actions](https://github.com/cjw25/moa-signup/actions/runs/38191991937)는 **success**였다. PostgreSQL·Flask·Next.js 환경에서 세션 로그인, 목록·상세·등록·수정·삭제, 새 HTTP 세션의 DB 자료 유지, 공백 입력 400, 없는 메모 404, DB 행의 수정 내용을 확인했다.

## 질문 답

**main에서 `git merge feature/minsu`를 실행하면 어느 브랜치가 변경을 받는가?** 현재 checkout된 `main`이 `feature/minsu`의 커밋을 받는다.

**GitHub에서 PR을 병합한 뒤에도 각 폴더에서 pull해야 하는 이유는?** GitHub의 원격 main만 바뀌므로 두 로컬 폴더의 main은 자동으로 갱신되지 않는다. 각 폴더에서 pull해야 원격 병합 결과를 받는다.
