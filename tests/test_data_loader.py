"""
データローダーのテストモジュール

このモジュールでは、データ管理システムの基本機能をテストします。
以下の機能について検証を行います：
1. 機種情報の取得 (vehicles.csv)
2. 試験名の検索 (tests.csv)
3. 試験条件の取得 (conditions.csv)
4. ユーザー情報の取得 (users.csv)

作成日: 2024-03-26
作成者: 開発チーム
"""

import sys
import os
from pathlib import Path

# プロジェクトルートからの相対パスを設定
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from data_manager.data_loader import DataLoader

def test_data_loader():
    """
    データローダーの基本機能テスト
    
    テスト項目:
    1. 機種の取得テスト
       - 期待値: K57の情報が取得できること
    2. 試験名の取得テスト
       - 期待値: "牽引"をキーワードに含む試験が1つ以上取得できること
    3. 条件の取得テスト
       - 期待値: 試験ID "T001" に紐づく条件が1つ以上取得できること
    4. ユーザーの取得テスト
       - 期待値: ユーザーID "U001" のユーザー情報が取得できること
    """
    data_path = project_root / 'src' / 'data'
    loader = DataLoader(str(data_path))
    
    # 機種の取得テスト
    vehicle = loader.get_vehicle_by_name("K57")
    assert vehicle is not None, "K57が見つかりません"
    print("機種テスト成功")

    # 試験名の取得テスト
    tests = loader.get_test_by_alias("牽引")
    assert len(tests) > 0, "牽引力試験が見つかりません"
    print("試験名テスト成功")

    # 条件の取得テスト
    conditions = loader.get_conditions_by_test_id("T001")
    assert len(conditions) > 0, "牽引力試験の条件が見つかりません"
    print("条件テスト成功")

    # ユーザーの取得テスト
    user = loader.get_user_by_id("U001")
    assert user is not None, "ユーザーが見つかりません"
    print("ユーザーテスト成功")

if __name__ == "__main__":
    test_data_loader()