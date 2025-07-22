# 🏠 네이버 부동산 뷰어

**PySide6 기반 네이버 부동산 데이터 조회 및 분석 도구**

[![Build Status](../../actions/workflows/build.yml/badge.svg)](../../actions/workflows/build.yml)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## ✨ 주요 기능

- 🔍 **지역별 부동산 검색** - 시/구/동 단위 검색 지원
- 📊 **상세 정보 조회** - 가격, 면적, 층수 등 상세 데이터
- 📈 **데이터 분석** - 가격 추이 및 통계 정보
- 💾 **엑셀 내보내기** - 검색 결과를 엑셀 파일로 저장
- 🎨 **직관적인 UI** - 사용하기 쉬운 그래픽 인터페이스

---

## 🚀 빠른 시작

### 📥 다운로드 (빌드된 버전)

**GitHub Actions에서 자동 빌드된 최신 버전:**

1. [**Releases**](../../releases) 페이지 방문
2. 운영체제에 맞는 파일 다운로드:
   - **Windows**: `네이버부동산뷰어-windows.zip`
   - **macOS**: `네이버부동산뷰어-macos.zip`
3. 압축 해제 후 실행

### 🔨 직접 빌드

#### Windows
```bash
pip install -r requirements.txt
pyinstaller 네이버부동산뷰어.spec --clean
```

#### macOS
```bash
chmod +x build_mac.sh
./build_mac.sh
```

---

## 🤖 자동 빌드 시스템

### GitHub Actions 무료 클라우드 빌드

이 프로젝트는 **GitHub Actions**를 사용하여 다음을 자동화합니다:

- ✅ **Windows** `.exe` 파일 생성
- ✅ **macOS** `.app` 번들 생성  
- ✅ **크로스 플랫폼** 동시 빌드
- ✅ **무료** 클라우드 빌드 (월 2000분)

### 자동 빌드 사용법

1. **코드 푸시** → 자동 빌드 시작
2. **Actions 탭** → 진행상황 확인
3. **Artifacts** → 빌드 결과 다운로드

**상세 가이드**: [GITHUB_BUILD_GUIDE.md](GITHUB_BUILD_GUIDE.md)

---

## 📋 시스템 요구사항

### Windows
- **OS**: Windows 10/11
- **Python**: 3.8+ (개발 시에만)
- **RAM**: 최소 4GB

### macOS  
- **OS**: macOS 11.0+ (Big Sur)
- **Python**: 3.8+ (개발 시에만)
- **아키텍처**: Intel x64 또는 Apple Silicon (M1/M2/M3)

---

## 🛠️ 개발 환경 설정

### 1. 저장소 클론
```bash
git clone https://github.com/USERNAME/naver-real-estate-viewer.git
cd naver-real-estate-viewer
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
python main.py
```

---

## 📁 프로젝트 구조

```
📦 naver-real-estate-viewer/
├── 🐍 main.py                    # 애플리케이션 진입점
├── 🖼️ main_window.py             # 메인 창 UI
├── 📊 property_table.py          # 부동산 목록 테이블
├── 📋 property_detail.py         # 상세 정보 위젯
├── 🌐 naver_api.py               # 네이버 API 연동
├── ⏳ loading_dialog.py          # 로딩 대화상자
├── 📄 requirements.txt           # Python 의존성
├── 🔧 네이버부동산뷰어.spec      # Windows 빌드 설정
├── 🍎 네이버부동산뷰어_mac.spec  # macOS 빌드 설정
├── 🚀 build_mac.sh              # macOS 빌드 스크립트
├── 📚 연수동_complexes.json     # 샘플 데이터
├── 🌀 spinner.gif               # 로딩 애니메이션
└── 📖 docs/                     # 문서 폴더
    ├── MAC_BUILD_GUIDE.md       # macOS 빌드 가이드
    ├── GITHUB_BUILD_GUIDE.md    # GitHub Actions 가이드
    └── CHANGELOG_MAC.md         # 변경사항 기록
```

---

## 🔧 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| **PySide6** | 6.5.0+ | GUI 프레임워크 |
| **requests** | 2.31.0+ | HTTP 요청 |
| **pandas** | 2.0.0+ | 데이터 처리 |
| **openpyxl** | 3.1.0+ | 엑셀 파일 처리 |

---

## 📸 스크린샷

### 메인 화면
- 지역 선택 인터페이스
- 부동산 목록 테이블
- 상세 정보 패널

### 주요 기능
- 실시간 데이터 조회
- 엑셀 내보내기
- 가격 분석

---

## 🤝 기여하기

1. **Fork** 프로젝트
2. **Feature 브랜치** 생성 (`git checkout -b feature/amazing-feature`)
3. **커밋** (`git commit -m 'Add amazing feature'`)
4. **푸시** (`git push origin feature/amazing-feature`)
5. **Pull Request** 생성

---

## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다.  
자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 지원 및 문의

### 문제 신고
- [**Issues**](../../issues) 탭에서 버그 신고
- 상세한 오류 메시지와 환경 정보 포함

### 기능 요청
- [**Discussions**](../../discussions) 탭에서 제안
- 사용 사례와 기대 효과 설명

### 빌드 문제
- **Windows**: [네이버부동산뷰어.spec](네이버부동산뷰어.spec) 확인
- **macOS**: [MAC_BUILD_GUIDE.md](MAC_BUILD_GUIDE.md) 참조
- **GitHub Actions**: [GITHUB_BUILD_GUIDE.md](GITHUB_BUILD_GUIDE.md) 참조

---

## 🎉 감사합니다!

**⭐ 도움이 되셨다면 Star를 눌러주세요!**

[![GitHub stars](https://img.shields.io/github/stars/USERNAME/REPOSITORY.svg?style=social)](../../stargazers) 