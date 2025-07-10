#!/usr/bin/env python3
"""
프로젝트 문서 PDF 변환 스크립트
"""

import os
import subprocess
from datetime import datetime

def convert_to_pdf():
    """문서를 PDF로 변환"""
    print("📄 PDF 변환 시작...")
    
    # 문서 실행 및 텍스트 파일로 저장
    os.system("python project_documentation.py > project_full_report.txt")
    os.system("python project_summary.py > project_executive_summary.txt")
    
    print("✅ 텍스트 파일 생성 완료")
    print("💡 PDF 변환을 위해 다음 도구를 사용하세요:")
    print("   • pandoc project_full_report.txt -o project_full_report.pdf")
    print("   • pandoc project_executive_summary.txt -o project_executive_summary.pdf")
    print("   • 또는 온라인 텍스트→PDF 변환 도구 활용")
    
    print(f"\n📋 생성된 파일:")
    print(f"   • project_full_report.txt (완전판)")
    print(f"   • project_executive_summary.txt (요약판)")
    print(f"   • 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    convert_to_pdf()
