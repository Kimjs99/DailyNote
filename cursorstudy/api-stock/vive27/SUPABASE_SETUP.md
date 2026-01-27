# Supabase 연동 설정 가이드

## 1. Supabase 프로젝트 정보 확인

1. [Supabase 대시보드](https://app.supabase.com)에 로그인
2. 프로젝트 선택 (현재: "Kimjs99's" 프로젝트)
3. 좌측 메뉴에서 **Settings** → **API** 클릭
4. 다음 정보를 확인:
   - **Project URL**: `https://xxxxx.supabase.co` 형식
   - **anon public key**: `eyJhbGc...` 형식의 긴 문자열

## 2. script.js 파일 수정

`script.js` 파일의 상단 부분을 찾아서 수정하세요:

```javascript
// Supabase 설정
const SUPABASE_URL = '여기에_Project_URL_입력';
const SUPABASE_ANON_KEY = '여기에_anon_public_key_입력';
```

예시:
```javascript
const SUPABASE_URL = 'https://abcdefghijklmnop.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI4MCwiZXhwIjoxOTU0NTQzMjgwfQ.abcdefghijklmnopqrstuvwxyz1234567890';
```

## 3. 테이블 구조 확인

현재 Supabase 테이블 구조:
- `id` (uuid, primary key)
- `player_name` (text)
- `turns` (integer) - 시도 횟수
- `created_at` (timestamptz) - 자동 생성

## 4. RLS (Row Level Security) 설정 확인

Supabase 대시보드에서:
1. **Authentication** → **Policies** 메뉴로 이동
2. `game_scores` 테이블의 정책 확인
3. 다음 정책이 필요합니다:
   - **SELECT 정책**: 모든 사용자가 읽기 가능
   - **INSERT 정책**: 모든 사용자가 점수 추가 가능

SQL Editor에서 다음 명령어로 확인/설정:

```sql
-- RLS 활성화 확인
ALTER TABLE game_scores ENABLE ROW LEVEL SECURITY;

-- 읽기 정책
CREATE POLICY "Anyone can read scores" ON game_scores
  FOR SELECT USING (true);

-- 쓰기 정책
CREATE POLICY "Anyone can insert scores" ON game_scores
  FOR INSERT WITH CHECK (true);
```

## 5. 테스트

1. 게임을 완료하고 점수를 저장
2. 브라우저 개발자 도구(F12) → Console 탭에서 오류 확인
3. Supabase 대시보드 → Table Editor에서 데이터 확인

## 주의사항

- Supabase 테이블에는 `turns` 컬럼만 저장됩니다
- 난이도(`difficulty`)와 완료 시간(`time_seconds`)은 로컬 스토리지에만 저장됩니다
- 리더보드의 "전체" 탭에서는 Supabase 데이터를 표시하고, 난이도별 탭에서는 로컬 스토리지 데이터를 표시합니다
