# -*- mode: python ; coding: utf-8 -*-
# macOS용 네이버 부동산 뷰어 빌드 설정 (Qt3D 충돌 완전 회피 - Onefile 모드)

import os
from PyInstaller.utils.hooks import collect_data_files

# 데이터 파일 추가
added_files = [
    ('연수동_complexes.json', '.'),
    ('spinner.gif', '.')
]

# PySide6 관련 데이터 파일 수집 (Qt3D 완전 제외)
try:
    pyside6_datas = collect_data_files('PySide6')
    # Qt3D 관련 파일들을 데이터에서도 제외
    filtered_datas = []
    for data in pyside6_datas:
        if not any(qt3d in str(data[0]).lower() for qt3d in ['qt3d', '3danimation', '3dcore', '3dextras', '3dlogic', '3drender']):
            filtered_datas.append(data)
    added_files.extend(filtered_datas)
except Exception as e:
    print(f"PySide6 데이터 수집 중 오류 (Qt3D 제외): {e}")

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
    hooksconfig={
        # PySide6 훅 설정에서도 Qt3D 제외
        'pyside6': {
            'exclude_qml_plugins': ['Qt3D*', '*3D*'],
            'exclude_frameworks': ['Qt3D*']
        }
    },
    runtime_hooks=[],
    # ===== Qt3D 충돌 완전 회피: 모든 Qt3D 관련 모듈/프레임워크 완전 제외 =====
    excludes=[
        'PyQt5', 'PyQt6', 'tkinter',
        # Qt3D 관련 모든 모듈 제외 (충돌 완전 방지)
        'Qt3DAnimation', 'Qt3DCore', 'Qt3DExtras', 'Qt3DInput', 
        'Qt3DLogic', 'Qt3DRender', 'Qt3DQuick', 'Qt3DQuickAnimation',
        'Qt3DQuickExtras', 'Qt3DQuickInput', 'Qt3DQuickRender',
        'Qt3DQuickScene2D', 'Qt3DQuickScene3D',
        # PySide6 Qt3D 모듈들
        'PySide6.Qt3DAnimation', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput', 'PySide6.Qt3DLogic', 'PySide6.Qt3DRender',
        'PySide6.Qt3DQuick', 'PySide6.Qt3DQuickAnimation',
        'PySide6.Qt3DQuickExtras', 'PySide6.Qt3DQuickInput',
        'PySide6.Qt3DQuickRender', 'PySide6.Qt3DQuickScene2D',
        # 추가 제외 (안전장치)
        'Qt3D', 'qt3d', 'QT3D', 'Qt3d', 'qT3D',
        # 프레임워크 레벨 제외
        'Qt3DAnimation.framework', 'Qt3DCore.framework',
        'Qt3DExtras.framework', 'Qt3DInput.framework',
        'Qt3DLogic.framework', 'Qt3DRender.framework',
        # QML 플러그인 제외
        'lib3dquicklogicplugin', 'libqtquickscene3dplugin'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# ===== Onefile 모드: Qt3D 프레임워크 충돌 완전 회피 =====
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # onefile 모드를 위해 binaries 포함
    a.datas,     # onefile 모드를 위해 datas 포함
    [],
    name='네이버부동산뷰어',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # 현재 아키텍처 사용 (Intel 또는 Apple Silicon)
    codesign_identity=None,  # 코드사인 ID (선택사항)
    entitlements_file=None,  # 권한 파일 (선택사항)
    icon=None,  # 아이콘 파일 (.icns)
)

# ===== 주의: Onefile 모드에서는 BUNDLE 대신 단일 실행파일 생성 =====
# Qt3D 프레임워크 구조 문제를 완전히 회피하기 위해 onefile 모드 사용
# 필요시 app 번들 생성을 원한다면 아래 주석을 해제하세요:

# app = BUNDLE(
#     exe,
#     name='네이버부동산뷰어.app',
#     icon=None,
#     bundle_identifier='com.naverrealestate.viewer',
#     info_plist={
#         'CFBundleName': '네이버부동산뷰어',
#         'CFBundleDisplayName': '네이버 부동산 뷰어',
#         'CFBundleVersion': '1.0.0',
#         'CFBundleShortVersionString': '1.0.0',
#         'CFBundleIdentifier': 'com.naverrealestate.viewer',
#         'NSHighResolutionCapable': True,
#         'LSMinimumSystemVersion': '11.0',
#         'NSAppTransportSecurity': {
#             'NSAllowsArbitraryLoads': True
#         },
#         'NSRequiresAquaSystemAppearance': False,
#     }
# ) 