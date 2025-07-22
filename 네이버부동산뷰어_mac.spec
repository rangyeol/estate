# -*- mode: python ; coding: utf-8 -*-
# macOS용 네이버 부동산 뷰어 빌드 설정

import os
from PyInstaller.utils.hooks import collect_data_files

# 데이터 파일 추가
added_files = [
    ('연수동_complexes.json', '.'),
    ('spinner.gif', '.')
]

# PySide6 관련 데이터 파일 수집
pyside6_datas = collect_data_files('PySide6')
added_files.extend(pyside6_datas)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'requests',
        'pandas',
        'openpyxl',
        'urllib3',
        'certifi'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'tkinter'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# macOS용 실행 파일 설정
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='네이버부동산뷰어',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # 현재 아키텍처 사용 (Intel 또는 Apple Silicon)
    codesign_identity=None,  # 코드사인 ID (선택사항)
    entitlements_file=None,  # 권한 파일 (선택사항)
    icon=None,  # 아이콘 파일 (.icns)
)

# macOS 앱 번들 생성
app = BUNDLE(
    exe,
    a.binaries,
    a.datas,
    name='네이버부동산뷰어.app',
    icon=None,  # 앱 아이콘 (.icns 파일)
    bundle_identifier='com.naverrealestate.viewer',  # 번들 식별자
    info_plist={
        'CFBundleName': '네이버부동산뷰어',
        'CFBundleDisplayName': '네이버 부동산 뷰어',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.naverrealestate.viewer',
        'NSHighResolutionCapable': True,  # Retina 디스플레이 지원
        'LSMinimumSystemVersion': '11.0',  # macOS 11.0 이상
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True  # HTTP 요청 허용
        },
        'NSRequiresAquaSystemAppearance': False,  # 다크모드 지원
    }
) 