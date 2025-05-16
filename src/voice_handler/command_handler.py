"""
音声コマンドの処理を行うモジュール
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.voice_handler.command_parser import VoiceCommandParser, ParsedCommand
from src.measurement.session_manager import SessionManager
from src.models.measurement_data import VehicleInfo, TestInfo

class VoiceCommandHandler:
    """音声コマンドハンドラー"""
    
    def __init__(self, session_manager: SessionManager):
        """
        初期化
        
        Args:
            session_manager (SessionManager): セッション管理インスタンス
        """
        self.logger = logging.getLogger(__name__)
        self.session_manager = session_manager
        self.command_parser = VoiceCommandParser()
        
        # 一時保存用の車両情報と試験情報
        self.temp_vehicle_info: Optional[VehicleInfo] = None
        self.temp_test_info: Optional[TestInfo] = None
        self.temp_test_conditions: Dict[str, str] = {}
    
    def handle_command(self, text: str) -> Optional[str]:
        """
        音声コマンドを処理
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[str]: 処理結果のメッセージ
        """
        command = self.command_parser.parse(text)
        if not command:
            return "コマンドを認識できませんでした"
            
        try:
            if command.command_type == 'session':
                return self._handle_session_command(command)
            elif command.command_type == 'vehicle':
                return self._handle_vehicle_command(command)
            elif command.command_type == 'test':
                return self._handle_test_command(command)
            elif command.command_type == 'measurement':
                return self._handle_measurement_command(command)
            elif command.command_type == 'note':
                return self._handle_note_command(command)
            else:
                return "未対応のコマンドタイプです"
        except Exception as e:
            self.logger.error(f"コマンド処理でエラー: {str(e)}")
            return f"エラーが発生しました: {str(e)}"
    
    def _handle_session_command(self, command: ParsedCommand) -> str:
        """セッション管理コマンドの処理"""
        if command.action == 'start':
            if not self.temp_vehicle_info or not self.temp_test_info:
                return "車両情報と試験情報を先に設定してください"
                
            self.session_manager.start_session(
                operator_name=command.params['operator_name'],
                vehicle_info=self.temp_vehicle_info,
                test_info=self.temp_test_info
            )
            return "計測セッションを開始しました"
            
        elif command.action == 'end':
            data = self.session_manager.end_session()
            if data:
                return "計測セッションを終了し、データを保存しました"
            else:
                return "アクティブなセッションがありません"
    
    def _handle_vehicle_command(self, command: ParsedCommand) -> str:
        """車両情報コマンドの処理"""
        if command.action == 'register':
            self.temp_vehicle_info = VehicleInfo(
                vehicle_id=command.params['vehicle_id'],
                vehicle_name=command.params['vehicle_name'],
                vehicle_type=command.params['vehicle_type']
            )
            return "車両情報を登録しました"
    
    def _handle_test_command(self, command: ParsedCommand) -> str:
        """試験情報コマンドの処理"""
        if command.action == 'register':
            self.temp_test_info = TestInfo(
                test_id=command.params['test_id'],
                test_name=command.params['test_name'],
                test_type=command.params['test_type'],
                conditions=self.temp_test_conditions
            )
            return "試験情報を登録しました"
            
        elif command.action == 'set_condition':
            if not self.temp_test_info:
                self.temp_test_conditions[command.params['condition_name']] = command.params['condition_value']
            else:
                self.temp_test_info.conditions[command.params['condition_name']] = command.params['condition_value']
            return "試験条件を設定しました"
    
    def _handle_measurement_command(self, command: ParsedCommand) -> str:
        """計測データコマンドの処理"""
        try:
            data = {
                command.params['item_name']: float(command.params['value'])
            }
            self.session_manager.add_data_point(data)
            return f"計測データを記録しました: {command.params['item_name']} = {command.params['value']}"
        except ValueError:
            return "無効な数値です"
        except RuntimeError as e:
            return str(e)
    
    def _handle_note_command(self, command: ParsedCommand) -> str:
        """メモコマンドの処理"""
        try:
            self.session_manager.add_notes(command.params['content'])
            return "メモを追加しました"
        except RuntimeError as e:
            return str(e) 