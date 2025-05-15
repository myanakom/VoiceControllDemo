"""
コマンドプロセッサのテストモジュール

このモジュールでは、音声コマンド処理の基本機能をテストします。
以下の機能について検証を行います：
1. コマンド認識の精度
2. パラメータ付きコマンドの処理
3. 状態管理の動作

作成日: 2024-03-27
作成者: 開発チーム
"""

import sys
import os
from pathlib import Path

# プロジェクトルートからの相対パスを設定
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from voice_handler.command_processor import CommandProcessor

def test_command_recognition():
    """基本的なコマンド認識のテスト"""
    processor = CommandProcessor()
    
    # 完全一致のテスト
    action, param = processor.process_command("計測開始")
    assert action == "start_measurement"
    assert param is None
    print("完全一致テスト: 成功")
    
    # エイリアスのテスト
    action, param = processor.process_command("測定開始")
    assert action == "start_measurement"
    assert param is None
    print("エイリアステスト: 成功")
    
    # 未知のコマンドのテスト
    action, param = processor.process_command("不明なコマンド")
    assert action == "unknown_command"
    assert param is None
    print("未知のコマンドテスト: 成功")

def test_parameterized_commands():
    """パラメータ付きコマンドのテスト"""
    processor = CommandProcessor()
    
    # 機種選択コマンドのテスト
    action, param = processor.process_command("機種選択 K57")
    assert action == "select_vehicle"
    assert param == "K57"
    print("機種選択テスト: 成功")
    
    # 試験選択コマンドのテスト
    action, param = processor.process_command("試験を選択 牽引力")
    assert action == "select_test"
    assert param == "牽引力"
    print("試験選択テスト: 成功")

def test_state_management():
    """状態管理のテスト"""
    processor = CommandProcessor()
    
    # 初期状態の確認
    state = processor.get_current_state()
    assert state["is_measuring"] == False
    assert state["selected_vehicle"] is None
    print("初期状態テスト: 成功")
    
    # 機種選択
    success = processor.update_state("select_vehicle", "K57")
    assert success == True
    state = processor.get_current_state()
    assert state["selected_vehicle"] == "K57"
    print("状態更新（機種選択）テスト: 成功")
    
    # 試験選択
    success = processor.update_state("select_test", "牽引力")
    assert success == True
    state = processor.get_current_state()
    assert state["selected_test"] == "牽引力"
    print("状態更新（試験選択）テスト: 成功")
    
    # 不完全な状態での計測開始（失敗するはず）
    success = processor.update_state("start_measurement")
    assert success == False
    state = processor.get_current_state()
    assert state["is_measuring"] == False
    print("不完全状態での計測開始テスト: 成功")

if __name__ == "__main__":
    print("コマンドプロセッサのテストを開始します")
    test_command_recognition()
    test_parameterized_commands()
    test_state_management()
    print("\nすべてのテストが完了しました") 