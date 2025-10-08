#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 주식 데이터 시각화 생성
다양한 차트와 그래프를 생성하여 데이터를 시각적으로 분석
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import logging
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataVisualizer:
    def __init__(self, excel_file="yahoo_stocks_gainers.xlsx"):
        self.excel_file = excel_file
        self.df = None
        self.output_dir = "visualizations"
        self.load_data()
        self.create_output_directory()
    
    def load_data(self):
        """데이터 로드"""
        try:
            self.df = pd.read_excel(self.excel_file)
            # 변동률을 숫자로 변환
            self.df['Change_Percent_Numeric'] = self.df['Change_Percent'].str.replace('%', '').str.replace('+', '').astype(float)
            logger.info(f"데이터 로드 완료: {len(self.df)}개 주식")
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
    
    def create_output_directory(self):
        """출력 디렉토리 생성"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"출력 디렉토리 생성: {self.output_dir}")
    
    def create_price_change_distribution(self):
        """가격 변동 분포 히스토그램"""
        plt.figure(figsize=(12, 8))
        
        # 서브플롯 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 가격 변동 히스토그램
        ax1.hist(self.df['Price_Change'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Price Change Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Price Change ($)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 변동률 히스토그램
        ax2.hist(self.df['Change_Percent_Numeric'], bins=10, alpha=0.7, color='lightcoral', edgecolor='black')
        ax2.set_title('Change Percentage Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Change Percentage (%)', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/price_change_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("가격 변동 분포 차트 생성 완료")
    
    def create_top_performers_chart(self):
        """상위 성과 주식 바 차트"""
        plt.figure(figsize=(14, 8))
        
        # 상위 10개 주식 선택
        top_10 = self.df.nlargest(10, 'Change_Percent_Numeric')
        
        # 바 차트 생성
        bars = plt.bar(range(len(top_10)), top_10['Change_Percent_Numeric'], 
                      color=plt.cm.viridis(np.linspace(0, 1, len(top_10))))
        
        # 차트 스타일링
        plt.title('Top 10 Performing Stocks by Change Percentage', fontsize=16, fontweight='bold')
        plt.xlabel('Stocks', fontsize=12)
        plt.ylabel('Change Percentage (%)', fontsize=12)
        plt.xticks(range(len(top_10)), top_10['Symbol'], rotation=45, ha='right')
        
        # 값 표시
        for i, (bar, value) in enumerate(zip(bars, top_10['Change_Percent_Numeric'])):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/top_performers_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("상위 성과 주식 차트 생성 완료")
    
    def create_pe_ratio_analysis(self):
        """PER 비율 분석 차트"""
        plt.figure(figsize=(12, 8))
        
        # 서브플롯 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # PER 비율 분포
        ax1.hist(self.df['PE_Ratio'], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        ax1.set_title('PE Ratio Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('PE Ratio', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # PER vs 변동률 산점도
        scatter = ax2.scatter(self.df['PE_Ratio'], self.df['Change_Percent_Numeric'], 
                            c=self.df['Price_Change'], cmap='viridis', alpha=0.7, s=100)
        ax2.set_title('PE Ratio vs Change Percentage', fontsize=14, fontweight='bold')
        ax2.set_xlabel('PE Ratio', fontsize=12)
        ax2.set_ylabel('Change Percentage (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 컬러바 추가
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Price Change ($)', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/pe_ratio_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("PER 비율 분석 차트 생성 완료")
    
    def create_volume_analysis(self):
        """거래량 분석 차트"""
        plt.figure(figsize=(12, 8))
        
        # 거래량 데이터 정리 (M, K 단위 제거하고 숫자로 변환)
        volume_numeric = []
        for vol in self.df['Volume']:
            if isinstance(vol, str):
                if 'M' in vol:
                    volume_numeric.append(float(vol.replace('M', '')) * 1000000)
                elif 'K' in vol:
                    volume_numeric.append(float(vol.replace('K', '')) * 1000)
                else:
                    try:
                        volume_numeric.append(float(vol))
                    except:
                        volume_numeric.append(0)
            else:
                volume_numeric.append(vol if vol else 0)
        
        self.df['Volume_Numeric'] = volume_numeric
        
        # 서브플롯 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 거래량 분포 (로그 스케일)
        ax1.hist(np.log10(self.df['Volume_Numeric'] + 1), bins=15, alpha=0.7, color='orange', edgecolor='black')
        ax1.set_title('Volume Distribution (Log Scale)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Log10(Volume)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 거래량 vs 변동률
        ax2.scatter(self.df['Volume_Numeric'], self.df['Change_Percent_Numeric'], 
                   c=self.df['Price_Change'], cmap='plasma', alpha=0.7, s=100)
        ax2.set_title('Volume vs Change Percentage', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Volume', fontsize=12)
        ax2.set_ylabel('Change Percentage (%)', fontsize=12)
        ax2.set_xscale('log')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/volume_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("거래량 분석 차트 생성 완료")
    
    def create_performance_categories(self):
        """성과 구간별 분석 차트"""
        plt.figure(figsize=(12, 8))
        
        # 성과 구간 분류
        high_performers = self.df[self.df['Change_Percent_Numeric'] >= 20]
        medium_performers = self.df[(self.df['Change_Percent_Numeric'] >= 10) & (self.df['Change_Percent_Numeric'] < 20)]
        low_performers = self.df[self.df['Change_Percent_Numeric'] < 10]
        
        # 파이 차트
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 성과 구간별 분포
        categories = ['High (≥20%)', 'Medium (10-20%)', 'Low (<10%)']
        counts = [len(high_performers), len(medium_performers), len(low_performers)]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
        
        wedges, texts, autotexts = ax1.pie(counts, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Stock Performance Categories Distribution', fontsize=14, fontweight='bold')
        
        # 성과 구간별 평균 가격 변동
        avg_price_changes = [
            high_performers['Price_Change'].mean(),
            medium_performers['Price_Change'].mean(),
            low_performers['Price_Change'].mean()
        ]
        
        bars = ax2.bar(categories, avg_price_changes, color=colors, alpha=0.7)
        ax2.set_title('Average Price Change by Performance Category', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Price Change ($)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 값 표시
        for bar, value in zip(bars, avg_price_changes):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'${value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/performance_categories.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("성과 구간별 분석 차트 생성 완료")
    
    def create_correlation_heatmap(self):
        """상관관계 히트맵"""
        plt.figure(figsize=(10, 8))
        
        # 수치형 컬럼만 선택
        numeric_columns = ['Price_Change', 'Change_Percent_Numeric', 'PE_Ratio', 'Volume_Numeric']
        correlation_data = self.df[numeric_columns].corr()
        
        # 히트맵 생성
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        
        plt.title('Correlation Heatmap of Stock Metrics', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("상관관계 히트맵 생성 완료")
    
    def create_summary_dashboard(self):
        """종합 대시보드"""
        fig = plt.figure(figsize=(20, 12))
        
        # 2x3 그리드 생성
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. 상위 5개 주식
        ax1 = fig.add_subplot(gs[0, 0])
        top_5 = self.df.nlargest(5, 'Change_Percent_Numeric')
        bars = ax1.bar(range(len(top_5)), top_5['Change_Percent_Numeric'], color='skyblue')
        ax1.set_title('Top 5 Performers', fontweight='bold')
        ax1.set_ylabel('Change %')
        ax1.set_xticks(range(len(top_5)))
        ax1.set_xticklabels(top_5['Symbol'], rotation=45)
        
        # 2. 변동률 분포
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(self.df['Change_Percent_Numeric'], bins=8, alpha=0.7, color='lightcoral')
        ax2.set_title('Change % Distribution', fontweight='bold')
        ax2.set_xlabel('Change %')
        ax2.set_ylabel('Count')
        
        # 3. 가격 변동 분포
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.hist(self.df['Price_Change'], bins=8, alpha=0.7, color='lightgreen')
        ax3.set_title('Price Change Distribution', fontweight='bold')
        ax3.set_xlabel('Price Change ($)')
        ax3.set_ylabel('Count')
        
        # 4. PER vs 변동률
        ax4 = fig.add_subplot(gs[1, 0])
        scatter = ax4.scatter(self.df['PE_Ratio'], self.df['Change_Percent_Numeric'], 
                            c=self.df['Price_Change'], cmap='viridis', alpha=0.7)
        ax4.set_title('PE Ratio vs Change %', fontweight='bold')
        ax4.set_xlabel('PE Ratio')
        ax4.set_ylabel('Change %')
        
        # 5. 성과 구간별 분포
        ax5 = fig.add_subplot(gs[1, 1])
        categories = ['High', 'Medium', 'Low']
        counts = [
            len(self.df[self.df['Change_Percent_Numeric'] >= 20]),
            len(self.df[(self.df['Change_Percent_Numeric'] >= 10) & (self.df['Change_Percent_Numeric'] < 20)]),
            len(self.df[self.df['Change_Percent_Numeric'] < 10])
        ]
        ax5.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax5.set_title('Performance Categories', fontweight='bold')
        
        # 6. 통계 요약 텍스트
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')
        
        stats_text = f"""
        📊 STATISTICS SUMMARY
        
        Total Stocks: {len(self.df)}
        Avg Change: {self.df['Change_Percent_Numeric'].mean():.1f}%
        Max Change: {self.df['Change_Percent_Numeric'].max():.1f}%
        Min Change: {self.df['Change_Percent_Numeric'].min():.1f}%
        
        Avg Price Change: ${self.df['Price_Change'].mean():.2f}
        Max Price Change: ${self.df['Price_Change'].max():.2f}
        
        Avg PE Ratio: {self.df['PE_Ratio'].mean():.1f}
        """
        
        ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.suptitle('Yahoo Finance Stock Gainers - Comprehensive Dashboard', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        plt.savefig(f'{self.output_dir}/summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("종합 대시보드 생성 완료")
    
    def generate_all_visualizations(self):
        """모든 시각화 생성"""
        logger.info("시각화 생성 시작")
        
        try:
            self.create_price_change_distribution()
            self.create_top_performers_chart()
            self.create_pe_ratio_analysis()
            self.create_volume_analysis()
            self.create_performance_categories()
            self.create_correlation_heatmap()
            self.create_summary_dashboard()
            
            logger.info("모든 시각화 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"시각화 생성 실패: {e}")
            return False

def main():
    """메인 함수"""
    visualizer = StockDataVisualizer()
    success = visualizer.generate_all_visualizations()
    
    if success:
        print("✅ 모든 시각화 이미지가 생성되었습니다!")
        print(f"📁 출력 폴더: {visualizer.output_dir}/")
        print("📊 생성된 차트:")
        print("   - price_change_distribution.png: 가격 변동 분포")
        print("   - top_performers_chart.png: 상위 성과 주식")
        print("   - pe_ratio_analysis.png: PER 비율 분석")
        print("   - volume_analysis.png: 거래량 분석")
        print("   - performance_categories.png: 성과 구간별 분석")
        print("   - correlation_heatmap.png: 상관관계 히트맵")
        print("   - summary_dashboard.png: 종합 대시보드")
    else:
        print("❌ 시각화 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
