# Yahoo Finance 주식 데이터 크롤러

Yahoo Finance에서 주식 상승률 데이터를 자동으로 수집하여 엑셀 파일로 저장하는 Python 크롤러입니다.

## 기능

- Yahoo Finance에서 실시간 주식 상승률 데이터 수집
- 주식 심볼, 회사명, 가격 변동, 거래량 등 정보 추출
- 무작위 클래스명 처리로 안정적인 크롤링
- 엑셀 파일로 데이터 저장 및 정리

## 수집되는 데이터

- **Symbol**: 주식 심볼 (예: AMD, NVDA)
- **Name**: 회사명
- **Price_Change**: 가격 변동 (절대값)
- **Change_Percent**: 변동률 (%)
- **Volume**: 거래량
- **Market_Cap**: 시가총액
- **PE_Ratio**: 주가수익비율
- **Avg_Volume**: 평균 거래량

## 설치 및 실행

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 주식 데이터 크롤링

```bash
python3 yahoo_stocks_simple.py
```

### 3. 통계 분석 및 시각화

```bash
# 통계 분석 실행
python3 add_statistics.py

# 시각화 이미지 생성
python3 create_visualizations.py
```

### 4. 결과 확인

- `yahoo_stocks_gainers.xlsx`: Yahoo Finance 주식 상승률 데이터 (7개 시트)
- `visualizations/`: 다양한 차트 이미지 (7개 PNG 파일)
- `visualization_interpretation_guide.md`: 차트 해석 가이드

## 주요 특징

### 크롤링 기능
- **Requests + BeautifulSoup**: 안정적인 정적 페이지 크롤링
- **정확한 데이터 파싱**: Yahoo Finance의 실제 HTML 구조에 맞춘 정밀한 데이터 추출
- **데이터 검증**: 유효하지 않은 데이터 필터링
- **에러 처리**: 안정적인 크롤링을 위한 예외 처리
- **실시간 데이터**: 최신 주식 상승률 데이터 수집

### 데이터 처리
- **엑셀 최적화**: 컬럼 너비 자동 조정
- **데이터 정리**: 정규표현식을 사용한 데이터 정제
- **로깅**: 상세한 실행 로그 제공
- **정확한 파싱**: 가격 변동과 변동률을 정확히 분리하여 추출

### 통계 분석 및 시각화
- **통계 계산**: 평균, 최대/최소값, 표준편차 등 기본 통계
- **구간별 분석**: 변동률에 따른 주식 분류 및 분석
- **다양한 차트**: 히스토그램, 막대차트, 산점도, 히트맵 등
- **종합 대시보드**: 모든 주요 지표를 한눈에 볼 수 있는 대시보드
- **해석 가이드**: 각 차트의 의미와 해석 방법 제공

## 생성되는 엑셀 파일 구조

### yahoo_stocks_gainers.xlsx
- **주식상승률**: Yahoo Finance에서 수집한 주식 상승률 데이터
  - Symbol: 주식 심볼
  - Name: 회사명
  - Price_Change: 가격 변동
  - Change_Percent: 변동률
  - Volume: 거래량
  - Market_Cap: 시가총액
  - PE_Ratio: 주가수익비율
  - Avg_Volume: 평균 거래량

## 설정 옵션

`yahoo_stocks_simple.py` 파일에서 다음을 수정할 수 있습니다:

- **URL 변경**: 다른 Yahoo Finance 페이지로 변경
- **데이터 정리 로직**: `_clean_*` 메서드 수정
- **엑셀 출력 형식**: `save_to_excel` 메서드 수정

## 사용 예시

### 기본 사용법
```python
from yahoo_stocks_simple import YahooStocksSimpleCrawler

# 크롤러 인스턴스 생성
crawler = YahooStocksSimpleCrawler()

# 크롤링 실행
success = crawler.run()

if success:
    print("크롤링 성공!")
    print(f"총 {len(crawler.data)}개의 주식 데이터를 수집했습니다.")
else:
    print("크롤링 실패!")
```

### 수집된 데이터 확인
```python
import pandas as pd

# 엑셀 파일 읽기
df = pd.read_excel('yahoo_stocks_gainers.xlsx')

# 상위 5개 주식 확인
print("상위 5개 상승 주식:")
print(df.head())

# 변동률 기준으로 정렬
df_sorted = df.sort_values('Change_Percent', ascending=False)
print("\n변동률 상위 5개:")
print(df_sorted.head())
```

## 주의사항

- 웹사이트의 구조가 변경될 경우 크롤러 수정이 필요할 수 있습니다
- 과도한 요청으로 인한 IP 차단을 방지하기 위해 적절한 대기 시간이 설정되어 있습니다
- 수집된 데이터는 투자 조언이 아닌 참고용입니다

## 라이선스

이 프로젝트는 교육 및 개인적 용도로만 사용하시기 바랍니다.

## 관련 프로젝트

- [금 시세 크롤러](../gold-price-crawler/): 한국금거래소 금 시세 데이터 크롤링
