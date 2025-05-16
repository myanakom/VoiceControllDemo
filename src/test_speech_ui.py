"""
音声認識とUIの統合テスト
"""
import sys
import os
import logging
from pathlib import Path

# プロジェクトルートへのパスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.ui_controller import UIController
from src.speech.speech_recognizer import SpeechRecognizer

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def manual_test():
    """音声認識とUIの手動テスト"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("音声認識とUIの統合テストを開始します...")
    
    # UIコントローラーの初期化
    ui_controller = UIController()
    
    # 音声認識の初期化
    recognizer = SpeechRecognizer()
    
    # 音声認識結果のハンドラ
    def handle_speech_result(text: str):
        print(f"\n認識されたテキスト: {text}")
        # UIの状態を更新
        if "計測開始" in text or "測定開始" in text:
            ui_controller.set_recording_state(True)
            ui_controller.update_system_status("計測中")
        elif "計測終了" in text or "測定終了" in text:
            ui_controller.set_recording_state(False)
            ui_controller.update_system_status("計測完了")
        elif "機種" in text:
            ui_controller.update_measurement_info({
                "機種": "K57",
                "試験名": "未選択",
                "試験条件": "未設定",
                "計測者": "未設定"
            })
    
    def show_menu():
        print("\n利用可能なコマンド:")
        print("1: 音声認識開始")
        print("2: 音声認識停止")
        print("q: 終了")
    
    def handle_command(cmd):
        if cmd == "1":
            recognizer.start_recognition(handle_speech_result)
            print("音声認識を開始しました。以下のコマンドを話しかけてください：")
            print("- 「計測開始」または「測定開始」")
            print("- 「計測終了」または「測定終了」")
            print("- 「機種選択」")
        
        elif cmd == "2":
            recognizer.stop_recognition()
            print("音声認識を停止しました。")
    
    # メインループ
    while True:
        show_menu()
        cmd = input("\nコマンドを入力してください: ")
        
        if cmd.lower() == "q":
            if recognizer.is_listening:
                recognizer.stop_recognition()
            ui_controller.stop()
            break
        
        handle_command(cmd)

if __name__ == "__main__":
    manual_test() 