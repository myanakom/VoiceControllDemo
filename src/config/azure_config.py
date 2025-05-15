"""
Azure Speech Serviceの設定を管理するモジュール
"""
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

class AzureConfig:
    """Azure設定を管理するクラス"""
    
    def __init__(self):
        """Azure設定の初期化"""
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')
        self.speech_language = os.getenv('SPEECH_LANGUAGE', 'ja-JP')
        self.voice_name = os.getenv('VOICE_NAME', 'ja-JP-NanamiNeural')
        self.recognition_timeout = int(os.getenv('SPEECH_RECOGNITION_TIMEOUT', '5'))
        
        # 設定値の検証
        if not self.speech_key or not self.speech_region:
            raise ValueError("Azure Speech Service の設定が不完全です。.envファイルを確認してください。")
    
    @property
    def speech_config_dict(self):
        """Speech SDKの設定を辞書形式で返す"""
        return {
            'subscription': self.speech_key,
            'region': self.speech_region,
            'speech_recognition_language': self.speech_language,
            'speech_synthesis_voice_name': self.voice_name
        }
    
    @property
    def timeout_seconds(self):
        """音声認識のタイムアウト時間（秒）を返す"""
        return self.recognition_timeout 