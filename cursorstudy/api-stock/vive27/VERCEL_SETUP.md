# Vercel 자동 배포 설정 가이드 🚀

GitHub와 연동하여 Vercel에 자동 배포하는 방법입니다.

## 1단계: Git 저장소 초기화 및 커밋

터미널에서 다음 명령어를 실행하세요:

```bash
cd /Users/kimpro/cursorstudy/api-stock/vive27

# Git 저장소 초기화 (이미 되어있다면 생략)
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: Card flip game with Supabase integration"

# 메인 브랜치로 설정
git branch -M main
```

## 2단계: GitHub 저장소 생성 및 연결

### 옵션 A: GitHub 웹사이트에서 생성

1. [GitHub](https://github.com)에 로그인
2. 우측 상단 "+" 버튼 → "New repository" 클릭
3. 저장소 설정:
   - Repository name: `card-flip-game` (또는 원하는 이름)
   - Description: "카드 뒤집기 게임 - Supabase 연동"
   - Public 또는 Private 선택
   - **"Initialize this repository with a README" 체크 해제** (이미 파일이 있으므로)
4. "Create repository" 클릭
5. 생성된 저장소의 URL을 복사 (예: `https://github.com/your-username/card-flip-game.git`)

### 옵션 B: GitHub CLI 사용 (선택사항)

```bash
# GitHub CLI로 저장소 생성
gh repo create card-flip-game --public --source=. --remote=origin --push
```

## 3단계: GitHub에 푸시

터미널에서 다음 명령어를 실행:

```bash
# GitHub 저장소 연결 (위에서 복사한 URL 사용)
git remote add origin https://github.com/your-username/card-flip-game.git

# GitHub에 푸시
git push -u origin main
```

**참고**: GitHub 인증이 필요할 수 있습니다. Personal Access Token을 사용하거나 GitHub CLI를 사용하세요.

## 4단계: Vercel에 배포

### 방법 1: Vercel 웹사이트에서 (추천)

1. [Vercel](https://vercel.com)에 가입/로그인
   - "Continue with GitHub" 버튼으로 GitHub 계정으로 로그인 권장

2. "Add New Project" 클릭

3. GitHub 저장소 선택
   - 방금 생성한 `card-flip-game` 저장소 선택
   - "Import" 클릭

4. 프로젝트 설정:
   - **Framework Preset**: `Other` 선택
   - **Root Directory**: `./` (기본값, 변경 불필요)
   - **Build Command**: 비워두기 (정적 사이트이므로)
   - **Output Directory**: 비워두기 (기본값)
   - **Install Command**: 비워두기

5. Environment Variables (선택사항):
   - 현재는 필요 없음 (Supabase 정보가 코드에 포함되어 있음)
   - 나중에 환경 변수로 분리하고 싶다면 추가 가능

6. "Deploy" 클릭

7. 배포 완료! 🎉
   - 배포된 URL 확인 (예: `https://card-flip-game.vercel.app`)
   - 이제 GitHub에 푸시할 때마다 자동으로 재배포됩니다!

### 방법 2: Vercel CLI 사용

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리에서 실행
cd /Users/kimpro/cursorstudy/api-stock/vive27
vercel

# GitHub 연동 확인
vercel --prod
```

## 5단계: Supabase CORS 설정

배포된 Vercel URL을 Supabase에 허용해야 합니다:

1. [Supabase 대시보드](https://app.supabase.com) 접속
2. 프로젝트 선택 (card-game-scores)
3. Settings → API 메뉴로 이동
4. "Allowed Origins" 섹션 찾기
5. Vercel 배포 URL 추가:
   - 예: `https://card-flip-game.vercel.app`
   - 또는 와일드카드: `https://*.vercel.app`
6. Save 클릭

## 6단계: 자동 배포 테스트

이제 코드를 수정하고 GitHub에 푸시하면 자동으로 재배포됩니다:

```bash
# 파일 수정 후
git add .
git commit -m "Update: 게임 개선"
git push origin main

# Vercel 대시보드에서 자동 배포 진행 상황 확인
```

## 문제 해결

### GitHub 푸시 오류
- Personal Access Token 필요할 수 있음
- GitHub Settings → Developer settings → Personal access tokens → Generate new token

### Vercel 배포 실패
- Vercel 대시보드 → Deployments → 실패한 배포 클릭 → Logs 확인
- `vercel.json` 파일이 올바른지 확인

### Supabase 연결 오류
- 브라우저 콘솔(F12)에서 오류 확인
- Supabase CORS 설정 확인
- `script.js`의 Supabase URL과 Key 확인

## 추가 설정 (선택사항)

### 커스텀 도메인
1. Vercel 프로젝트 → Settings → Domains
2. 도메인 추가
3. DNS 설정 안내 따르기

### 환경 변수 사용 (보안 강화)
나중에 Supabase 정보를 환경 변수로 분리하려면:

1. Vercel 프로젝트 → Settings → Environment Variables
2. 변수 추가:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. `script.js`에서 환경 변수 사용하도록 수정

## 완료! 🎉

이제 GitHub에 코드를 푸시할 때마다 Vercel이 자동으로 배포합니다!
