# -*- coding: utf-8 -*-
"""
UIの手動テストスクリプト
"""
import time
import sys
import os
from pathlib import Path

# プロジェクトルートへのパスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.ui_controller import UIController

def manual_test():
    """UIの手動テスト"""
    print("UIの手動テストを開始します...")
    controller = UIController()
    
    def show_menu():
        print("\n利用可能なコマンド:")
        print("1: 計測情報を更新")
        print("2: 録音開始")
        print("3: 録音停止")
        print("4: システム状態を更新")
        print("q: 終了")
    
    # メニュー処理
    def handle_command(cmd):
        if cmd == "1":
            controller.update_measurement_info({
                "機種": "K57",
                "試験名": "牽引力試験",
                "試験条件": "前進速度3km/h",
                "計測者": "テスト太郎"
            })
            print("計測情報を更新しました")
        
        elif cmd == "2":
            controller.set_recording_state(True)
            controller.update_system_status("計測中")
            print("録音を開始しました")
        
        elif cmd == "3":
            controller.set_recording_state(False)
            controller.update_system_status("計測完了")
            print("録音を停止しました")
        
        elif cmd == "4":
            status = input("新しいステータスを入力してください: ")
            controller.update_system_status(status)
            print(f"システム状態を「{status}」に更新しました")
    
    # コマンド受付用スレッド
    import threading
    def command_loop():
        while True:
            show_menu()
            cmd = input("\nコマンドを入力してください: ")
            if cmd.lower() == "q":
                controller.stop()
                break
            handle_command(cmd)
    
    # コマンド受付スレッドの開始
    threading.Thread(target=command_loop, daemon=True).start()
    
    # UIの開始
    controller.start()

if __name__ == "__main__":
    manual_test() 