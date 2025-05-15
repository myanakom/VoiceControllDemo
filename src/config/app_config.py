"""
アプリケーション全体の設定を管理するモジュール
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

class AppConfig:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self):
        """アプリケーション設定の初期化"""
        # ベースディレクトリの設定
        self.base_dir = Path(__file__).parent.parent.parent
        
        # データディレクトリの設定
        self.data_dir = Path(os.getenv('DATA_DIR', 'src/data'))
        self.recordings_dir = Path(os.getenv('VOICE_RECORDING_DIR', 'data/recordings'))
        
        # ログレベルの設定
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.debug_mode = os.getenv('APP_DEBUG', 'False').lower() == 'true'
        
        # 設定の初期化
        self._initialize_logging()
        self._ensure_directories()
    
    def _initialize_logging(self):
        """ロギングの初期化"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _ensure_directories(self):
        """必要なディレクトリの作成"""
        for directory in [self.data_dir, self.recordings_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def csv_files(self):
        """CSVファイルのパスを辞書形式で返す"""
        return {
            'vehicles': self.data_dir / 'vehicles.csv',
            'tests': self.data_dir / 'tests.csv',
            'conditions': self.data_dir / 'conditions.csv',
            'users': self.data_dir / 'users.csv'
        }
    
    def get_recording_path(self, test_id: str, timestamp: str) -> Path:
        """録音ファイルのパスを生成する"""
        return self.recordings_dir / f"recording_{test_id}_{timestamp}.wav" 