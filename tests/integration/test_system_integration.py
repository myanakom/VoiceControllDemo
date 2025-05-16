"""
システム統合テスト
"""
import sys
import os
import unittest
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

# プロジェクトルートへのパスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.ui_controller import UIController
from src.speech.speech_recognizer import SpeechRecognizer

class TestSystemIntegration(unittest.TestCase):
    """システム統合テストクラス"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラスの初期化"""
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)
    
    def setUp(self):
        """各テストケースの前処理"""
        self.ui_controller = UIController()
        self.speech_recognizer = SpeechRecognizer()
    
    def tearDown(self):
        """各テストケースの後処理"""
        if hasattr(self, 'ui_controller'):
            self.ui_controller.stop()
    
    def test_ui_speech_integration(self):
        """UIと音声認識の統合テスト"""
        # 音声認識結果のモック
        mock_result = "計測開始"
        
        # コールバック関数の定義
        def speech_callback(text):
            self.assertEqual(text, mock_result)
            self.ui_controller.update_system_status("計測中")
        
        # 音声認識開始
        with patch.object(self.speech_recognizer, '_handle_result') as mock_handler:
            self.speech_recognizer.start_recognition(speech_callback)
            # モックイベントの発火
            mock_event = MagicMock()
            mock_event.result.text = mock_result
            mock_event.result.reason = "RecognizedSpeech"
            self.speech_recognizer._handle_result(mock_event)
    
    def test_measurement_flow(self):
        """計測フロー全体のテスト"""
        # 計測情報の更新
        test_info = {
            "機種": "K57",
            "試験名": "牽引力試験",
            "試験条件": "前進速度3km/h",
            "計測者": "テスト太郎"
        }
        self.ui_controller.update_measurement_info(test_info)
        
        # 録音状態の変更
        self.ui_controller.set_recording_state(True)
        self.ui_controller.update_system_status("計測中")
        
        # 録音停止
        self.ui_controller.set_recording_state(False)
        self.ui_controller.update_system_status("計測完了")
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効な計測情報
        with self.assertRaises(ValueError):
            self.ui_controller.update_measurement_info({
                "invalid_key": "invalid_value"
            })
        
        # 録音停止時の録音停止操作
        self.ui_controller.set_recording_state(False)
        self.ui_controller.set_recording_state(False)  # 2回目の停止操作

if __name__ == '__main__':
    unittest.main() 