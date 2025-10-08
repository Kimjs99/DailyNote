#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국금거래소 금 시세 크롤러
https://www.koreagoldx.co.kr/price/gold 에서 금 시세 데이터를 수집하여 엑셀 파일로 저장
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

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoldPriceCrawler:
    def __init__(self):
        self.url = "https://www.koreagoldx.co.kr/price/gold"
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
            
            # 페이지가 완전히 로드될 때까지 대기
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tabulator"))
            )
            
            # 추가 대기 시간 (JavaScript 로딩 완료)
            time.sleep(3)
            logger.info("페이지 로드 완료")
            return True
        except Exception as e:
            logger.error(f"페이지 로드 실패: {e}")
            return False
    
    def extract_table_data(self):
        """테이블에서 데이터 추출"""
        try:
            # Tabulator 테이블 찾기
            table = self.driver.find_element(By.CLASS_NAME, "tabulator")
            
            # 테이블의 모든 행 찾기
            rows = table.find_elements(By.CSS_SELECTOR, ".tabulator-row")
            logger.info(f"발견된 행 수: {len(rows)}")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, ".tabulator-cell")
                    if len(cells) >= 5:  # 최소 5개 컬럼이 있어야 함
                        date = cells[0].text.strip()
                        buy_pure = cells[1].text.strip().replace(',', '')
                        sell_pure = cells[2].text.strip().replace(',', '')
                        sell_18k = cells[3].text.strip().replace(',', '')
                        sell_14k = cells[4].text.strip().replace(',', '')
                        
                        # 데이터가 유효한지 확인
                        if date and buy_pure.isdigit() and sell_pure.isdigit():
                            data_row = {
                                '고시날짜': date,
                                '내가살때_순금(3.75g)': int(buy_pure),
                                '내가팔때_순금(3.75g)': int(sell_pure),
                                '내가팔때_18K(3.75g)': int(sell_18k) if sell_18k.isdigit() else 0,
                                '내가팔때_14K(3.75g)': int(sell_14k) if sell_14k.isdigit() else 0
                            }
                            self.data.append(data_row)
                            logger.info(f"데이터 추출: {date} - 순금구매: {buy_pure}, 순금판매: {sell_pure}")
                
                except Exception as e:
                    logger.warning(f"행 데이터 추출 실패: {e}")
                    continue
            
            logger.info(f"총 {len(self.data)}개 데이터 추출 완료")
            return len(self.data) > 0
            
        except Exception as e:
            logger.error(f"테이블 데이터 추출 실패: {e}")
            return False
    
    def navigate_pages(self, target_count=100):
        """페이지네이션을 통해 더 많은 데이터 수집"""
        try:
            current_count = len(self.data)
            page_num = 1
            
            while current_count < target_count:
                # 다음 페이지 버튼 찾기
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-page='next']:not([disabled])")
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(3)  # 페이지 로딩 대기
                        
                        # 새 데이터 추출
                        if self.extract_table_data():
                            new_count = len(self.data)
                            page_num += 1
                            logger.info(f"페이지 {page_num} 처리 완료. 현재 데이터 수: {new_count}")
                            
                            if new_count == current_count:  # 더 이상 새 데이터가 없으면 중단
                                logger.info("더 이상 새로운 데이터가 없습니다.")
                                break
                            current_count = new_count
                        else:
                            logger.warning("페이지에서 데이터를 추출할 수 없습니다.")
                            break
                    else:
                        logger.info("다음 페이지 버튼이 비활성화되어 있습니다.")
                        break
                        
                except Exception as e:
                    logger.warning(f"페이지 네비게이션 실패: {e}")
                    break
            
            # 목표 개수에 도달했으면 중단
            if len(self.data) >= target_count:
                self.data = self.data[:target_count]
                logger.info(f"목표 개수 {target_count}개에 도달하여 수집을 중단합니다.")
            
            return True
            
        except Exception as e:
            logger.error(f"페이지 네비게이션 실패: {e}")
            return False
    
    def save_to_excel(self, filename="gold_prices.xlsx"):
        """데이터를 엑셀 파일로 저장"""
        try:
            if not self.data:
                logger.warning("저장할 데이터가 없습니다.")
                return False
            
            df = pd.DataFrame(self.data)
            
            # 날짜 컬럼을 datetime으로 변환
            df['고시날짜'] = pd.to_datetime(df['고시날짜'], format='%Y.%m.%d')
            
            # 날짜순으로 정렬
            df = df.sort_values('고시날짜', ascending=False)
            
            # 엑셀 파일로 저장
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='금시세', index=False)
                
                # 워크시트 스타일링
                worksheet = writer.sheets['금시세']
                
                # 컬럼 너비 조정
                column_widths = {
                    'A': 15,  # 고시날짜
                    'B': 20,  # 내가살때_순금
                    'C': 20,  # 내가팔때_순금
                    'D': 20,  # 내가팔때_18K
                    'E': 20   # 내가팔때_14K
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
            
            logger.info(f"데이터가 {filename}에 저장되었습니다. (총 {len(df)}개 행)")
            return True
            
        except Exception as e:
            logger.error(f"엑셀 파일 저장 실패: {e}")
            return False
    
    def run(self, target_count=100):
        """크롤링 실행"""
        try:
            logger.info("금 시세 크롤링을 시작합니다.")
            
            # WebDriver 설정
            if not self.setup_driver():
                return False
            
            # 페이지 로드
            if not self.load_page():
                return False
            
            # 첫 페이지 데이터 추출
            if not self.extract_table_data():
                return False
            
            # 추가 페이지에서 데이터 수집
            if len(self.data) < target_count:
                self.navigate_pages(target_count)
            
            # 엑셀 파일로 저장
            if self.data:
                self.save_to_excel()
                logger.info(f"크롤링 완료! 총 {len(self.data)}개의 데이터를 수집했습니다.")
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
    crawler = GoldPriceCrawler()
    success = crawler.run(target_count=100)
    
    if success:
        print("✅ 금 시세 크롤링이 성공적으로 완료되었습니다!")
        print("📁 gold_prices.xlsx 파일을 확인해주세요.")
    else:
        print("❌ 금 시세 크롤링에 실패했습니다.")

if __name__ == "__main__":
    main()

