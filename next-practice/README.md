# 작은 메모 연습장

`create-next-app` 16.4.0의 JavaScript·App Router 기본 프로젝트에서 시작해 홈 카운터와 메모 화면을 구현했습니다. 이 폴더는 Git 협업 실습 폴더 안의 별도 Next.js 앱입니다.

## 실행 (Windows CMD)

Node.js 20.9 이상을 준비하고 이 폴더에서 실행합니다.

```cmd
npm ci
npm run dev
```

개발 주소는 `http://localhost:3000`입니다. 프로덕션 실행은 개발 서버를 종료한 뒤 진행합니다.

```cmd
npm run build
npm run start
```

## 파일과 동작

Next.js는 React로 화면을 만들고, 파일 기반 경로와 빌드·서버 기능을 제공합니다. `app/page.js`는 `/` 홈 화면, `app/notes/page.js`는 `/notes` 화면, `app/layout.js`는 두 화면에 공통인 헤더·링크·바닥글을 렌더링합니다. 화면 이동은 `next/link`의 `Link`를 사용합니다.

`components/Counter.js`와 `components/Notes.js`에는 `"use client"`를 붙였습니다. 버튼 클릭과 입력 이벤트를 처리하고 `useState`로 값을 바꾸려면 Client Component가 필요하기 때문입니다. 카운터는 증가·초기화가 가능합니다. 메모는 고유 ID로 등록·수정·삭제되며, 같은 텍스트를 여러 번 등록해도 각각 구별됩니다. 삭제 전에 확인하고, 공백 입력은 거절합니다.

메모 배열은 브라우저의 React state에만 있습니다. 새로고침하면 컴포넌트가 다시 만들어져 초기 메모 한 개로 돌아갑니다. DB 저장 앱은 별도 서버나 DB에 쓰기 때문에 새로고침 뒤에도 자료가 유지됩니다. 이 차이를 확인할 수 있도록 이 앱은 DB를 사용하지 않습니다.

## 동작 확인

홈에서 숫자 증가·초기화, 링크 이동, 같은 텍스트 메모 두 개 등록, 한쪽만 수정, 수정 취소·공백 거절, 삭제 취소·확정, 수정 중 삭제 후 폼 초기화, 빈 목록 안내, 새로고침 후 초기화 순서로 확인합니다. `npm run build`와 `npm run start`를 통해 `/`와 `/notes`가 열리는지도 확인합니다.
