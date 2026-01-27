# 카드 뒤집기 게임 🎴

가장 간단한 웹 기술(HTML, CSS, Vanilla JavaScript)로 만든 카드 뒤집기 게임입니다. Supabase를 사용하여 점수와 리더보드를 저장합니다.

## 기능

- 🎮 카드 뒤집기 게임 (쉬움/보통/어려움 난이도)
- ⏱️ 실시간 타이머
- 📊 시도 횟수 추적
- 🏆 Supabase 리더보드
- 💾 점수 저장 기능
- 🎨 부드러운 카드 애니메이션

## 설치 및 설정

### 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 가입하고 새 프로젝트를 생성합니다.
2. 프로젝트 설정에서 URL과 Anon Key를 확인합니다.

### 2. 데이터베이스 테이블 생성

Supabase 대시보드의 SQL Editor에서 다음 SQL을 실행합니다:

```sql
-- game_scores 테이블 생성
CREATE TABLE game_scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  player_name TEXT,
  attempts INTEGER NOT NULL,
  time_seconds INTEGER NOT NULL,
  difficulty TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) 설정
ALTER TABLE game_scores ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능
CREATE POLICY "Anyone can read scores" ON game_scores
  FOR SELECT USING (true);

-- 모든 사용자가 점수 추가 가능
CREATE POLICY "Anyone can insert scores" ON game_scores
  FOR INSERT WITH CHECK (true);
```

또는 `supabase_setup.sql` 파일의 내용을 사용할 수 있습니다.

### 3. Supabase 설정

`script.js` 파일을 열고 다음 부분을 수정합니다:

```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
```

본인의 Supabase 프로젝트 URL과 Anon Key로 변경하세요.

### 4. 실행

로컬 웹 서버를 실행하거나, 파일을 직접 브라우저에서 열 수 있습니다.

```bash
# Python 3를 사용하는 경우
python -m http.server 8000

# Node.js http-server를 사용하는 경우
npx http-server -p 8000
```

브라우저에서 `http://localhost:8000`으로 접속합니다.

## 게임 방법

1. 난이도를 선택합니다 (쉬움/보통/어려움)
2. "새 게임" 버튼을 클릭하여 게임을 시작합니다
3. 카드를 클릭하여 뒤집습니다
4. 같은 숫자의 카드 쌍을 찾아 매칭합니다
5. 모든 카드를 매칭하면 게임이 완료됩니다
6. 점수를 저장하여 리더보드에 등록할 수 있습니다

## 파일 구조

```
vive27/
├── index.html          # HTML 구조
├── style.css           # 스타일 및 애니메이션
├── script.js           # 게임 로직 및 Supabase 통합
├── supabase_setup.sql  # Supabase 데이터베이스 설정 SQL
└── README.md           # 이 파일
```

## 기술 스택

- HTML5
- CSS3 (Flexbox, Grid, Animations)
- Vanilla JavaScript (ES6+)
- Supabase (PostgreSQL 데이터베이스)

## 라이선스

MIT
