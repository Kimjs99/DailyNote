#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
금 시세 데이터 시각화 생성기
크롤링된 금 시세 데이터를 다양한 차트로 시각화하여 PNG 파일로 저장
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 스타일 설정
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class GoldPriceVisualizer:
    def __init__(self, excel_file="gold_prices_with_statistics.xlsx"):
        self.excel_file = excel_file
        self.df = None
        self.output_dir = "visualizations"
        
    def load_data(self):
        """데이터 로드"""
        try:
            self.df = pd.read_excel(self.excel_file, sheet_name='원본데이터')
            self.df['고시날짜'] = pd.to_datetime(self.df['고시날짜'])
            self.df = self.df.sort_values('고시날짜')
            print(f"데이터 로드 완료: {len(self.df)}개 행")
            return True
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return False
    
    def create_output_directory(self):
        """출력 디렉토리 생성"""
        import os
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"출력 디렉토리 생성: {self.output_dir}")
    
    def plot_price_trends(self):
        """금 가격 추이 시계열 차트"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Gold Price Trends Over Time', fontsize=16, fontweight='bold')
            
            price_columns = [
                ('내가살때_순금(3.75g)', '순금 구매가 (3.75g)'),
                ('내가팔때_순금(3.75g)', '순금 판매가 (3.75g)'),
                ('내가팔때_18K(3.75g)', '18K 판매가 (3.75g)'),
                ('내가팔때_14K(3.75g)', '14K 판매가 (3.75g)')
            ]
            
            for i, (col, title) in enumerate(price_columns):
                row, col_idx = i // 2, i % 2
                ax = axes[row, col_idx]
                
                ax.plot(self.df['고시날짜'], self.df[col], linewidth=2, marker='o', markersize=3)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel('Price (KRW)')
                ax.grid(True, alpha=0.3)
                
                # 가격 포맷팅
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
                
                # 날짜 포맷팅
                ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/01_price_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 가격 추이 차트 생성 완료: 01_price_trends.png")
            
        except Exception as e:
            print(f"❌ 가격 추이 차트 생성 실패: {e}")
    
    def plot_price_distribution(self):
        """금 가격 분포 히스토그램"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Gold Price Distribution', fontsize=16, fontweight='bold')
            
            price_columns = [
                ('내가살때_순금(3.75g)', '순금 구매가 분포'),
                ('내가팔때_순금(3.75g)', '순금 판매가 분포'),
                ('내가팔때_18K(3.75g)', '18K 판매가 분포'),
                ('내가팔때_14K(3.75g)', '14K 판매가 분포')
            ]
            
            for i, (col, title) in enumerate(price_columns):
                row, col_idx = i // 2, i % 2
                ax = axes[row, col_idx]
                
                # 히스토그램과 KDE
                sns.histplot(data=self.df, x=col, kde=True, ax=ax, alpha=0.7)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Price (KRW)')
                ax.set_ylabel('Frequency')
                
                # 가격 포맷팅
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
                
                # 통계 정보 추가
                mean_price = self.df[col].mean()
                median_price = self.df[col].median()
                ax.axvline(mean_price, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_price:,.0f}')
                ax.axvline(median_price, color='green', linestyle='--', alpha=0.7, label=f'Median: {median_price:,.0f}')
                ax.legend()
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/02_price_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 가격 분포 히스토그램 생성 완료: 02_price_distribution.png")
            
        except Exception as e:
            print(f"❌ 가격 분포 히스토그램 생성 실패: {e}")
    
    def plot_correlation_heatmap(self):
        """상관관계 히트맵"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 상관관계 계산
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            correlation_matrix = self.df[price_columns].corr()
            
            # 히트맵 생성
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, fmt='.3f', cbar_kws={'shrink': 0.8})
            
            ax.set_title('Gold Price Correlation Matrix', fontsize=16, fontweight='bold')
            
            # 축 레이블 설정
            labels = ['순금 구매가', '순금 판매가', '18K 판매가', '14K 판매가']
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.set_yticklabels(labels, rotation=0)
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/03_correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 상관관계 히트맵 생성 완료: 03_correlation_heatmap.png")
            
        except Exception as e:
            print(f"❌ 상관관계 히트맵 생성 실패: {e}")
    
    def plot_price_changes(self):
        """가격 변동률 분석"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Daily Price Changes Analysis', fontsize=16, fontweight='bold')
            
            price_columns = [
                ('내가살때_순금(3.75g)', '순금 구매가 변동률'),
                ('내가팔때_순금(3.75g)', '순금 판매가 변동률'),
                ('내가팔때_18K(3.75g)', '18K 판매가 변동률'),
                ('내가팔때_14K(3.75g)', '14K 판매가 변동률')
            ]
            
            for i, (col, title) in enumerate(price_columns):
                row, col_idx = i // 2, i % 2
                ax = axes[row, col_idx]
                
                # 일일 변동률 계산
                daily_changes = self.df[col].pct_change() * 100
                
                # 변동률 히스토그램
                ax.hist(daily_changes.dropna(), bins=20, alpha=0.7, edgecolor='black')
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Daily Change (%)')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
                
                # 통계 정보 추가
                mean_change = daily_changes.mean()
                std_change = daily_changes.std()
                ax.axvline(mean_change, color='red', linestyle='--', alpha=0.7, 
                          label=f'Mean: {mean_change:.2f}%')
                ax.axvline(mean_change + std_change, color='orange', linestyle='--', alpha=0.7, 
                          label=f'+1σ: {mean_change + std_change:.2f}%')
                ax.axvline(mean_change - std_change, color='orange', linestyle='--', alpha=0.7, 
                          label=f'-1σ: {mean_change - std_change:.2f}%')
                ax.legend()
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/04_price_changes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 가격 변동률 분석 차트 생성 완료: 04_price_changes.png")
            
        except Exception as e:
            print(f"❌ 가격 변동률 분석 차트 생성 실패: {e}")
    
    def plot_period_comparison(self):
        """기간별 평균 가격 비교"""
        try:
            # 기간별 데이터 분할
            total_period = self.df
            recent_30_days = self.df[self.df['고시날짜'] >= (self.df['고시날짜'].max() - timedelta(days=30))]
            recent_7_days = self.df[self.df['고시날짜'] >= (self.df['고시날짜'].max() - timedelta(days=7))]
            
            periods = {
                '전체기간': total_period,
                '최근30일': recent_30_days,
                '최근7일': recent_7_days
            }
            
            # 각 기간별 평균 가격 계산
            period_means = {}
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            
            for period_name, period_data in periods.items():
                if len(period_data) > 0:
                    period_means[period_name] = [period_data[col].mean() for col in price_columns]
            
            # 막대 차트 생성
            fig, ax = plt.subplots(figsize=(14, 8))
            
            x = np.arange(len(price_columns))
            width = 0.25
            
            for i, (period_name, means) in enumerate(period_means.items()):
                ax.bar(x + i * width, means, width, label=period_name, alpha=0.8)
            
            ax.set_xlabel('Gold Types')
            ax.set_ylabel('Average Price (KRW)')
            ax.set_title('Average Gold Prices by Period', fontsize=16, fontweight='bold')
            ax.set_xticks(x + width)
            ax.set_xticklabels(['순금 구매가', '순금 판매가', '18K 판매가', '14K 판매가'])
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 가격 포맷팅
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/05_period_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 기간별 평균 가격 비교 차트 생성 완료: 05_period_comparison.png")
            
        except Exception as e:
            print(f"❌ 기간별 평균 가격 비교 차트 생성 실패: {e}")
    
    def plot_box_plots(self):
        """금 종류별 가격 박스플롯"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 데이터 준비
            price_data = []
            labels = []
            
            price_columns = [
                ('내가살때_순금(3.75g)', '순금 구매가'),
                ('내가팔때_순금(3.75g)', '순금 판매가'),
                ('내가팔때_18K(3.75g)', '18K 판매가'),
                ('내가팔때_14K(3.75g)', '14K 판매가')
            ]
            
            for col, label in price_columns:
                price_data.append(self.df[col])
                labels.append(label)
            
            # 박스플롯 생성
            box_plot = ax.boxplot(price_data, labels=labels, patch_artist=True)
            
            # 색상 설정
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_title('Gold Price Distribution by Type', fontsize=16, fontweight='bold')
            ax.set_ylabel('Price (KRW)')
            ax.grid(True, alpha=0.3)
            
            # 가격 포맷팅
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/06_box_plots.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 박스플롯 생성 완료: 06_box_plots.png")
            
        except Exception as e:
            print(f"❌ 박스플롯 생성 실패: {e}")
    
    def plot_dashboard(self):
        """통합 대시보드"""
        try:
            fig = plt.figure(figsize=(20, 16))
            fig.suptitle('Gold Price Analysis Dashboard', fontsize=20, fontweight='bold')
            
            # 1. 가격 추이 (상단 좌측)
            ax1 = plt.subplot(3, 3, 1)
            ax1.plot(self.df['고시날짜'], self.df['내가살때_순금(3.75g)'], label='순금 구매가', linewidth=2)
            ax1.plot(self.df['고시날짜'], self.df['내가팔때_순금(3.75g)'], label='순금 판매가', linewidth=2)
            ax1.set_title('순금 가격 추이')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # 2. 18K/14K 가격 추이 (상단 중앙)
            ax2 = plt.subplot(3, 3, 2)
            ax2.plot(self.df['고시날짜'], self.df['내가팔때_18K(3.75g)'], label='18K 판매가', linewidth=2)
            ax2.plot(self.df['고시날짜'], self.df['내가팔때_14K(3.75g)'], label='14K 판매가', linewidth=2)
            ax2.set_title('18K/14K 가격 추이')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. 상관관계 히트맵 (상단 우측)
            ax3 = plt.subplot(3, 3, 3)
            price_columns = ['내가살때_순금(3.75g)', '내가팔때_순금(3.75g)', '내가팔때_18K(3.75g)', '내가팔때_14K(3.75g)']
            correlation_matrix = self.df[price_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax3, fmt='.2f')
            ax3.set_title('가격 상관관계')
            
            # 4. 가격 분포 (중간 좌측)
            ax4 = plt.subplot(3, 3, 4)
            ax4.hist(self.df['내가살때_순금(3.75g)'], bins=20, alpha=0.7, label='순금 구매가')
            ax4.hist(self.df['내가팔때_순금(3.75g)'], bins=20, alpha=0.7, label='순금 판매가')
            ax4.set_title('순금 가격 분포')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # 5. 변동률 분석 (중간 중앙)
            ax5 = plt.subplot(3, 3, 5)
            daily_changes = self.df['내가살때_순금(3.75g)'].pct_change() * 100
            ax5.hist(daily_changes.dropna(), bins=20, alpha=0.7, edgecolor='black')
            ax5.set_title('순금 구매가 일일 변동률')
            ax5.set_xlabel('Daily Change (%)')
            ax5.grid(True, alpha=0.3)
            
            # 6. 기간별 비교 (중간 우측)
            ax6 = plt.subplot(3, 3, 6)
            recent_30_days = self.df[self.df['고시날짜'] >= (self.df['고시날짜'].max() - timedelta(days=30))]
            recent_7_days = self.df[self.df['고시날짜'] >= (self.df['고시날짜'].max() - timedelta(days=7))]
            
            periods = ['전체기간', '최근30일', '최근7일']
            means = [
                self.df['내가살때_순금(3.75g)'].mean(),
                recent_30_days['내가살때_순금(3.75g)'].mean() if len(recent_30_days) > 0 else 0,
                recent_7_days['내가살때_순금(3.75g)'].mean() if len(recent_7_days) > 0 else 0
            ]
            
            ax6.bar(periods, means, alpha=0.7)
            ax6.set_title('기간별 순금 구매가 평균')
            ax6.set_ylabel('Average Price (KRW)')
            ax6.grid(True, alpha=0.3)
            
            # 7. 통계 요약 (하단)
            ax7 = plt.subplot(3, 3, (7, 9))
            ax7.axis('off')
            
            # 통계 텍스트 생성
            stats_text = f"""
            📊 금 시세 분석 요약 (총 {len(self.df)}개 데이터)
            
            💰 순금 구매가:
            • 평균: {self.df['내가살때_순금(3.75g)'].mean():,.0f}원
            • 최고가: {self.df['내가살때_순금(3.75g)'].max():,.0f}원
            • 최저가: {self.df['내가살때_순금(3.75g)'].min():,.0f}원
            • 변동폭: {self.df['내가살때_순금(3.75g)'].max() - self.df['내가살때_순금(3.75g)'].min():,.0f}원
            
            💰 순금 판매가:
            • 평균: {self.df['내가팔때_순금(3.75g)'].mean():,.0f}원
            • 최고가: {self.df['내가팔때_순금(3.75g)'].max():,.0f}원
            • 최저가: {self.df['내가팔때_순금(3.75g)'].min():,.0f}원
            • 변동폭: {self.df['내가팔때_순금(3.75g)'].max() - self.df['내가팔때_순금(3.75g)'].min():,.0f}원
            
            📈 분석 기간:
            • 시작일: {self.df['고시날짜'].min().strftime('%Y-%m-%d')}
            • 종료일: {self.df['고시날짜'].max().strftime('%Y-%m-%d')}
            • 총 기간: {(self.df['고시날짜'].max() - self.df['고시날짜'].min()).days}일
            """
            
            ax7.text(0.05, 0.95, stats_text, transform=ax7.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/07_dashboard.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("✅ 통합 대시보드 생성 완료: 07_dashboard.png")
            
        except Exception as e:
            print(f"❌ 통합 대시보드 생성 실패: {e}")
    
    def generate_all_visualizations(self):
        """모든 시각화 생성"""
        try:
            print("🎨 금 시세 데이터 시각화를 시작합니다...")
            
            # 출력 디렉토리 생성
            self.create_output_directory()
            
            # 각종 차트 생성
            self.plot_price_trends()
            self.plot_price_distribution()
            self.plot_correlation_heatmap()
            self.plot_price_changes()
            self.plot_period_comparison()
            self.plot_box_plots()
            self.plot_dashboard()
            
            print(f"\n🎉 모든 시각화가 완료되었습니다!")
            print(f"📁 생성된 이미지 파일 위치: {self.output_dir}/")
            print("\n생성된 파일 목록:")
            print("• 01_price_trends.png - 금 가격 추이 시계열 차트")
            print("• 02_price_distribution.png - 금 가격 분포 히스토그램")
            print("• 03_correlation_heatmap.png - 상관관계 히트맵")
            print("• 04_price_changes.png - 가격 변동률 분석")
            print("• 05_period_comparison.png - 기간별 평균 가격 비교")
            print("• 06_box_plots.png - 금 종류별 가격 박스플롯")
            print("• 07_dashboard.png - 통합 대시보드")
            
            return True
            
        except Exception as e:
            print(f"❌ 시각화 생성 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    visualizer = GoldPriceVisualizer()
    
    # 데이터 로드
    if not visualizer.load_data():
        return
    
    # 시각화 생성
    visualizer.generate_all_visualizations()

if __name__ == "__main__":
    main()
