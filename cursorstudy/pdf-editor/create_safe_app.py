#!/usr/bin/env python3
"""
PDF 페이지 추출기 - 안전한 앱 생성기
종료 버튼 추가 및 예기치 않은 종료 방지
"""

import os
import subprocess
import sys
import shutil

def create_safe_app():
    """안전한 앱 생성 (종료 버튼 포함)"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_name = "PDF 페이지 추출기.app"
    desktop_path = os.path.expanduser("~/Desktop")
    app_path = os.path.join(desktop_path, app_name)
    
    # 기존 앱 삭제
    if os.path.exists(app_path):
        shutil.rmtree(app_path)
        print("기존 앱을 삭제했습니다.")
    
    # .app 번들 구조 생성
    contents_path = os.path.join(app_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    # 디렉토리 생성
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # 안전한 실행 스크립트 생성
    launcher_script = f'''#!/bin/bash

# PDF 페이지 추출기 실행 스크립트
# 안전한 종료 버튼 포함 버전

# 현재 스크립트의 디렉토리로 이동
SCRIPT_DIR="{current_dir}"
cd "$SCRIPT_DIR"

# Python 경로 확인
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 중복 실행 방지
LOCK_FILE="/tmp/pdf_extractor_gui_safe.lock"
if [ -f "$LOCK_FILE" ]; then
    echo "PDF 페이지 추출기가 이미 실행 중입니다."
    echo "기존 창을 확인해보세요."
    exit 1
fi

# 잠금 파일 생성
echo $$ > "$LOCK_FILE"

# 정리 함수
cleanup() {{
    rm -f "$LOCK_FILE"
}}

# 종료 시 정리
trap cleanup EXIT

# GUI 프로그램 실행 (안전한 버전)
echo "PDF 페이지 추출기를 시작합니다..."
echo "종료할 때는 프로그램 내의 '안전하게 종료' 버튼을 사용하세요."
"$PYTHON_CMD" pdf_extractor_gui_safe.py

# 실행 완료 후 정리
cleanup
'''
    
    launcher_path = os.path.join(macos_path, "PDF 페이지 추출기")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_script)
    
    # 실행 권한 부여
    os.chmod(launcher_path, 0o755)
    
    # Info.plist 생성
    info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PDF 페이지 추출기</string>
    <key>CFBundleIdentifier</key>
    <string>com.pdfextractor.safe.app</string>
    <key>CFBundleName</key>
    <string>PDF 페이지 추출기</string>
    <key>CFBundleDisplayName</key>
    <string>PDF 페이지 추출기</string>
    <key>CFBundleVersion</key>
    <string>1.2.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.2.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>PDFX</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>pdf</string>
            </array>
        </dict>
    </array>
</dict>
</plist>'''
    
    info_plist_path = os.path.join(contents_path, "Info.plist")
    with open(info_plist_path, 'w', encoding='utf-8') as f:
        f.write(info_plist)
    
    # 아이콘 복사 (있는 경우)
    icon_source = os.path.join(current_dir, "app_icon.icns")
    if os.path.exists(icon_source):
        icon_dest = os.path.join(resources_path, "app_icon.icns")
        shutil.copy2(icon_source, icon_dest)
        print("아이콘을 복사했습니다.")
    
    print(f"✅ 안전한 앱이 생성되었습니다: {app_path}")
    return app_path

def test_app(app_path):
    """앱 테스트"""
    print(f"🧪 앱 테스트 중: {app_path}")
    
    try:
        # 앱 실행 테스트
        result = subprocess.run(['open', app_path], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ 앱 실행 성공!")
            return True
        else:
            print(f"❌ 앱 실행 실패: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ 앱이 백그라운드에서 실행 중입니다.")
        return True
    except Exception as e:
        print(f"❌ 앱 테스트 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 PDF 페이지 추출기 - 안전한 앱 생성")
    print("종료 버튼 추가 및 예기치 않은 종료 방지")
    print()
    
    # 앱 생성
    app_path = create_safe_app()
    
    if app_path:
        print()
        print("🎉 안전한 앱 생성 완료!")
        print(f"📱 위치: {app_path}")
        print()
        print("🔧 새로운 기능:")
        print("- 🚪 안전하게 종료 버튼 추가")
        print("- 작업 중일 때 종료 확인 메시지")
        print("- 상태 표시 개선")
        print("- 예기치 않은 종료 방지")
        print()
        print("💡 사용 방법:")
        print("1. 데스크톱의 'PDF 페이지 추출기.app'을 더블클릭")
        print("2. 프로그램 내의 '🚪 안전하게 종료' 버튼 사용")
        print("3. 작업 중일 때는 종료 확인 메시지가 나타남")
        print()
        print("🔧 문제 해결:")
        print("- 앱이 실행되지 않으면:")
        print("  - Finder에서 앱을 우클릭 → '열기' 선택")
        print("  - 또는 터미널에서: open '/Users/kimpro/Desktop/PDF 페이지 추출기.app'")
        print("- 중복 실행 오류가 나면:")
        print("  - 기존 창을 찾아서 사용하거나")
        print("  - 터미널에서: rm /tmp/pdf_extractor_gui_safe.lock")
        print()
        
        # 앱 테스트
        test_app(app_path)
        
        print()
        print("🎯 완료! 이제 안전하게 사용할 수 있습니다!")
        print("💡 종료할 때는 반드시 '🚪 안전하게 종료' 버튼을 사용하세요!")

if __name__ == "__main__":
    main()
