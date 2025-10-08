#!/usr/bin/env python3
"""
PDF 페이지 추출기
특정 페이지 범위를 추출하여 날짜가 포함된 새 파일명으로 저장하는 프로그램
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("pypdf 라이브러리가 설치되지 않았습니다.")
    print("다음 명령어로 설치하세요: pip install pypdf")
    sys.exit(1)


def extract_pdf_pages(input_path, start_page, end_page, output_path=None):
    """
    PDF에서 특정 페이지 범위를 추출하여 새 파일로 저장
    
    Args:
        input_path (str): 입력 PDF 파일 경로
        start_page (int): 시작 페이지 번호 (1부터 시작)
        end_page (int): 끝 페이지 번호 (1부터 시작)
        output_path (str, optional): 출력 파일 경로. None이면 자동 생성
    
    Returns:
        str: 생성된 출력 파일 경로
    """
    try:
        # PDF 파일 읽기
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        # 페이지 번호 유효성 검사
        if start_page < 1 or end_page < 1:
            raise ValueError("페이지 번호는 1 이상이어야 합니다.")
        
        if start_page > total_pages:
            raise ValueError(f"시작 페이지({start_page})가 총 페이지 수({total_pages})보다 큽니다.")
        
        if end_page > total_pages:
            print(f"경고: 끝 페이지({end_page})가 총 페이지 수({total_pages})보다 큽니다. {total_pages}로 조정합니다.")
            end_page = total_pages
        
        if start_page > end_page:
            raise ValueError("시작 페이지가 끝 페이지보다 큽니다.")
        
        # 페이지 추출 (0부터 시작하는 인덱스로 변환)
        writer = PdfWriter()
        for page_num in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page_num])
        
        # 출력 파일 경로 생성
        if output_path is None:
            input_file = Path(input_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{input_file.stem}_pages_{start_page}-{end_page}_{timestamp}.pdf"
            output_path = input_file.parent / output_filename
        
        # 파일 저장
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return str(output_path)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")
    except Exception as e:
        raise Exception(f"PDF 처리 중 오류가 발생했습니다: {str(e)}")


def get_user_input():
    """사용자로부터 입력을 받는 함수"""
    print("=== PDF 페이지 추출기 ===")
    print()
    
    # 파일 경로 입력
    while True:
        file_path = input("PDF 파일 경로를 입력하세요: ").strip()
        if not file_path:
            print("파일 경로를 입력해주세요.")
            continue
        
        # 따옴표 제거
        file_path = file_path.strip('"\'')
        
        if not os.path.exists(file_path):
            print(f"파일을 찾을 수 없습니다: {file_path}")
            continue
        
        if not file_path.lower().endswith('.pdf'):
            print("PDF 파일만 지원됩니다.")
            continue
        
        break
    
    # 페이지 범위 입력
    while True:
        try:
            start_page = int(input("시작 페이지 번호를 입력하세요 (1부터 시작): "))
            if start_page < 1:
                print("페이지 번호는 1 이상이어야 합니다.")
                continue
            break
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
    
    while True:
        try:
            end_page = int(input("끝 페이지 번호를 입력하세요: "))
            if end_page < start_page:
                print(f"끝 페이지는 시작 페이지({start_page}) 이상이어야 합니다.")
                continue
            break
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
    
    return file_path, start_page, end_page


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="PDF에서 특정 페이지 범위를 추출합니다.")
    parser.add_argument("input_file", nargs="?", help="입력 PDF 파일 경로")
    parser.add_argument("-s", "--start", type=int, help="시작 페이지 번호 (1부터 시작)")
    parser.add_argument("-e", "--end", type=int, help="끝 페이지 번호")
    parser.add_argument("-o", "--output", help="출력 파일 경로")
    
    args = parser.parse_args()
    
    try:
        if args.input_file and args.start and args.end:
            # 명령행 인수로 실행
            file_path = args.input_file
            start_page = args.start
            end_page = args.end
            output_path = args.output
        else:
            # 대화형 모드로 실행
            file_path, start_page, end_page = get_user_input()
            output_path = None
        
        print(f"\n처리 중...")
        print(f"입력 파일: {file_path}")
        print(f"추출 페이지: {start_page} ~ {end_page}")
        
        # 페이지 추출 실행
        result_path = extract_pdf_pages(file_path, start_page, end_page, output_path)
        
        print(f"✅ 성공적으로 추출되었습니다!")
        print(f"출력 파일: {result_path}")
        
        # 파일 크기 정보
        file_size = os.path.getsize(result_path)
        print(f"파일 크기: {file_size:,} bytes")
        
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
