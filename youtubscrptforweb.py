import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QLineEdit, QPushButton, QLabel, QFileDialog, QTextEdit
)
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
)

class YouTubeSubtitleDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # 다크 테마 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #363636;
            }
            QPushButton {
                background-color: #0d47a1;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QTextEdit {
                background-color: #363636;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # URL 입력 필드
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube URL을 입력하세요...")
        layout.addWidget(self.url_input)
        
        # 다운로드 버튼
        self.download_btn = QPushButton("자막 다운로드")
        self.download_btn.clicked.connect(self.download_subtitles)
        layout.addWidget(self.download_btn)
        
        # 자막 표시 영역 추가
        self.subtitle_display = QTextEdit()
        self.subtitle_display.setReadOnly(True)
        self.subtitle_display.setPlaceholderText("자막이 여기에 표시됩니다...")
        self.subtitle_display.setMinimumHeight(200)
        layout.addWidget(self.subtitle_display)
        
        self.status_label = QLabel("상태: 준비 완료")
        layout.addWidget(self.status_label)
        
        # 창 설정
        self.setLayout(layout)
        self.setWindowTitle("유튜브 자막 추출기")
        self.resize(500, 400)
        self.show()
    
    def extract_video_id(self, url):
        """URL에서 YouTube 동영상 ID 추출"""
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
        match = re.search(regex, url)
        return match.group(1) if match else None
    
    def download_subtitles(self):
        """자막 다운로드 및 저장 핸들러"""
        url = self.url_input.text()
        video_id = self.extract_video_id(url)
        
        if not video_id:
            self.status_label.setText("상태: 유효하지 않은 YouTube URL입니다!")
            return
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['ko', 'en']
            )
            text = '\n'.join([entry['text'] for entry in transcript])
            
            # 자막을 화면에 표시
            self.subtitle_display.setText(text)
            
        except (TranscriptsDisabled, NoTranscriptFound):
            self.status_label.setText("상태: 사용 가능한 자막이 없습니다!")
            return
        except VideoUnavailable:
            self.status_label.setText("상태: 동영상을 찾을 수 없습니다!")
            return
        except Exception as e:
            self.status_label.setText(f"상태: 오류 발생 - {str(e)}")
            return
        
        # 파일 저장 다이얼로그
        file_name, _ = QFileDialog.getSaveFileName(
            self, "파일 저장", "youtube_subtitles.txt", "텍스트 파일 (*.txt)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_label.setText(f"상태: 성공! {file_name}에 저장되었습니다.")
            except Exception as e:
                self.status_label.setText(f"상태: 파일 저장 실패 - {str(e)}")
        else:
            self.status_label.setText("상태: 파일 저장이 취소되었습니다.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeSubtitleDownloader()
    sys.exit(app.exec_())