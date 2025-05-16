"""
音声コマンドのパース処理を行うモジュール
"""
import re
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from src.models.measurement_data import VehicleInfo, TestInfo

@dataclass
class ParsedCommand:
    """パース済みコマンド情報"""
    command_type: str  # session, vehicle, test, measurement, note
    action: str       # start, end, register, set, add
    params: Dict[str, Any]

class VoiceCommandParser:
    """音声コマンドパーサー"""
    
    def __init__(self):
        """初期化"""
        # セッション管理コマンドのパターン
        self.session_patterns = {
            'start': [
                r'計測開始\s+オペレーター\s*(?P<operator_name>[^\s]+)',
                r'新規セッション\s+担当者\s*(?P<operator_name>[^\s]+)'
            ],
            'end': [
                r'計測終了',
                r'セッション終了'
            ]
        }
        
        # 車両情報コマンドのパターン
        self.vehicle_patterns = {
            'register': [
                r'車両情報登録\s+ID\s*(?P<vehicle_id>[^\s]+)\s+名称\s*(?P<vehicle_name>[^\s]+)\s+種別\s*(?P<vehicle_type>[^\s]+)',
                r'車両設定\s+ID\s*(?P<vehicle_id>[^\s]+)\s+名前\s*(?P<vehicle_name>[^\s]+)\s+タイプ\s*(?P<vehicle_type>[^\s]+)'
            ]
        }
        
        # 試験情報コマンドのパターン
        self.test_patterns = {
            'register': [
                r'試験情報登録\s+ID\s*(?P<test_id>[^\s]+)\s+名称\s*(?P<test_name>[^\s]+)\s+種別\s*(?P<test_type>[^\s]+)'
            ],
            'set_condition': [
                r'試験条件設定\s+(?P<condition_name>[^\s]+)は(?P<condition_value>.+)'
            ]
        }
        
        # 計測データコマンドのパターン
        self.measurement_patterns = {
            'add': [
                r'計測値\s+(?P<item_name>[^\s]+)\s*(?P<value>[\d.]+)\s*(?P<unit>[^\s]*)',
                r'データ入力\s+(?P<item_name>[^\s]+)\s*(?P<value>[\d.]+)'
            ]
        }
        
        # メモコマンドのパターン
        self.note_patterns = {
            'add': [
                r'メモ追加\s+(?P<content>.+)',
                r'注釈\s+(?P<content>.+)'
            ]
        }
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        音声テキストをパースしてコマンドを解析
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[ParsedCommand]: パース結果
        """
        # セッション管理コマンドのチェック
        result = self._check_patterns(text, self.session_patterns, 'session')
        if result:
            return result
            
        # 車両情報コマンドのチェック
        result = self._check_patterns(text, self.vehicle_patterns, 'vehicle')
        if result:
            return result
            
        # 試験情報コマンドのチェック
        result = self._check_patterns(text, self.test_patterns, 'test')
        if result:
            return result
            
        # 計測データコマンドのチェック
        result = self._check_patterns(text, self.measurement_patterns, 'measurement')
        if result:
            return result
            
        # メモコマンドのチェック
        result = self._check_patterns(text, self.note_patterns, 'note')
        if result:
            return result
            
        return None
    
    def _check_patterns(
        self,
        text: str,
        patterns: Dict[str, list],
        command_type: str
    ) -> Optional[ParsedCommand]:
        """
        パターンマッチングを実行
        
        Args:
            text (str): 音声認識テキスト
            patterns (Dict[str, list]): パターン辞書
            command_type (str): コマンドタイプ
            
        Returns:
            Optional[ParsedCommand]: パース結果
        """
        for action, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.match(pattern, text)
                if match:
                    return ParsedCommand(
                        command_type=command_type,
                        action=action,
                        params=match.groupdict()
                    )
        return None
    
    def parse_vehicle_info(self, text: str) -> Optional[VehicleInfo]:
        """
        車両情報コマンドをパースしてVehicleInfoを作成
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[VehicleInfo]: 車両情報
        """
        command = self.parse(text)
        if not command or command.command_type != 'vehicle':
            return None
            
        return VehicleInfo(
            vehicle_id=command.params['vehicle_id'],
            vehicle_name=command.params['vehicle_name'],
            vehicle_type=command.params['vehicle_type']
        )
    
    def parse_test_info(self, text: str) -> Optional[TestInfo]:
        """
        試験情報コマンドをパースしてTestInfoを作成
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[TestInfo]: 試験情報
        """
        command = self.parse(text)
        if not command or command.command_type != 'test':
            return None
            
        if command.action == 'register':
            return TestInfo(
                test_id=command.params['test_id'],
                test_name=command.params['test_name'],
                test_type=command.params['test_type'],
                conditions={}
            )
        return None
    
    def parse_measurement_data(self, text: str) -> Optional[Dict[str, float]]:
        """
        計測データコマンドをパースしてデータポイントを作成
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[Dict[str, float]]: 計測データ
        """
        command = self.parse(text)
        if not command or command.command_type != 'measurement':
            return None
            
        try:
            value = float(command.params['value'])
            return {command.params['item_name']: value}
        except (ValueError, KeyError):
            return None 