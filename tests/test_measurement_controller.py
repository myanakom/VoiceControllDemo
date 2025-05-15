"""
計測システム制御のテストモジュール

このモジュールでは、計測システムの基本機能をテストします。
以下の機能について検証を行います：
1. 計測の開始/終了制御
2. データの記録と保存
3. 状態管理の動作

作成日: 2024-03-27
作成者: 開発チーム
"""

import sys
import os
from pathlib import Path
import json
import shutil
import time

# プロジェクトルートからの相対パスを設定
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from measurement.measurement_controller import MeasurementController

def setup_test_environment():
    """テスト環境のセットアップ"""
    test_data_dir = project_root / "test_data"
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)
    test_data_dir.mkdir(parents=True)
    return test_data_dir

def test_measurement_lifecycle():
    """計測のライフサイクルテスト"""
    test_data_dir = setup_test_environment()
    controller = MeasurementController(test_data_dir)
    
    # 計測開始テスト
    success = controller.start_measurement("K57", "牽引力", "標準")
    assert success == True
    assert controller.is_measuring == True
    print("計測開始テスト: 成功")
    
    # データ追加テスト
    success = controller.add_measurement_data(123.45)
    assert success == True
    print("データ追加テスト: 成功")
    
    # 計測終了テスト
    result = controller.stop_measurement()
    assert result is not None
    assert controller.is_measuring == False
    assert len(result["data"]) == 1
    assert result["data"][0]["value"] == 123.45
    print("計測終了テスト: 成功")
    
    # ファイル保存テスト
    measurement_dir = next(test_data_dir.glob("measurements/K57/牽引力/*"))
    json_file = measurement_dir / "measurement_data.json"
    csv_file = measurement_dir / "measurement_data.csv"
    
    assert json_file.exists()
    assert csv_file.exists()
    print("ファイル保存テスト: 成功")
    
    # 保存されたJSONデータの検証
    with open(json_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["vehicle"] == "K57"
    assert saved_data["test"] == "牽引力"
    assert saved_data["condition"] == "標準"
    print("保存データ検証: 成功")

def test_error_conditions():
    """エラー条件のテスト"""
    test_data_dir = setup_test_environment()
    controller = MeasurementController(test_data_dir)
    
    # 計測中でないときのデータ追加テスト
    success = controller.add_measurement_data(100)
    assert success == False
    print("未計測時データ追加テスト: 成功")
    
    # 計測中でないときの計測終了テスト
    result = controller.stop_measurement()
    assert result is None
    print("未計測時終了テスト: 成功")
    
    # 計測中の二重開始テスト
    controller.start_measurement("K57", "牽引力", "標準")
    success = controller.start_measurement("K57", "牽引力", "標準")
    assert success == False
    print("二重開始テスト: 成功")
    
    # クリーンアップ
    controller.stop_measurement()

if __name__ == "__main__":
    print("計測システム制御のテストを開始します")
    test_measurement_lifecycle()
    test_error_conditions()
    print("\nすべてのテストが完了しました") 