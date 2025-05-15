import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

class DataLoader:
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self._load_data()

    def _load_data(self):
        """データファイルの読み込み"""
        self.vehicles = pd.read_csv(self.data_dir / "vehicles.csv")
        self.tests = pd.read_csv(self.data_dir / "tests.csv")
        self.conditions = pd.read_csv(self.data_dir / "conditions.csv")
        self.users = pd.read_csv(self.data_dir / "users.csv")

    def get_vehicle_by_name(self, name: str) -> Optional[Dict]:
        """機種名から機種情報を取得"""
        vehicle = self.vehicles[self.vehicles['name'] == name]
        return vehicle.to_dict('records')[0] if not vehicle.empty else None

    def get_test_by_alias(self, alias: str) -> List[Dict]:
        """試験名のエイリアスから試験情報を取得"""
        tests = self.tests[
            (self.tests['name'].str.contains(alias)) | 
            (self.tests['alias'].str.contains(alias))
        ]
        return tests.to_dict('records')

    def get_conditions_by_test_id(self, test_id: str) -> List[Dict]:
        """試験IDから条件リストを取得"""
        conditions = self.conditions[self.conditions['test_id'] == test_id]
        return conditions.to_dict('records')

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ユーザーIDからユーザー情報を取得"""
        user = self.users[self.users['user_id'] == user_id]
        return user.to_dict('records')[0] if not user.empty else None