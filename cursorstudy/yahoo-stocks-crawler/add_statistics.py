#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 주식 데이터 통계 분석 및 엑셀 파일 업데이트
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_stock_data(df):
    """주식 데이터 분석 및 통계 계산"""
    try:
        # 변동률을 숫자로 변환
        df['Change_Percent_Numeric'] = df['Change_Percent'].str.replace('%', '').str.replace('+', '').astype(float)
        
        # 기본 통계 계산
        stats = {
            '총_주식_수': len(df),
            '평균_변동률': round(df['Change_Percent_Numeric'].mean(), 2),
            '최대_변동률': round(df['Change_Percent_Numeric'].max(), 2),
            '최소_변동률': round(df['Change_Percent_Numeric'].min(), 2),
            '변동률_표준편차': round(df['Change_Percent_Numeric'].std(), 2),
            '평균_가격변동': round(df['Price_Change'].mean(), 2),
            '최대_가격변동': round(df['Price_Change'].max(), 2),
            '최소_가격변동': round(df['Price_Change'].min(), 2),
            '평균_PE비율': round(df['PE_Ratio'].mean(), 2),
            '최대_PE비율': round(df['PE_Ratio'].max(), 2),
            '최소_PE비율': round(df['PE_Ratio'].min(), 2)
        }
        
        # 변동률 구간별 분석
        high_gainers = df[df['Change_Percent_Numeric'] >= 20]
        medium_gainers = df[(df['Change_Percent_Numeric'] >= 10) & (df['Change_Percent_Numeric'] < 20)]
        low_gainers = df[df['Change_Percent_Numeric'] < 10]
        
        stats['고변동률_주식수'] = len(high_gainers)
        stats['중변동률_주식수'] = len(medium_gainers)
        stats['저변동률_주식수'] = len(low_gainers)
        
        # 상위 5개 주식
        top_5 = df.nlargest(5, 'Change_Percent_Numeric')[['Symbol', 'Name', 'Change_Percent', 'Price_Change']]
        
        return stats, top_5, high_gainers, medium_gainers, low_gainers
        
    except Exception as e:
        logger.error(f"데이터 분석 실패: {e}")
        return None, None, None, None, None

def create_summary_sheet(stats, top_5, high_gainers, medium_gainers, low_gainers):
    """요약 시트 생성"""
    try:
        # 통계 요약 데이터프레임 생성
        summary_data = []
        for key, value in stats.items():
            summary_data.append({'항목': key, '값': value})
        
        summary_df = pd.DataFrame(summary_data)
        
        # 변동률 구간별 요약
        category_summary = pd.DataFrame({
            '구간': ['고변동률 (20% 이상)', '중변동률 (10-20%)', '저변동률 (10% 미만)'],
            '주식수': [stats['고변동률_주식수'], stats['중변동률_주식수'], stats['저변동률_주식수']],
            '비율': [
                f"{stats['고변동률_주식수']/stats['총_주식_수']*100:.1f}%",
                f"{stats['중변동률_주식수']/stats['총_주식_수']*100:.1f}%",
                f"{stats['저변동률_주식수']/stats['총_주식_수']*100:.1f}%"
            ]
        })
        
        return summary_df, category_summary, top_5
        
    except Exception as e:
        logger.error(f"요약 시트 생성 실패: {e}")
        return None, None, None

def update_excel_with_statistics(filename="yahoo_stocks_gainers.xlsx"):
    """엑셀 파일에 통계 정보 추가"""
    try:
        # 기존 데이터 읽기
        df = pd.read_excel(filename)
        logger.info(f"기존 데이터 로드 완료: {len(df)}개 주식")
        
        # 데이터 분석
        stats, top_5, high_gainers, medium_gainers, low_gainers = analyze_stock_data(df)
        if stats is None:
            return False
        
        # 요약 시트 생성
        summary_df, category_summary, top_5_df = create_summary_sheet(stats, top_5, high_gainers, medium_gainers, low_gainers)
        if summary_df is None:
            return False
        
        # 엑셀 파일 업데이트
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 기존 주식 데이터
            df.to_excel(writer, sheet_name='주식상승률', index=False)
            
            # 통계 요약
            summary_df.to_excel(writer, sheet_name='통계요약', index=False)
            
            # 변동률 구간별 분석
            category_summary.to_excel(writer, sheet_name='구간별분석', index=False)
            
            # 상위 5개 주식
            top_5_df.to_excel(writer, sheet_name='상위5개주식', index=False)
            
            # 고변동률 주식
            if len(high_gainers) > 0:
                high_gainers.to_excel(writer, sheet_name='고변동률주식', index=False)
            
            # 중변동률 주식
            if len(medium_gainers) > 0:
                medium_gainers.to_excel(writer, sheet_name='중변동률주식', index=False)
            
            # 저변동률 주식
            if len(low_gainers) > 0:
                low_gainers.to_excel(writer, sheet_name='저변동률주식', index=False)
            
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
        
        logger.info("엑셀 파일 업데이트 완료")
        return True
        
    except Exception as e:
        logger.error(f"엑셀 파일 업데이트 실패: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("주식 데이터 통계 분석을 시작합니다.")
    
    success = update_excel_with_statistics()
    
    if success:
        print("✅ 통계 분석이 완료되었습니다!")
        print("📁 업데이트된 yahoo_stocks_gainers.xlsx 파일을 확인해주세요.")
        print("📊 추가된 시트:")
        print("   - 통계요약: 전체 통계 정보")
        print("   - 구간별분석: 변동률 구간별 주식 분포")
        print("   - 상위5개주식: 변동률 상위 5개 주식")
        print("   - 고변동률주식: 20% 이상 상승한 주식")
        print("   - 중변동률주식: 10-20% 상승한 주식")
        print("   - 저변동률주식: 10% 미만 상승한 주식")
    else:
        print("❌ 통계 분석에 실패했습니다.")

if __name__ == "__main__":
    main()
