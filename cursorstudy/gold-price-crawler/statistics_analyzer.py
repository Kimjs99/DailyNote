#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
금 시세 데이터 통계 분석기
크롤링된 금 시세 데이터를 분석하여 통계값을 계산하고 엑셀에 저장
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoldPriceAnalyzer:
    def __init__(self, excel_file="gold_prices.xlsx"):
        self.excel_file = excel_file
        self.df = None
        self.stats_data = {}
        
    def load_data(self):
        """엑셀 파일에서 데이터 로드"""
        try:
            self.df = pd.read_excel(self.excel_file)
            logger.info(f"데이터 로드 완료: {len(self.df)}개 행")
            return True
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return False
    
    def calculate_basic_statistics(self):
        """기본 통계값 계산"""
        try:
            # 각 금 종류별 기본 통계
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            
            basic_stats = {}
            for col in price_columns:
                basic_stats[col] = {
                    '평균': round(self.df[col].mean(), 0),
                    '중앙값': round(self.df[col].median(), 0),
                    '최고가': self.df[col].max(),
                    '최저가': self.df[col].min(),
                    '표준편차': round(self.df[col].std(), 0),
                    '변동계수': round((self.df[col].std() / self.df[col].mean()) * 100, 2),
                    '범위': self.df[col].max() - self.df[col].min()
                }
            
            self.stats_data['기본통계'] = basic_stats
            logger.info("기본 통계 계산 완료")
            return True
            
        except Exception as e:
            logger.error(f"기본 통계 계산 실패: {e}")
            return False
    
    def calculate_price_changes(self):
        """가격 변동 분석"""
        try:
            # 날짜순으로 정렬
            df_sorted = self.df.sort_values('고시날짜')
            
            price_changes = {}
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            
            for col in price_columns:
                # 일일 변동률 계산
                daily_changes = df_sorted[col].pct_change() * 100
                
                # 가격 변동 통계
                price_changes[col] = {
                    '최대상승률': round(daily_changes.max(), 2),
                    '최대하락률': round(daily_changes.min(), 2),
                    '평균변동률': round(daily_changes.mean(), 2),
                    '변동률_표준편차': round(daily_changes.std(), 2),
                    '상승일수': (daily_changes > 0).sum(),
                    '하락일수': (daily_changes < 0).sum(),
                    '보합일수': (daily_changes == 0).sum()
                }
            
            self.stats_data['가격변동'] = price_changes
            logger.info("가격 변동 분석 완료")
            return True
            
        except Exception as e:
            logger.error(f"가격 변동 분석 실패: {e}")
            return False
    
    def calculate_period_analysis(self):
        """기간별 분석"""
        try:
            # 최근 7일, 30일, 전체 기간 분석
            df_sorted = self.df.sort_values('고시날짜')
            
            # 전체 기간
            total_days = (df_sorted['고시날짜'].max() - df_sorted['고시날짜'].min()).days
            
            # 최근 30일 데이터
            recent_30_days = df_sorted[df_sorted['고시날짜'] >= (df_sorted['고시날짜'].max() - timedelta(days=30))]
            
            # 최근 7일 데이터
            recent_7_days = df_sorted[df_sorted['고시날짜'] >= (df_sorted['고시날짜'].max() - timedelta(days=7))]
            
            period_analysis = {
                '전체기간': {
                    '기간': f"{total_days}일",
                    '데이터수': len(df_sorted),
                    '시작일': df_sorted['고시날짜'].min().strftime('%Y-%m-%d'),
                    '종료일': df_sorted['고시날짜'].max().strftime('%Y-%m-%d')
                },
                '최근30일': {
                    '기간': '30일',
                    '데이터수': len(recent_30_days),
                    '시작일': recent_30_days['고시날짜'].min().strftime('%Y-%m-%d') if len(recent_30_days) > 0 else 'N/A',
                    '종료일': recent_30_days['고시날짜'].max().strftime('%Y-%m-%d') if len(recent_30_days) > 0 else 'N/A'
                },
                '최근7일': {
                    '기간': '7일',
                    '데이터수': len(recent_7_days),
                    '시작일': recent_7_days['고시날짜'].min().strftime('%Y-%m-%d') if len(recent_7_days) > 0 else 'N/A',
                    '종료일': recent_7_days['고시날짜'].max().strftime('%Y-%m-%d') if len(recent_7_days) > 0 else 'N/A'
                }
            }
            
            # 각 기간별 가격 통계 추가
            for period_name, period_df in [('전체기간', df_sorted), ('최근30일', recent_30_days), ('최근7일', recent_7_days)]:
                if len(period_df) > 0:
                    for col in ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)']:
                        period_analysis[period_name][f'{col}_평균'] = round(period_df[col].mean(), 0)
                        period_analysis[period_name][f'{col}_최고가'] = period_df[col].max()
                        period_analysis[period_name][f'{col}_최저가'] = period_df[col].min()
            
            self.stats_data['기간별분석'] = period_analysis
            logger.info("기간별 분석 완료")
            return True
            
        except Exception as e:
            logger.error(f"기간별 분석 실패: {e}")
            return False
    
    def calculate_correlation_analysis(self):
        """상관관계 분석"""
        try:
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            
            # 상관계수 계산
            correlation_matrix = self.df[price_columns].corr()
            
            # 주요 상관관계 추출
            correlations = {}
            for i, col1 in enumerate(price_columns):
                for j, col2 in enumerate(price_columns):
                    if i < j:  # 중복 제거
                        corr_value = correlation_matrix.loc[col1, col2]
                        correlations[f"{col1} vs {col2}"] = round(corr_value, 4)
            
            self.stats_data['상관관계'] = correlations
            logger.info("상관관계 분석 완료")
            return True
            
        except Exception as e:
            logger.error(f"상관관계 분석 실패: {e}")
            return False
    
    def create_summary_table(self):
        """요약 테이블 생성"""
        try:
            # 요약 데이터 생성
            summary_data = []
            
            # 기본 통계 요약
            for col, stats in self.stats_data['기본통계'].items():
                summary_data.append({
                    '구분': col,
                    '항목': '평균',
                    '값': f"{stats['평균']:,}원"
                })
                summary_data.append({
                    '구분': col,
                    '항목': '최고가',
                    '값': f"{stats['최고가']:,}원"
                })
                summary_data.append({
                    '구분': col,
                    '항목': '최저가',
                    '값': f"{stats['최저가']:,}원"
                })
                summary_data.append({
                    '구분': col,
                    '항목': '변동폭',
                    '값': f"{stats['범위']:,}원"
                })
                summary_data.append({
                    '구분': col,
                    '항목': '변동계수',
                    '값': f"{stats['변동계수']}%"
                })
            
            self.stats_data['요약테이블'] = pd.DataFrame(summary_data)
            logger.info("요약 테이블 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"요약 테이블 생성 실패: {e}")
            return False
    
    def save_to_excel(self, output_file="gold_prices_with_statistics.xlsx"):
        """통계 데이터를 포함한 엑셀 파일 저장"""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 원본 데이터
                self.df.to_excel(writer, sheet_name='원본데이터', index=False)
                
                # 기본 통계
                basic_stats_df = pd.DataFrame(self.stats_data['기본통계']).T
                basic_stats_df.to_excel(writer, sheet_name='기본통계')
                
                # 가격 변동 분석
                price_changes_df = pd.DataFrame(self.stats_data['가격변동']).T
                price_changes_df.to_excel(writer, sheet_name='가격변동분석')
                
                # 기간별 분석
                period_analysis_df = pd.DataFrame(self.stats_data['기간별분석']).T
                period_analysis_df.to_excel(writer, sheet_name='기간별분석')
                
                # 상관관계 분석
                correlation_df = pd.DataFrame(list(self.stats_data['상관관계'].items()), 
                                            columns=['금종류', '상관계수'])
                correlation_df.to_excel(writer, sheet_name='상관관계분석', index=False)
                
                # 요약 테이블
                self.stats_data['요약테이블'].to_excel(writer, sheet_name='요약테이블', index=False)
                
                # 워크시트 스타일링
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    
                    # 컬럼 너비 자동 조정
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"통계 데이터가 포함된 엑셀 파일이 저장되었습니다: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"엑셀 파일 저장 실패: {e}")
            return False
    
    def run_analysis(self):
        """전체 분석 실행"""
        try:
            logger.info("금 시세 데이터 분석을 시작합니다.")
            
            # 데이터 로드
            if not self.load_data():
                return False
            
            # 각종 분석 수행
            self.calculate_basic_statistics()
            self.calculate_price_changes()
            self.calculate_period_analysis()
            self.calculate_correlation_analysis()
            self.create_summary_table()
            
            # 엑셀 파일로 저장
            if self.save_to_excel():
                logger.info("분석 완료!")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"분석 실행 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    analyzer = GoldPriceAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("✅ 금 시세 데이터 분석이 성공적으로 완료되었습니다!")
        print("📁 gold_prices_with_statistics.xlsx 파일을 확인해주세요.")
        print("\n📊 포함된 분석 내용:")
        print("- 기본통계: 평균, 최고가, 최저가, 변동폭 등")
        print("- 가격변동분석: 일일 변동률, 상승/하락 일수")
        print("- 기간별분석: 전체기간, 최근30일, 최근7일")
        print("- 상관관계분석: 각 금 종류 간 상관계수")
        print("- 요약테이블: 주요 통계값 요약")
    else:
        print("❌ 금 시세 데이터 분석에 실패했습니다.")

if __name__ == "__main__":
    main()
