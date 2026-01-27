# 배포 가이드 🚀

카드 뒤집기 게임을 배포하는 방법을 안내합니다.

## 추천 배포 플랫폼

### 1. **Vercel** (가장 추천 ⭐)
- ✅ 무료
- ✅ 가장 간단하고 빠름
- ✅ GitHub 연동으로 자동 배포
- ✅ 커스텀 도메인 지원
- ✅ HTTPS 자동 설정

### 2. **Netlify**
- ✅ 무료
- ✅ 드래그 앤 드롭 배포 가능
- ✅ GitHub 연동 지원
- ✅ 커스텀 도메인 지원

### 3. **GitHub Pages**
- ✅ 완전 무료
- ✅ GitHub 저장소와 통합
- ⚠️ 커스텀 도메인 설정 필요

### 4. **Cloudflare Pages**
- ✅ 무료
- ✅ 매우 빠른 CDN
- ✅ GitHub 연동 지원

---

## 배포 방법

### 방법 1: Vercel 배포 (추천)

#### 옵션 A: GitHub 연동 (자동 배포)

1. **GitHub에 저장소 생성**
   ```bash
   cd /Users/kimpro/cursorstudy/api-stock/vive27
   git init
   git add .
   git commit -m "Initial commit: Card flip game"
   git branch -M main
   git remote add origin https://github.com/your-username/card-flip-game.git
   git push -u origin main
   ```

2. **Vercel에 배포**
   - [Vercel](https://vercel.com)에 가입/로그인
   - "Add New Project" 클릭
   - GitHub 저장소 선택
   - 프로젝트 설정:
     - Framework Preset: **Other**
     - Root Directory: `./` (기본값)
   - "Deploy" 클릭
   - 배포 완료 후 URL 확인 (예: `https://card-flip-game.vercel.app`)

#### 옵션 B: Vercel CLI (수동 배포)

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리에서 실행
cd /Users/kimpro/cursorstudy/api-stock/vive27
vercel

# 배포 확인
# 배포된 URL이 표시됩니다
```

---

### 방법 2: Netlify 배포

#### 옵션 A: 드래그 앤 드롭

1. [Netlify Drop](https://app.netlify.com/drop) 접속
2. 프로젝트 폴더를 드래그 앤 드롭
3. 배포 완료! URL 확인

#### 옵션 B: GitHub 연동

1. GitHub에 저장소 푸시
2. [Netlify](https://www.netlify.com)에 가입/로그인
3. "Add new site" → "Import an existing project"
4. GitHub 저장소 선택
5. Build settings:
   - Build command: (비워두기)
   - Publish directory: `/` (기본값)
6. "Deploy site" 클릭

---

### 방법 3: GitHub Pages 배포

1. **GitHub 저장소 생성 및 푸시**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/card-flip-game.git
   git push -u origin main
   ```

2. **GitHub Pages 활성화**
   - GitHub 저장소 → Settings → Pages
   - Source: `main` 브랜치 선택
   - `/ (root)` 폴더 선택
   - Save 클릭
   - 배포된 URL: `https://your-username.github.io/card-flip-game/`

---

### 방법 4: Cloudflare Pages 배포

1. [Cloudflare Pages](https://pages.cloudflare.com) 접속
2. "Create a project" 클릭
3. GitHub 저장소 연결
4. Build settings:
   - Framework preset: None
   - Build command: (비워두기)
   - Build output directory: `/`
5. "Save and Deploy" 클릭

---

## 배포 전 확인사항

### ✅ 필수 파일 확인
다음 파일들이 모두 포함되어 있는지 확인:
- `index.html`
- `style.css`
- `script.js`
- (선택) `README.md`

### ✅ Supabase 설정 확인
`script.js` 파일에 Supabase URL과 Key가 올바르게 설정되어 있는지 확인:
```javascript
const SUPABASE_URL = 'https://zbhhjoghntjzdyfttmuo.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
```

### ✅ CORS 설정 확인
Supabase에서 배포된 도메인을 허용해야 할 수도 있습니다:
1. Supabase 대시보드 → Settings → API
2. "Allowed Origins"에 배포된 URL 추가 (예: `https://your-app.vercel.app`)

---

## 배포 후 테스트

1. ✅ 게임이 정상적으로 로드되는지 확인
2. ✅ 카드 뒤집기가 작동하는지 확인
3. ✅ 점수 저장이 Supabase에 되는지 확인
4. ✅ 리더보드가 정상적으로 표시되는지 확인
5. ✅ 모바일에서도 정상 작동하는지 확인

---

## 커스텀 도메인 설정 (선택)

### Vercel
1. 프로젝트 → Settings → Domains
2. 도메인 추가
3. DNS 설정 안내 따르기

### Netlify
1. Site settings → Domain management
2. "Add custom domain"
3. DNS 설정 안내 따르기

---

## 문제 해결

### CORS 오류
- Supabase 대시보드에서 배포된 도메인을 허용 목록에 추가

### Supabase 연결 실패
- 브라우저 콘솔에서 오류 확인
- Supabase URL과 Key 재확인
- RLS 정책 확인

### 배포 후 파일을 찾을 수 없음
- 파일 경로가 상대 경로인지 확인
- `index.html`이 루트에 있는지 확인

---

## 추천 순서

1. **Vercel** (가장 빠르고 간단)
2. **Netlify** (드래그 앤 드롭으로 가장 쉬움)
3. **GitHub Pages** (GitHub 사용자에게 적합)
4. **Cloudflare Pages** (최고 성능 필요 시)

---

## 배포 완료 후

배포가 완료되면:
- ✅ 배포된 URL을 친구들과 공유
- ✅ 모바일에서도 테스트
- ✅ 성능 모니터링
- ✅ 사용자 피드백 수집

행운을 빕니다! 🎉
