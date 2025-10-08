#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 주식 상승률 크롤러
https://finance.yahoo.com/markets/stocks/gainers/ 에서 주식 상승률 데이터를 수집하여 엑셀 파일로 저장
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YahooStocksCrawler:
    def __init__(self):
        self.url = "https://finance.yahoo.com/markets/stocks/gainers/"
        self.driver = None
        self.data = []
        
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver 설정 완료")
            return True
        except Exception as e:
            logger.error(f"WebDriver 설정 실패: {e}")
            return False
    
    def load_page(self):
        """웹페이지 로드"""
        try:
            logger.info(f"페이지 로드 중: {self.url}")
            self.driver.get(self.url)
            
            # 페이지 로드 대기 시간 증가
            time.sleep(10)
            
            # 여러 선택자로 테이블 찾기 시도
            table_selectors = [
                "section[class*='mainContent'] table",
                "table[data-testid='gainers-table']",
                "table",
                "div[data-testid='gainers-table'] table"
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    table = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"테이블 발견: {selector}")
                    break
                except:
                    continue
            
            if not table:
                logger.error("테이블을 찾을 수 없습니다.")
                return False
            
            logger.info("페이지 로드 완료")
            return True
        except Exception as e:
            logger.error(f"페이지 로드 실패: {e}")
            return False
    
    def extract_stock_data(self):
        """주식 데이터 추출"""
        try:
            # 여러 선택자로 테이블 찾기 시도
            table_selectors = [
                "section[class*='mainContent'] table",
                "table[data-testid='gainers-table']",
                "table",
                "div[data-testid='gainers-table'] table"
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    table = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"테이블 발견: {selector}")
                    break
                except:
                    continue
            
            if not table:
                logger.error("테이블을 찾을 수 없습니다.")
                return False
            
            # 테이블의 모든 행 찾기
            rows = table.find_elements(By.CSS_SELECTOR, "tr")
            logger.info(f"발견된 행 수: {len(rows)}")
            
            # 헤더 행 건너뛰기 (첫 번째 행)
            for i, row in enumerate(rows[1:], 1):
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(cells) >= 6:  # 최소 6개 컬럼이 있어야 함
                        # 각 셀에서 데이터 추출
                        symbol = cells[0].text.strip()
                        name = cells[1].text.strip()
                        price_change = cells[2].text.strip()
                        change_percent = cells[3].text.strip()
                        volume = cells[4].text.strip() if len(cells) > 4 else ""
                        market_cap = cells[5].text.strip() if len(cells) > 5 else ""
                        pe_ratio = cells[6].text.strip() if len(cells) > 6 else ""
                        avg_volume = cells[7].text.strip() if len(cells) > 7 else ""
                        
                        # 데이터 정리
                        data_row = {
                            'Symbol': symbol,
                            'Name': name,
                            'Price_Change': self._clean_price_data(price_change),
                            'Change_Percent': self._clean_percent_data(change_percent),
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
                    'F': 15,  # Avg_Volume
                    'G': 20,  # Market_Cap
                    'H': 12   # PE_Ratio
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
            
            # WebDriver 설정
            if not self.setup_driver():
                return False
            
            # 페이지 로드
            if not self.load_page():
                return False
            
            # 주식 데이터 추출
            if not self.extract_stock_data():
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
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver 종료")

def main():
    """메인 함수"""
    crawler = YahooStocksCrawler()
    success = crawler.run()
    
    if success:
        print("✅ Yahoo Finance 주식 상승률 크롤링이 성공적으로 완료되었습니다!")
        print("📁 yahoo_stocks_gainers.xlsx 파일을 확인해주세요.")
    else:
        print("❌ Yahoo Finance 주식 상승률 크롤링에 실패했습니다.")

if __name__ == "__main__":
    main()

