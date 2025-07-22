from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtGui import QMovie, QColor, QPalette
from PySide6.QtCore import Qt, QSize

class LoadingDialog(QDialog):
    def __init__(self, parent=None, gif_path="spinner.gif"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground) # 배경 투명하게 하여 GIF만 보이도록
        self.setStyleSheet("background-color: rgba(0,0,0,0);") # 완전 투명

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0) # 여백 최소화

        self.movie_label = QLabel(self)
        self.movie_label.setAlignment(Qt.AlignCenter)
        
        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            # GIF 크기에 맞춰 레이블 크기 조정 또는 고정 크기 사용
            scaled_size = QSize(64, 64) # 원하는 GIF 크기
            self.movie.setScaledSize(scaled_size)
            self.movie_label.setMovie(self.movie)
            self.movie.start()
            self.setFixedSize(scaled_size.width() + 40, scaled_size.height() + 40) # GIF 주변 여백 고려
        else:
            print(f"로딩 GIF 파일을 찾을 수 없거나 유효하지 않습니다: {gif_path}")
            self.movie_label.setText("로딩 중...") # GIF 없을 경우 대체 텍스트
            self.movie_label.setStyleSheet("color: black; background-color: white; padding: 10px; border-radius: 5px;")
            self.setFixedSize(150, 80)

        layout.addWidget(self.movie_label)

        # 메시지 레이블 (선택 사항)
        # self.message_label = QLabel("데이터를 수집하고 있습니다...")
        # self.message_label.setAlignment(Qt.AlignCenter)
        # self.message_label.setStyleSheet("color: black; font-weight: bold; background-color: rgba(220, 220, 220, 200); padding: 8px; border-radius: 5px; margin-top: 5px;")
        # layout.addWidget(self.message_label)
        
    def setText(self, text): # 외부에서 메시지 설정 (현재는 사용 안함)
        # if hasattr(self, 'message_label'):
        # self.message_label.setText(text)
        pass

    def closeEvent(self, event):
        self.movie.stop()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        if self.movie.isValid() and not self.movie.state() == QMovie.MovieState.Running:
            self.movie.start()
        # 부모 창 중앙에 표시
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(parent_rect.center() - self.rect().center())