"""
UIコントローラーモジュール
"""
from typing import Optional, Dict, Any
import logging
from .main_window import MainWindow

class UIController:
    """UIコントローラークラス"""
    
    def __init__(self):
        """UIコントローラーの初期化"""
        self.window = MainWindow()
        self.logger = logging.getLogger(__name__)
        
        # 初期状態の設定
        self._set_initial_state()
    
    def _set_initial_state(self):
        """初期状態の設定"""
        initial_info = {
            "機種": "未選択",
            "試験名": "未選択",
            "試験条件": "未設定",
            "計測者": "未設定"
        }
        self.window.update_info(initial_info)
        self.window.update_status("準備完了")
        self.window.update_recording_status(False)
    
    def update_measurement_info(self, info: Dict[str, Any]) -> None:
        """計測情報の更新"""
        # 必須キーの確認
        required_keys = {"機種", "試験名", "試験条件", "計測者"}
        if not all(key in info for key in required_keys):
            self.logger.error(f"計測情報に必須キーが不足しています: {info}")
            raise ValueError("計測情報に必須キーが不足しています")
            
        self.window.update_info(info)
        self.logger.info(f"計測情報を更新: {info}")
    
    def update_system_status(self, status: str) -> None:
        """システム状態の更新"""
        self.window.update_status(status)
        self.logger.info(f"システム状態を更新: {status}")
    
    def set_recording_state(self, is_recording: bool) -> None:
        """録音状態の更新"""
        self.window.update_recording_status(is_recording)
        status = "録音中" if is_recording else "録音停止"
        self.logger.info(f"録音状態を更新: {status}")
    
    def start(self) -> None:
        """UIの開始"""
        self.logger.info("UIを開始します")
        self.window.run()
    
    def stop(self) -> None:
        """UIの停止"""
        self.logger.info("UIを停止します")
        self.window.stop() 