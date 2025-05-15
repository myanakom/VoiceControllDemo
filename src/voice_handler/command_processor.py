"""
音声コマンド処理モジュール

このモジュールは音声コマンドの解析と実行を担当します。
主な機能：
1. コマンドパターンの定義と管理
2. 音声入力とコマンドのマッチング
3. コマンド実行の制御
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import difflib

class CommandProcessor:
    def __init__(self):
        """コマンドプロセッサの初期化"""
        # コマンドパターンの定義
        self.command_patterns = {
            "計測開始": {
                "aliases": ["測定開始", "スタート", "開始"],
                "action": "start_measurement"
            },
            "計測終了": {
                "aliases": ["測定終了", "ストップ", "終了"],
                "action": "stop_measurement"
            },
            "機種選択": {
                "aliases": ["機種を選択", "機種変更"],
                "action": "select_vehicle",
                "requires_param": True
            },
            "試験選択": {
                "aliases": ["試験を選択", "試験変更"],
                "action": "select_test",
                "requires_param": True
            }
        }
        
        # 現在の状態管理
        self.current_state = {
            "is_measuring": False,
            "selected_vehicle": None,
            "selected_test": None,
            "selected_condition": None
        }
    
    def process_command(self, voice_input: str) -> Tuple[str, Optional[str]]:
        """
        音声入力を解析してコマンドを特定し、対応するアクションを返す
        
        Args:
            voice_input: 音声認識結果のテキスト
            
        Returns:
            Tuple[str, Optional[str]]: (アクション名, パラメータ)
        """
        # 入力の正規化（空白除去、小文字化）
        normalized_input = voice_input.strip()
        
        # 最も類似したコマンドを探す
        best_match = None
        best_ratio = 0
        matched_param = None
        
        for cmd, details in self.command_patterns.items():
            # メインコマンドとエイリアスをチェック
            all_patterns = [cmd] + details["aliases"]
            
            for pattern in all_patterns:
                # コマンドとパラメータを分離
                if details.get("requires_param", False):
                    # パラメータを含むコマンドの場合
                    if pattern in normalized_input:
                        # パラメータを抽出
                        param_start = normalized_input.find(pattern) + len(pattern)
                        matched_param = normalized_input[param_start:].strip()
                        ratio = 1.0
                    else:
                        continue
                else:
                    # 単純なコマンドの場合
                    ratio = difflib.SequenceMatcher(None, pattern, normalized_input).ratio()
                
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = details["action"]
        
        # マッチング閾値（0.8以上で一致とみなす）
        if best_ratio >= 0.8:
            return best_match, matched_param
            
        return "unknown_command", None
    
    def update_state(self, action: str, param: Optional[str] = None) -> bool:
        """
        システムの状態を更新
        
        Args:
            action: 実行するアクション
            param: アクションのパラメータ（必要な場合）
            
        Returns:
            bool: 更新が成功したかどうか
        """
        if action == "start_measurement":
            if not all([self.current_state["selected_vehicle"],
                       self.current_state["selected_test"],
                       self.current_state["selected_condition"]]):
                return False
            self.current_state["is_measuring"] = True
            
        elif action == "stop_measurement":
            self.current_state["is_measuring"] = False
            
        elif action == "select_vehicle":
            if not param:
                return False
            self.current_state["selected_vehicle"] = param
            
        elif action == "select_test":
            if not param:
                return False
            self.current_state["selected_test"] = param
            self.current_state["selected_condition"] = None  # 試験変更時は条件をリセット
            
        return True
    
    def get_current_state(self) -> Dict:
        """現在の状態を取得"""
        return self.current_state.copy() 