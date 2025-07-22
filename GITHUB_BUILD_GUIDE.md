# 🚀 GitHub Actions 자동 빌드 가이드

GitHub에서 **무료로** Windows와 macOS 버전을 자동으로 빌드하는 방법입니다!

---

## 📋 준비사항

1. **GitHub 계정** (무료)
2. **Git 설치** (선택사항, 웹에서도 가능)

---

## 🎯 1단계: GitHub 저장소 생성

### 방법 1: 웹에서 생성 (쉬움)
1. [GitHub.com](https://github.com) 로그인
2. **"New repository"** 클릭
3. 저장소 이름: `naver-real-estate-viewer` (원하는 이름)
4. **Public** 또는 **Private** 선택
5. **"Create repository"** 클릭

### 방법 2: Git으로 생성
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

---

## 📤 2단계: 파일 업로드

### 방법 1: 웹에서 업로드 (쉬움)
1. GitHub 저장소 페이지로 이동
2. **"uploading an existing file"** 클릭
3. 모든 프로젝트 파일을 드래그 & 드롭
4. **"Commit changes"** 클릭

### 방법 2: Git으로 업로드
```bash
git add .
git commit -m "Add Naver Real Estate Viewer"
git push origin main
```

---

## ⚡ 3단계: 자동 빌드 확인

업로드 후 **자동으로 빌드가 시작**됩니다!

### 빌드 진행상황 확인
1. GitHub 저장소의 **"Actions"** 탭 클릭
2. **"Build Naver Real Estate Viewer"** 워크플로우 확인
3. 빌드 진행상황 실시간 확인 가능

### 빌드 시간
- **Windows**: 약 5-8분
- **macOS**: 약 6-10분
- **동시 진행**: 총 10분 내외

---

## 📦 4단계: 빌드 결과 다운로드

### Artifacts 다운로드 (항상 가능)
1. **Actions** 탭 → 완료된 빌드 클릭
2. 하단 **"Artifacts"** 섹션에서 다운로드:
   - `naver-real-estate-viewer-windows.zip` (Windows용)
   - `naver-real-estate-viewer-macos.zip` (macOS용)

### Release 다운로드 (태그 생성 시)
1. **"Releases"** 탭에서 다운로드
2. 더 공식적인 배포 방식

---

## 🎮 5단계: 실행 방법

### Windows
1. `네이버부동산뷰어-windows.zip` 압축 해제
2. `네이버부동산뷰어.exe` 실행

### macOS
1. `네이버부동산뷰어-macos.zip` 압축 해제
2. `네이버부동산뷰어.app` 더블클릭
3. 보안 경고 시: `시스템 환경설정` → `보안` → `실행 허용`

---

## 🔄 자동 빌드 트리거

다음 상황에서 **자동으로 빌드**됩니다:

### 1. 코드 푸시 시
```bash
git push origin main
```
→ 즉시 빌드 시작

### 2. 수동 실행
1. **Actions** 탭
2. **"Build Naver Real Estate Viewer"** 선택
3. **"Run workflow"** 클릭

### 3. Release 생성 시
1. **Releases** 탭
2. **"Create a new release"** 
3. 태그 생성 → 자동 빌드 + 업로드

---

## 📊 빌드 상태 확인

### 성공 시 ✅
- 초록색 체크마크
- Artifacts에서 다운로드 가능

### 실패 시 ❌
- 빨간색 X 마크
- 로그에서 오류 확인 가능

---

## 🔧 고급 사용법

### Release 자동 배포
```bash
# 태그 생성 후 푸시
git tag v1.0.0
git push origin v1.0.0
```
→ 자동으로 Release 생성 + 파일 업로드

### 브랜치별 빌드
- `main` 또는 `master` 브랜치에서만 빌드
- 다른 브랜치도 설정 가능

---

## 💰 비용

GitHub Actions는 **무료**입니다!

### 무료 한도 (월간)
- **Public 저장소**: 무제한
- **Private 저장소**: 2,000분

### 예상 사용량
- 1회 빌드: 약 15-20분
- 월 100회 빌드 가능 (Private 저장소 기준)

---

## 🛠️ 커스터마이징

### 빌드 설정 변경
`.github/workflows/build.yml` 파일 수정:

```yaml
# Python 버전 변경
python-version: '3.11'  # → '3.12'

# 빌드 트리거 변경
on:
  push:
    branches: [ main, develop ]  # develop 브랜치 추가
```

### 추가 플랫폼 지원
- Linux 빌드 추가 가능
- ARM 아키텍처 지원 가능

---

## 🆘 문제 해결

### 빌드 실패 시
1. **Actions** 탭 → 실패한 빌드 클릭
2. 로그에서 오류 메시지 확인
3. 의존성 문제가 대부분

### 권한 오류 시
- 저장소 설정에서 Actions 활성화 확인
- `GITHUB_TOKEN` 권한 확인

### 파일 업로드 오류 시
- 파일 크기 100MB 미만 확인
- Git LFS 사용 고려 (큰 파일)

---

## 🎉 완료!

이제 **코드만 푸시하면** 자동으로:
- ✅ Windows `.exe` 생성
- ✅ macOS `.app` 생성
- ✅ 다운로드 링크 제공
- ✅ 무료로 사용 가능

---

## 📞 추가 도움

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [PyInstaller 문서](https://pyinstaller.readthedocs.io/)
- GitHub Issues에서 문의 가능 