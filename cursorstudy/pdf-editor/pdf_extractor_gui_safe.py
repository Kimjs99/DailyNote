#!/usr/bin/env python3
"""
PDF 페이지 추출기 - 안전한 GUI 버전
종료 버튼 추가 및 예기치 않은 종료 방지
"""

import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import tkinter as tk

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    messagebox.showerror("오류", "pypdf 라이브러리가 설치되지 않았습니다.\n다음 명령어로 설치하세요: pip install pypdf")
    sys.exit(1)


class PDFExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 페이지 추출기")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # 변수 초기화
        self.input_file_path = StringVar()
        self.output_file_path = StringVar()
        self.start_page = StringVar(value="1")
        self.end_page = StringVar()
        
        # 상태 변수
        self.is_processing = False
        self.is_closing = False
        
        # 앱 종료 시 정리 작업
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # GUI 초기화
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성 요소 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="PDF 페이지 추출기", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 입력 파일 선택
        ttk.Label(main_frame, text="PDF 파일:").grid(row=1, column=0, sticky=W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file_path, width=50).grid(
            row=1, column=1, sticky=(W, E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="찾아보기", 
                  command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        # 페이지 범위 입력
        page_frame = ttk.LabelFrame(main_frame, text="페이지 범위", padding="10")
        page_frame.grid(row=2, column=0, columnspan=3, sticky=(W, E), pady=10)
        
        ttk.Label(page_frame, text="시작 페이지:").grid(row=0, column=0, sticky=W, padx=(0, 5))
        start_spinbox = ttk.Spinbox(page_frame, from_=1, to=9999, width=10, 
                                   textvariable=self.start_page)
        start_spinbox.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(page_frame, text="끝 페이지:").grid(row=0, column=2, sticky=W, padx=(0, 5))
        end_spinbox = ttk.Spinbox(page_frame, from_=1, to=9999, width=10, 
                                 textvariable=self.end_page)
        end_spinbox.grid(row=0, column=3)
        
        # 출력 파일 선택
        ttk.Label(main_frame, text="저장 위치:").grid(row=3, column=0, sticky=W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file_path, width=50).grid(
            row=3, column=1, sticky=(W, E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="찾아보기", 
                  command=self.browse_output_file).grid(row=3, column=2, pady=5)
        
        # 자동 파일명 생성 체크박스
        self.auto_filename = BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="자동으로 파일명 생성 (날짜/시간 포함)", 
                       variable=self.auto_filename,
                       command=self.toggle_auto_filename).grid(
            row=4, column=0, columnspan=3, sticky=W, pady=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 추출 버튼
        self.extract_button = ttk.Button(button_frame, text="📄 페이지 추출", 
                                        command=self.extract_pages,
                                        style="Accent.TButton")
        self.extract_button.grid(row=0, column=0, padx=(0, 10))
        
        # 종료 버튼 추가
        self.exit_button = ttk.Button(button_frame, text="🚪 안전하게 종료", 
                                     command=self.safe_exit)
        self.exit_button.grid(row=0, column=1, padx=(10, 0))
        
        # 진행 상황 표시
        self.progress_var = StringVar(value="준비됨")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(
            row=6, column=0, columnspan=3, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(W, E), pady=5)
        
        # 결과 텍스트 영역
        result_frame = ttk.LabelFrame(main_frame, text="결과", padding="10")
        result_frame.grid(row=8, column=0, columnspan=3, sticky=(W, E, N, S), pady=10)
        
        self.result_text = Text(result_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(W, E, N, S))
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        # 상태 표시
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=9, column=0, columnspan=3, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="상태: 대기 중", 
                                     font=("Arial", 10, "italic"))
        self.status_label.grid(row=0, column=0)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
    def safe_exit(self):
        """안전한 종료"""
        if self.is_processing:
            if messagebox.askokcancel("종료 확인", 
                                    "작업이 진행 중입니다.\n정말 종료하시겠습니까?"):
                self.is_processing = False
                self.is_closing = True
                self.update_status("종료 중...")
                self.root.after(1000, self.force_exit)
        else:
            if messagebox.askokcancel("종료 확인", 
                                    "PDF 페이지 추출기를 종료하시겠습니까?"):
                self.is_closing = True
                self.update_status("종료 중...")
                self.root.after(500, self.force_exit)
    
    def force_exit(self):
        """강제 종료"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            os._exit(0)
    
    def on_closing(self):
        """창 닫기 이벤트 처리"""
        self.safe_exit()
    
    def update_status(self, status):
        """상태 업데이트"""
        self.status_label.config(text=f"상태: {status}")
        self.root.update_idletasks()
    
    def toggle_auto_filename(self):
        """자동 파일명 생성 토글"""
        if self.auto_filename.get():
            self.output_file_path.set("")
            # 출력 파일 입력 필드 비활성화
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Entry) and child.cget('textvariable') == self.output_file_path:
                            child.configure(state='disabled')
        else:
            # 출력 파일 입력 필드 활성화
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Entry) and child.cget('textvariable') == self.output_file_path:
                            child.configure(state='normal')
    
    def browse_input_file(self):
        """입력 파일 선택 다이얼로그"""
        filename = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_path.set(filename)
            # 자동으로 끝 페이지 설정 (PDF 페이지 수 확인)
            self.set_pdf_page_count(filename)
    
    def browse_output_file(self):
        """출력 파일 선택 다이얼로그"""
        filename = filedialog.asksaveasfilename(
            title="저장할 위치 선택",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_path.set(filename)
            self.auto_filename.set(False)
    
    def set_pdf_page_count(self, filepath):
        """PDF 파일의 페이지 수를 확인하고 끝 페이지 설정"""
        try:
            reader = PdfReader(filepath)
            total_pages = len(reader.pages)
            self.end_page.set(str(total_pages))
            self.log_message(f"PDF 파일 로드됨: {total_pages}페이지")
            self.update_status("PDF 파일 로드 완료")
        except Exception as e:
            self.log_message(f"PDF 파일 읽기 오류: {str(e)}")
            self.update_status("PDF 파일 읽기 오류")
    
    def log_message(self, message):
        """결과 텍스트 영역에 메시지 추가"""
        if self.is_closing:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(END, f"[{timestamp}] {message}\n")
        self.result_text.see(END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """입력 값 유효성 검사"""
        if not self.input_file_path.get():
            messagebox.showerror("오류", "PDF 파일을 선택해주세요.")
            return False
        
        if not os.path.exists(self.input_file_path.get()):
            messagebox.showerror("오류", "선택한 파일이 존재하지 않습니다.")
            return False
        
        try:
            start = int(self.start_page.get())
            end = int(self.end_page.get())
            
            if start < 1 or end < 1:
                messagebox.showerror("오류", "페이지 번호는 1 이상이어야 합니다.")
                return False
            
            if start > end:
                messagebox.showerror("오류", "시작 페이지가 끝 페이지보다 큽니다.")
                return False
                
        except ValueError:
            messagebox.showerror("오류", "페이지 번호는 숫자여야 합니다.")
            return False
        
        if not self.auto_filename.get() and not self.output_file_path.get():
            messagebox.showerror("오류", "저장 위치를 선택하거나 자동 파일명 생성을 활성화해주세요.")
            return False
        
        return True
    
    def extract_pages(self):
        """페이지 추출 실행"""
        if not self.validate_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("경고", "이미 작업이 진행 중입니다.")
            return
        
        # UI 비활성화
        self.is_processing = True
        self.extract_button.configure(state='disabled')
        self.exit_button.configure(state='disabled')
        self.progress_bar.start()
        self.progress_var.set("처리 중...")
        self.update_status("페이지 추출 중...")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._extract_pages_thread)
        thread.daemon = True
        thread.start()
    
    def _extract_pages_thread(self):
        """페이지 추출 스레드"""
        try:
            input_path = self.input_file_path.get()
            start_page = int(self.start_page.get())
            end_page = int(self.end_page.get())
            
            # 출력 파일 경로 결정
            if self.auto_filename.get():
                input_file = Path(input_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{input_file.stem}_pages_{start_page}-{end_page}_{timestamp}.pdf"
                output_path = input_file.parent / output_filename
            else:
                output_path = self.output_file_path.get()
            
            self.log_message(f"입력 파일: {input_path}")
            self.log_message(f"추출 페이지: {start_page} ~ {end_page}")
            self.log_message(f"출력 파일: {output_path}")
            
            # PDF 처리
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            if end_page > total_pages:
                self.log_message(f"경고: 끝 페이지({end_page})가 총 페이지 수({total_pages})보다 큽니다.")
                end_page = total_pages
            
            writer = PdfWriter()
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])
            
            # 파일 저장
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # 결과 표시
            file_size = os.path.getsize(output_path)
            self.log_message(f"✅ 성공적으로 추출되었습니다!")
            self.log_message(f"파일 크기: {file_size:,} bytes")
            self.log_message(f"저장 위치: {output_path}")
            
            # UI 업데이트
            self.root.after(0, self._extraction_complete)
            
        except Exception as e:
            self.log_message(f"❌ 오류: {str(e)}")
            self.root.after(0, self._extraction_error)
    
    def _extraction_complete(self):
        """추출 완료 후 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("완료!")
        self.extract_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("추출 완료")
        messagebox.showinfo("완료", "페이지 추출이 완료되었습니다!")
    
    def _extraction_error(self):
        """추출 오류 시 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("오류 발생")
        self.extract_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("오류 발생")


def main():
    """메인 함수"""
    # 중복 실행 방지
    import fcntl
    lock_file = "/tmp/pdf_extractor_gui_safe.lock"
    
    try:
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, IOError):
        messagebox.showerror("오류", "PDF 페이지 추출기가 이미 실행 중입니다.")
        sys.exit(1)
    
    root = tk.Tk()
    
    # 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')
    
    # 앱 실행
    app = PDFExtractorGUI(root)
    
    # 창 닫기 이벤트 처리
    def cleanup():
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            os.unlink(lock_file)
        except:
            pass
    
    root.protocol("WM_DELETE_WINDOW", lambda: [cleanup(), root.destroy()])
    
    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
