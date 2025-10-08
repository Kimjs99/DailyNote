# 📝 Notes

Next.js 15와 Express.js를 사용한 현대적인 메모 관리 애플리케이션입니다. 사용자 인증, 데이터베이스 연동, 실시간 메모 관리 기능을 제공합니다.

## 🚀 주요 기능

- **사용자 인증**: 회원가입, 로그인, 로그아웃
- **메모 관리**: 메모 생성, 수정, 삭제
- **태그 시스템**: 메모에 태그 추가 및 필터링
- **색상 구분**: 파스텔 색상으로 메모 구분
- **검색 기능**: 제목, 내용, 태그로 메모 검색
- **반응형 디자인**: 모바일과 데스크톱 모두 지원

## 🛠 기술 스택

### 프론트엔드
- Next.js 15
- TypeScript
- Tailwind CSS
- shadcn/ui
- Axios (HTTP 클라이언트)

### 백엔드
- Node.js
- Express.js
- Prisma ORM
- SQLite 데이터베이스
- JWT 인증
- bcryptjs (비밀번호 해싱)

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd memo-app
```

### 2. 백엔드 의존성 설치 및 실행
```bash
cd backend
npm install
npx prisma generate
npx prisma db push
npm start
```
백엔드 서버는 `http://localhost:5001`에서 실행됩니다.

### 3. 프론트엔드 의존성 설치 및 실행
```bash
cd frontend
npm install
npm run dev
```
프론트엔드는 `http://localhost:3000`에서 실행됩니다.

## 🔧 API 엔드포인트

### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `GET /api/auth/me` - 사용자 정보 조회

### 메모
- `GET /api/memos` - 메모 목록 조회
- `POST /api/memos` - 새 메모 생성
- `PUT /api/memos/:id` - 메모 수정
- `DELETE /api/memos/:id` - 메모 삭제

## 📱 사용법

1. **회원가입**: 첫 방문 시 회원가입을 진행합니다.
2. **로그인**: 이메일과 비밀번호로 로그인합니다.
3. **메모 작성**: "새 메모" 버튼을 클릭하여 메모를 작성합니다.
4. **메모 편집**: 메모 카드의 "수정" 버튼을 클릭하여 편집합니다.
5. **태그 추가**: 메모에 쉼표로 구분하여 태그를 추가할 수 있습니다.
6. **색상 선택**: 10가지 파스텔 색상 중 선택하여 메모를 구분할 수 있습니다.
7. **검색**: 상단 검색창에서 제목, 내용, 태그로 메모를 검색할 수 있습니다.

## 🗂 프로젝트 구조

```
my-memo/
├── backend/              # Express.js 백엔드
│   ├── prisma/           # Prisma 스키마
│   ├── server.js         # Express 서버
│   └── package.json      # 백엔드 의존성
├── frontend/             # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/          # Next.js 앱 라우터
│   │   ├── components/   # React 컴포넌트
│   │   └── contexts/     # React 컨텍스트
│   ├── app/              # 글로벌 스타일
│   └── package.json      # 프론트엔드 의존성
├── README.md
└── DEVELOPMENT.md        # 개발 과정 문서
```

## 🔒 보안 기능

- JWT 토큰 기반 인증
- 비밀번호 해싱 (bcryptjs)
- 사용자별 메모 격리
- CORS 설정

## 🎨 UI/UX 특징

- 모던하고 직관적인 디자인
- 모노톤 베이지/아이보리 색상 팔레트
- 2컬럼 사이드바 레이아웃
- 부드러운 폰트 (Source Serif Pro, Noto Sans)
- 키보드 단축키 지원 (Ctrl+S, Esc)
- 반응형 디자인
- 실시간 편집 및 미리보기

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.