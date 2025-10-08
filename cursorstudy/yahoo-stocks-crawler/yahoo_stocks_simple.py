#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 주식 상승률 크롤러 (Simple Version)
requests와 BeautifulSoup을 사용하여 더 안정적으로 크롤링
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YahooStocksSimpleCrawler:
    def __init__(self):
        self.url = "https://finance.yahoo.com/markets/stocks/gainers/"
        self.data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def load_page(self):
        """웹페이지 로드"""
        try:
            logger.info(f"페이지 로드 중: {self.url}")
            
            # 세션 생성
            session = requests.Session()
            session.headers.update(self.headers)
            
            # 페이지 요청
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"페이지 로드 완료. 상태 코드: {response.status_code}")
            return response.text
            
        except Exception as e:
            logger.error(f"페이지 로드 실패: {e}")
            return None
    
    def extract_stock_data(self, html_content):
        """주식 데이터 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 테이블 찾기 - 여러 선택자 시도
            table = None
            table_selectors = [
                'table[data-testid="gainers-table"]',
                'table',
                'div[data-testid="gainers-table"] table',
                'section table'
            ]
            
            for selector in table_selectors:
                table = soup.select_one(selector)
                if table:
                    logger.info(f"테이블 발견: {selector}")
                    break
            
            if not table:
                logger.error("테이블을 찾을 수 없습니다.")
                return False
            
            # 테이블의 모든 행 찾기
            rows = table.find_all('tr')
            logger.info(f"발견된 행 수: {len(rows)}")
            
            # 헤더 행 건너뛰기 (첫 번째 행)
            for i, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:  # 최소 6개 컬럼이 있어야 함
                        # 각 셀에서 데이터 추출
                        symbol = cells[0].get_text(strip=True)
                        name = cells[1].get_text(strip=True)
                        
                        # 실제 구조에 맞게 데이터 추출
                        # 셀 2: 빈 값 (차트/아이콘)
                        # 셀 3: 전체 가격 정보 (203.71+39.04(+23.71%))
                        # 셀 4: 가격 변동 (+39.04)
                        # 셀 5: 변동률 (+23.71%)
                        price_change = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        change_percent = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                        
                        # 추가 컬럼들 (있는 경우)
                        volume = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                        market_cap = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                        pe_ratio = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                        avg_volume = cells[9].get_text(strip=True) if len(cells) > 9 else ""
                        
                        # 데이터 정리
                        data_row = {
                            'Symbol': symbol,
                            'Name': name,
                            'Price_Change': price_change,  # 이미 정리된 형태
                            'Change_Percent': change_percent,  # 이미 정리된 형태
                            'Volume': self._clean_volume_data(volume),
                            'Market_Cap': self._clean_market_cap_data(market_cap),
                            'PE_Ratio': self._clean_pe_ratio_data(pe_ratio),
                            'Avg_Volume': self._clean_volume_data(avg_volume)
                        }
                        
                        self.data.append(data_row)
                        logger.info(f"데이터 추출: {symbol} - {name} - {change_percent}")
                
                except Exception as e:
                    logger.warning(f"행 {i} 데이터 추출 실패: {e}")
                    continue
            
            logger.info(f"총 {len(self.data)}개 주식 데이터 추출 완료")
            return len(self.data) > 0
            
        except Exception as e:
            logger.error(f"주식 데이터 추출 실패: {e}")
            return False
    
    def _clean_price_data(self, price_str):
        """가격 데이터 정리"""
        try:
            # +, - 기호와 숫자만 추출
            cleaned = re.sub(r'[^\d\.\+\-]', '', price_str)
            if cleaned:
                return cleaned
            return price_str
        except:
            return price_str
    
    def _clean_percent_data(self, percent_str):
        """퍼센트 데이터 정리"""
        try:
            # +, - 기호와 숫자, % 기호만 추출
            cleaned = re.sub(r'[^\d\.\+\-%]', '', percent_str)
            if cleaned:
                return cleaned
            return percent_str
        except:
            return percent_str
    
    def _clean_volume_data(self, volume_str):
        """거래량 데이터 정리"""
        try:
            # 숫자와 K, M, B 단위만 추출
            cleaned = re.sub(r'[^\d\.KM]', '', volume_str)
            if cleaned:
                return cleaned
            return volume_str
        except:
            return volume_str
    
    def _clean_market_cap_data(self, market_cap_str):
        """시가총액 데이터 정리"""
        try:
            # 숫자와 K, M, B 단위만 추출
            cleaned = re.sub(r'[^\d\.KM]', '', market_cap_str)
            if cleaned:
                return cleaned
            return market_cap_str
        except:
            return market_cap_str
    
    def _clean_pe_ratio_data(self, pe_str):
        """PER 데이터 정리"""
        try:
            # 숫자와 소수점만 추출
            cleaned = re.sub(r'[^\d\.]', '', pe_str)
            if cleaned:
                return cleaned
            return pe_str
        except:
            return pe_str
    
    def _parse_price_change_data(self, price_text, percent_text):
        """가격 변동 데이터 파싱"""
        try:
            # 가격 변동 텍스트에서 절대 변동값 추출 (예: "203.71+39.04(+23.71%)" -> 39.04)
            price_change = ""
            change_percent = ""
            
            # 가격 변동 텍스트에서 + 또는 - 뒤의 숫자 추출
            price_match = re.search(r'[+-](\d+\.?\d*)', price_text)
            if price_match:
                price_change = price_match.group(1)
                # + 기호가 있으면 양수, - 기호가 있으면 음수
                if '+' in price_text:
                    price_change = '+' + price_change
                else:
                    price_change = '-' + price_change
            
            # 퍼센트 텍스트에서 퍼센트 값 추출
            percent_match = re.search(r'([+-]?\d+\.?\d*)%', percent_text)
            if percent_match:
                change_percent = percent_match.group(1) + '%'
            
            return price_change, change_percent
            
        except Exception as e:
            logger.warning(f"가격 변동 데이터 파싱 실패: {e}")
            return price_text, percent_text
    
    def save_to_excel(self, filename="yahoo_stocks_gainers.xlsx"):
        """데이터를 엑셀 파일로 저장"""
        try:
            if not self.data:
                logger.warning("저장할 데이터가 없습니다.")
                return False
            
            df = pd.DataFrame(self.data)
            
            # 엑셀 파일로 저장
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='주식상승률', index=False)
                
                # 워크시트 스타일링
                worksheet = writer.sheets['주식상승률']
                
                # 컬럼 너비 조정
                column_widths = {
                    'A': 12,  # Symbol
                    'B': 30,  # Name
                    'C': 15,  # Price_Change
                    'D': 15,  # Change_Percent
                    'E': 15,  # Volume
                    'F': 20,  # Market_Cap
                    'G': 12,  # PE_Ratio
                    'H': 15   # Avg_Volume
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
            
            logger.info(f"데이터가 {filename}에 저장되었습니다. (총 {len(df)}개 행)")
            return True
            
        except Exception as e:
            logger.error(f"엑셀 파일 저장 실패: {e}")
            return False
    
    def run(self):
        """크롤링 실행"""
        try:
            logger.info("Yahoo Finance 주식 상승률 크롤링을 시작합니다.")
            
            # 페이지 로드
            html_content = self.load_page()
            if not html_content:
                return False
            
            # 주식 데이터 추출
            if not self.extract_stock_data(html_content):
                return False
            
            # 엑셀 파일로 저장
            if self.data:
                self.save_to_excel()
                logger.info(f"크롤링 완료! 총 {len(self.data)}개의 주식 데이터를 수집했습니다.")
                return True
            else:
                logger.warning("수집된 데이터가 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"크롤링 실행 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    crawler = YahooStocksSimpleCrawler()
    success = crawler.run()
    
    if success:
        print("✅ Yahoo Finance 주식 상승률 크롤링이 성공적으로 완료되었습니다!")
        print("📁 yahoo_stocks_gainers.xlsx 파일을 확인해주세요.")
    else:
        print("❌ Yahoo Finance 주식 상승률 크롤링에 실패했습니다.")

if __name__ == "__main__":
    main()
