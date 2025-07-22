# main.py (이전 답변과 거의 동일, get_app_data_path 경로 결정 로직 약간 보강)
import sys
import json
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QStandardPaths, QCoreApplication

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from main_window import MainWindow

def get_app_data_path(filename=""):
    # QApplication 인스턴스 생성 후, QCoreApplication 이름들이 설정된 후 호출되어야 함
    org_name = QCoreApplication.organizationName()
    app_name = QCoreApplication.applicationName()

    if not org_name or not app_name:
        # print("경고: OrganizationName 또는 ApplicationName이 설정되지 않았습니다. 임시 경로를 사용합니다.")
        # 안전한 폴백 경로 (예: 사용자 홈 디렉토리)
        base_dir = os.path.join(os.path.expanduser("~"), ".MyNaverRealEstateApp_TempCache")
    else:
        # 표준 경로 사용
        app_data_dir_std = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not app_data_dir_std : # 표준 경로를 얻지 못한 경우 (드문 경우)
             app_data_dir_std = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
        
        if app_data_dir_std: # 표준 경로를 얻었다면 사용
            # AppDataLocation은 이미 org/app 이름을 포함하는 경우가 많음. OS별 동작 확인 필요.
            # 명시적으로 만들려면: base_dir = os.path.join(app_data_dir_std, org_name, app_name)
            base_dir = app_data_dir_std # 대부분의 경우 이 경로가 org/app 포함
        else: # 표준 경로를 얻지 못했다면 사용자 홈에 생성
            base_dir = os.path.join(os.path.expanduser("~"), f".{org_name}", app_name)


    if not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir, exist_ok=True)
            # print(f"앱 데이터 폴더 생성: {base_dir}")
        except OSError as e_os:
            print(f"앱 데이터 디렉토리 생성 실패 {base_dir}: {e_os}")
            base_dir = os.path.dirname(os.path.abspath(__file__)) # 생성 실패 시 스크립트 디렉토리
            print(f"폴백 경로 사용 (스크립트 디렉토리): {base_dir}")

    return os.path.join(base_dir, filename) if filename else base_dir


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("MyRealEstateOrg") # 원하는 조직명으로 변경
    QCoreApplication.setApplicationName("Naver 부동산 뷰어") # 원하는 앱 이름으로 변경
    
    print(f"애플리케이션 데이터 기본 경로: {get_app_data_path()}")

    try:
        window = MainWindow(None)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"프로그램 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "프로그램 실행 오류", f"프로그램 실행 중 심각한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)