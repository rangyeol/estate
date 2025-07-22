# ⚡ 빠른 시작 - GitHub Actions 자동 빌드

**3단계로 Windows + macOS 앱 자동 생성하기**

---

## 📝 단계별 가이드

### 1️⃣ GitHub에 업로드

**웹에서 쉽게 (Git 설치 불필요)**

1. [GitHub.com](https://github.com) 로그인
2. **"New repository"** 클릭
3. 이름: `naver-real-estate-viewer`
4. **"Create repository"** 클릭
5. **"uploading an existing file"** 클릭
6. **모든 프로젝트 파일** 드래그 & 드롭
7. **"Commit changes"** 클릭

### 2️⃣ 자동 빌드 시작

업로드 완료 → **즉시 자동 빌드 시작!** 🚀

- **Actions** 탭에서 진행상황 확인
- 약 **10분** 후 완료

### 3️⃣ 결과 다운로드

**Actions** 탭 → 완료된 빌드 → **"Artifacts"**

- `naver-real-estate-viewer-windows.zip` ← Windows용
- `naver-real-estate-viewer-macos.zip` ← macOS용

---

## 🎯 결과물

### Windows
- `네이버부동산뷰어.exe` - 더블클릭으로 실행

### macOS  
- `네이버부동산뷰어.app` - 더블클릭으로 실행
- 보안 경고 시: **시스템 환경설정** → **보안** → **실행 허용**

---

## 💰 비용

**완전 무료!** 🆓
- GitHub Actions 월 2000분 무료 제공
- 1회 빌드 약 15-20분 소요

---

## 🔄 업데이트 방법

코드 수정 후 다시 GitHub에 업로드 → **자동으로 새 버전 빌드**

---

## 🆘 문제 해결

**빌드 실패 시**  
→ **Actions** 탭 → 빌드 클릭 → 로그 확인

**상세 가이드**  
→ [GITHUB_BUILD_GUIDE.md](GITHUB_BUILD_GUIDE.md)

---

**🎉 3단계로 크로스 플랫폼 앱 완성!** 