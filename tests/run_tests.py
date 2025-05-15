"""
テスト実行用のラッパースクリプト

このスクリプトは以下の機能を提供します：
1. 指定されたテストの実行
2. テスト結果のログ保存
3. テスト実行履歴の管理
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import importlib
import traceback

def run_test(test_module_name: str) -> bool:
    """
    指定されたテストモジュールを実行し、結果をログに保存します
    
    Args:
        test_module_name: テストモジュールの名前（例: "test_data_loader"）
    
    Returns:
        bool: テストが成功したかどうか
    """
    # ログファイルの準備
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(__file__).parent / "logs" / f"{test_module_name}_{timestamp}.log"
    
    try:
        # 標準出力をログファイルにリダイレクト
        with open(log_file, "w", encoding='utf-8') as f:
            f.write(f"=== テスト実行: {test_module_name} ===\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # テストモジュールの動的インポートと実行
            module = importlib.import_module(test_module_name)
            
            # モジュールのdocstringを記録
            if module.__doc__:
                f.write("テスト概要:\n")
                f.write(module.__doc__ + "\n\n")
            
            # テストの実行
            original_stdout = sys.stdout
            sys.stdout = f
            
            if hasattr(module, 'test_data_loader'):
                module.test_data_loader()
                f.write("\nテスト結果: 成功\n")
                return True
            else:
                f.write("\nエラー: テスト関数が見つかりません\n")
                return False
            
    except Exception as e:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"\nエラー発生:\n{str(e)}\n")
            f.write(traceback.format_exc())
        return False
    finally:
        sys.stdout = original_stdout

if __name__ == "__main__":
    # テストモジュールのリスト
    test_modules = ["test_data_loader"]
    
    # 各テストの実行
    for test_module in test_modules:
        success = run_test(test_module)
        print(f"{test_module}: {'成功' if success else '失敗'}")