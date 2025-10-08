#!/usr/bin/env python3
"""
PDF 도구 - 추출 및 병합 기능
PDF 파일 추출과 병합을 모두 지원하는 통합 GUI 도구
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


class PDFToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 도구 - 추출 및 병합")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.minsize(900, 750)  # 최소 크기 설정
        
        # 변수 초기화
        self.input_file_path = StringVar()
        self.output_file_path = StringVar()
        self.start_page = StringVar(value="1")
        self.end_page = StringVar()
        
        # 병합 관련 변수
        self.merge_files = []  # 병합할 파일 목록
        self.merge_output_path = StringVar()
        self.auto_merge_filename = BooleanVar(value=True)  # 자동 파일명 생성
        
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
        title_label = ttk.Label(main_frame, text="PDF 도구 - 추출 및 병합", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 탭 위젯 생성
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(W, E, N, S), pady=10)
        
        # 추출 탭
        extract_frame = ttk.Frame(notebook, padding="10")
        notebook.add(extract_frame, text="📄 페이지 추출")
        
        # 병합 탭
        merge_frame = ttk.Frame(notebook, padding="10")
        notebook.add(merge_frame, text="🔗 파일 병합")
        
        # 추출 탭 설정
        self.setup_extract_tab(extract_frame)
        
        # 병합 탭 설정
        self.setup_merge_tab(merge_frame)
        
        # 초기화: 병합용 자동 파일명 생성 필드 비활성화
        self.toggle_merge_auto_filename()
        
        # 공통 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        # 종료 버튼
        self.exit_button = ttk.Button(button_frame, text="🚪 안전하게 종료", 
                                     command=self.safe_exit)
        self.exit_button.grid(row=0, column=0, padx=10)
        
        # 진행 상황 표시
        self.progress_var = StringVar(value="준비됨")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(
            row=3, column=0, columnspan=3, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(W, E), pady=5)
        
        # 결과 텍스트 영역 (높이 줄임)
        result_frame = ttk.LabelFrame(main_frame, text="결과", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(W, E, N, S), pady=10)
        
        self.result_text = Text(result_frame, height=6, width=80)
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(W, E, N, S))
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        # 상태 표시
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="상태: 대기 중", 
                                     font=("Arial", 10, "italic"))
        self.status_label.grid(row=0, column=0)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
    def setup_extract_tab(self, parent):
        """추출 탭 설정"""
        # 입력 파일 선택
        ttk.Label(parent, text="PDF 파일:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(parent, textvariable=self.input_file_path, width=50).grid(
            row=0, column=1, sticky=(W, E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="찾아보기", 
                  command=self.browse_input_file).grid(row=0, column=2, pady=5)
        
        # 페이지 범위 입력
        page_frame = ttk.LabelFrame(parent, text="페이지 범위", padding="10")
        page_frame.grid(row=1, column=0, columnspan=3, sticky=(W, E), pady=10)
        
        ttk.Label(page_frame, text="시작 페이지:").grid(row=0, column=0, sticky=W, padx=(0, 5))
        start_spinbox = ttk.Spinbox(page_frame, from_=1, to=9999, width=10, 
                                   textvariable=self.start_page)
        start_spinbox.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(page_frame, text="끝 페이지:").grid(row=0, column=2, sticky=W, padx=(0, 5))
        end_spinbox = ttk.Spinbox(page_frame, from_=1, to=9999, width=10, 
                                 textvariable=self.end_page)
        end_spinbox.grid(row=0, column=3)
        
        # 출력 파일 선택
        ttk.Label(parent, text="저장 위치:").grid(row=2, column=0, sticky=W, pady=5)
        ttk.Entry(parent, textvariable=self.output_file_path, width=50).grid(
            row=2, column=1, sticky=(W, E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="찾아보기", 
                  command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # 자동 파일명 생성 체크박스
        self.auto_filename = BooleanVar(value=True)
        ttk.Checkbutton(parent, text="자동으로 파일명 생성 (날짜/시간 포함)", 
                       variable=self.auto_filename,
                       command=self.toggle_auto_filename).grid(
            row=3, column=0, columnspan=3, sticky=W, pady=5)
        
        # 추출 버튼
        self.extract_button = ttk.Button(parent, text="📄 페이지 추출", 
                                        command=self.extract_pages,
                                        style="Accent.TButton")
        self.extract_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # 그리드 가중치 설정
        parent.columnconfigure(1, weight=1)
        
    def setup_merge_tab(self, parent):
        """병합 탭 설정"""
        # 파일 목록 프레임
        list_frame = ttk.LabelFrame(parent, text="병합할 PDF 파일들 (순서대로)", padding="10")
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(W, E, N, S), pady=10)
        
        # 파일 목록 (높이 줄임)
        self.file_listbox = Listbox(list_frame, height=6, width=70)
        file_scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.grid(row=0, column=0, sticky=(W, E, N, S))
        file_scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        # 파일 목록 버튼들 (2줄로 배치)
        file_button_frame = ttk.Frame(list_frame)
        file_button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 첫 번째 줄
        ttk.Button(file_button_frame, text="📁 파일 추가", 
                  command=self.add_merge_files).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(file_button_frame, text="🗑️ 선택 삭제", 
                  command=self.remove_selected_file).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(file_button_frame, text="⬆️ 위로 이동", 
                  command=self.move_file_up).grid(row=0, column=2, padx=2, pady=2)
        ttk.Button(file_button_frame, text="⬇️ 아래로 이동", 
                  command=self.move_file_down).grid(row=0, column=3, padx=2, pady=2)
        ttk.Button(file_button_frame, text="🗑️ 전체 삭제", 
                  command=self.clear_all_files).grid(row=0, column=4, padx=2, pady=2)
        
        # 출력 파일 선택
        ttk.Label(parent, text="병합된 파일 저장 위치:").grid(row=2, column=0, sticky=W, pady=5)
        ttk.Entry(parent, textvariable=self.merge_output_path, width=50).grid(
            row=2, column=1, sticky=(W, E), padx=(10, 5), pady=5)
        ttk.Button(parent, text="찾아보기", 
                  command=self.browse_merge_output).grid(row=2, column=2, pady=5)
        
        # 자동 파일명 생성 체크박스
        ttk.Checkbutton(parent, text="자동으로 파일명 생성 (날짜/시간 포함)", 
                       variable=self.auto_merge_filename,
                       command=self.toggle_merge_auto_filename).grid(
            row=3, column=0, columnspan=3, sticky=W, pady=5)
        
        # 병합 버튼 (고정 위치)
        merge_button_frame = ttk.Frame(parent)
        merge_button_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=(W, E))
        
        self.merge_button = ttk.Button(merge_button_frame, text="🔗 파일 병합", 
                                      command=self.merge_files_func,
                                      style="Accent.TButton")
        self.merge_button.grid(row=0, column=0, pady=10)
        
        # 그리드 가중치 설정
        parent.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
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
                                    "PDF 도구를 종료하시겠습니까?"):
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
    
    def log_message(self, message):
        """결과 텍스트 영역에 메시지 추가"""
        if self.is_closing:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(END, f"[{timestamp}] {message}\n")
        self.result_text.see(END)
        self.root.update_idletasks()
    
    # 추출 관련 메서드들
    def toggle_auto_filename(self):
        """자동 파일명 생성 토글 (추출용)"""
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
    
    def toggle_merge_auto_filename(self):
        """자동 파일명 생성 토글 (병합용)"""
        if self.auto_merge_filename.get():
            self.merge_output_path.set("")
            # 병합 출력 파일 입력 필드 비활성화
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Entry) and child.cget('textvariable') == self.merge_output_path:
                            child.configure(state='disabled')
        else:
            # 병합 출력 파일 입력 필드 활성화
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Entry) and child.cget('textvariable') == self.merge_output_path:
                            child.configure(state='normal')
    
    def browse_input_file(self):
        """입력 파일 선택 다이얼로그"""
        filename = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_path.set(filename)
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
    
    def validate_extract_inputs(self):
        """추출 입력 값 유효성 검사"""
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
        if not self.validate_extract_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("경고", "이미 작업이 진행 중입니다.")
            return
        
        # UI 비활성화
        self.is_processing = True
        self.extract_button.configure(state='disabled')
        self.merge_button.configure(state='disabled')
        self.exit_button.configure(state='disabled')
        self.progress_bar.start()
        self.progress_var.set("추출 중...")
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
            self.log_message(f"✅ 추출 완료!")
            self.log_message(f"파일 크기: {file_size:,} bytes")
            self.log_message(f"저장 위치: {output_path}")
            
            # UI 업데이트
            self.root.after(0, self._extraction_complete)
            
        except Exception as e:
            self.log_message(f"❌ 추출 오류: {str(e)}")
            self.root.after(0, self._extraction_error)
    
    def _extraction_complete(self):
        """추출 완료 후 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("추출 완료!")
        self.extract_button.configure(state='normal')
        self.merge_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("추출 완료")
        messagebox.showinfo("완료", "페이지 추출이 완료되었습니다!")
    
    def _extraction_error(self):
        """추출 오류 시 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("추출 오류")
        self.extract_button.configure(state='normal')
        self.merge_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("추출 오류")
    
    # 병합 관련 메서드들
    def add_merge_files(self):
        """병합할 파일들 추가"""
        filenames = filedialog.askopenfilenames(
            title="병합할 PDF 파일들 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for filename in filenames:
            if filename not in self.merge_files:
                self.merge_files.append(filename)
                self.update_file_list()
                self.log_message(f"파일 추가: {os.path.basename(filename)}")
    
    def remove_selected_file(self):
        """선택된 파일 삭제"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            removed_file = self.merge_files.pop(index)
            self.update_file_list()
            self.log_message(f"파일 삭제: {os.path.basename(removed_file)}")
    
    def move_file_up(self):
        """선택된 파일을 위로 이동"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.merge_files[index], self.merge_files[index-1] = self.merge_files[index-1], self.merge_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index-1)
    
    def move_file_down(self):
        """선택된 파일을 아래로 이동"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.merge_files) - 1:
            index = selection[0]
            self.merge_files[index], self.merge_files[index+1] = self.merge_files[index+1], self.merge_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index+1)
    
    def clear_all_files(self):
        """모든 파일 삭제"""
        if self.merge_files:
            if messagebox.askokcancel("확인", "모든 파일을 삭제하시겠습니까?"):
                self.merge_files.clear()
                self.update_file_list()
                self.log_message("모든 파일 삭제됨")
    
    def update_file_list(self):
        """파일 목록 업데이트"""
        self.file_listbox.delete(0, END)
        for i, filepath in enumerate(self.merge_files, 1):
            filename = os.path.basename(filepath)
            self.file_listbox.insert(END, f"{i}. {filename}")
    
    def browse_merge_output(self):
        """병합 출력 파일 선택"""
        filename = filedialog.asksaveasfilename(
            title="병합된 파일 저장 위치 선택",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.merge_output_path.set(filename)
    
    def validate_merge_inputs(self):
        """병합 입력 값 유효성 검사"""
        if len(self.merge_files) < 2:
            messagebox.showerror("오류", "병합할 파일을 2개 이상 선택해주세요.")
            return False
        
        if not self.auto_merge_filename.get() and not self.merge_output_path.get():
            messagebox.showerror("오류", "저장 위치를 선택하거나 자동 파일명 생성을 활성화해주세요.")
            return False
        
        # 파일 존재 여부 확인
        for filepath in self.merge_files:
            if not os.path.exists(filepath):
                messagebox.showerror("오류", f"파일이 존재하지 않습니다: {os.path.basename(filepath)}")
                return False
        
        return True
    
    def merge_files_func(self):
        """파일 병합 실행"""
        if not self.validate_merge_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("경고", "이미 작업이 진행 중입니다.")
            return
        
        # UI 비활성화
        self.is_processing = True
        self.extract_button.configure(state='disabled')
        self.merge_button.configure(state='disabled')
        self.exit_button.configure(state='disabled')
        self.progress_bar.start()
        self.progress_var.set("병합 중...")
        self.update_status("파일 병합 중...")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._merge_files_thread)
        thread.daemon = True
        thread.start()
    
    def _merge_files_thread(self):
        """파일 병합 스레드"""
        try:
            # 출력 파일 경로 결정
            if self.auto_merge_filename.get():
                # 자동 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_count = len(self.merge_files)
                first_file = Path(self.merge_files[0])
                output_filename = f"merged_{file_count}files_{timestamp}.pdf"
                output_path = first_file.parent / output_filename
            else:
                output_path = self.merge_output_path.get()
            
            self.log_message(f"병합할 파일 수: {len(self.merge_files)}개")
            self.log_message(f"출력 파일: {output_path}")
            
            writer = PdfWriter()
            total_pages = 0
            
            for i, filepath in enumerate(self.merge_files, 1):
                self.log_message(f"처리 중 ({i}/{len(self.merge_files)}): {os.path.basename(filepath)}")
                
                try:
                    reader = PdfReader(filepath)
                    file_pages = len(reader.pages)
                    total_pages += file_pages
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    self.log_message(f"  → {file_pages}페이지 추가됨")
                    
                except Exception as e:
                    self.log_message(f"  ❌ 오류: {str(e)}")
                    raise e
            
            # 파일 저장
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # 결과 표시
            file_size = os.path.getsize(output_path)
            self.log_message(f"✅ 병합 완료!")
            self.log_message(f"총 페이지 수: {total_pages}페이지")
            self.log_message(f"파일 크기: {file_size:,} bytes")
            self.log_message(f"저장 위치: {output_path}")
            
            # UI 업데이트
            self.root.after(0, self._merge_complete)
            
        except Exception as e:
            self.log_message(f"❌ 병합 오류: {str(e)}")
            self.root.after(0, self._merge_error)
    
    def _merge_complete(self):
        """병합 완료 후 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("병합 완료!")
        self.extract_button.configure(state='normal')
        self.merge_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("병합 완료")
        messagebox.showinfo("완료", "파일 병합이 완료되었습니다!")
    
    def _merge_error(self):
        """병합 오류 시 UI 업데이트"""
        if self.is_closing:
            return
            
        self.progress_bar.stop()
        self.progress_var.set("병합 오류")
        self.extract_button.configure(state='normal')
        self.merge_button.configure(state='normal')
        self.exit_button.configure(state='normal')
        self.is_processing = False
        self.update_status("병합 오류")


def main():
    """메인 함수"""
    # 중복 실행 방지
    import fcntl
    lock_file = "/tmp/pdf_tool_gui.lock"
    
    try:
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, IOError):
        messagebox.showerror("오류", "PDF 도구가 이미 실행 중입니다.")
        sys.exit(1)
    
    root = tk.Tk()
    
    # 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')
    
    # 앱 실행
    app = PDFToolGUI(root)
    
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
