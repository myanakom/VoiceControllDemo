"""
計測システム制御モジュール

このモジュールは計測システムの制御を担当します。
主な機能：
1. 計測の開始/終了制御
2. 計測データの保存
3. 計測状態の管理
"""

from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import json
import csv

class MeasurementController:
    def __init__(self, data_dir: Path):
        """
        計測コントローラーの初期化
        
        Args:
            data_dir: データ保存用のディレクトリパス
        """
        self.data_dir = data_dir
        self.current_measurement = None
        self.is_measuring = False
        
        # 計測データ保存用のディレクトリを作成
        self.measurements_dir = data_dir / "measurements"
        self.measurements_dir.mkdir(parents=True, exist_ok=True)
    
    def start_measurement(self, vehicle: str, test: str, condition: str) -> bool:
        """
        計測を開始
        
        Args:
            vehicle: 機種名
            test: 試験名
            condition: 試験条件
            
        Returns:
            bool: 開始が成功したかどうか
        """
        if self.is_measuring:
            return False
            
        # 計測情報の初期化
        self.current_measurement = {
            "vehicle": vehicle,
            "test": test,
            "condition": condition,
            "start_time": datetime.now().isoformat(),
            "data": []
        }
        
        # 計測用ディレクトリの作成
        measurement_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_data_dir = self.measurements_dir / vehicle / test / measurement_time
        self.current_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_measuring = True
        return True
    
    def stop_measurement(self) -> Optional[Dict]:
        """
        計測を終了し、結果を保存
        
        Returns:
            Optional[Dict]: 計測結果。失敗時はNone
        """
        if not self.is_measuring:
            return None
            
        # 計測終了時刻を記録
        self.current_measurement["end_time"] = datetime.now().isoformat()
        
        # 計測データをJSONファイルとして保存
        result_file = self.current_data_dir / "measurement_data.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(self.current_measurement, f, ensure_ascii=False, indent=2)
        
        # CSVファイルとしても保存（データ分析用）
        csv_file = self.current_data_dir / "measurement_data.csv"
        with open(csv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "value"])
            writer.writeheader()
            for data_point in self.current_measurement["data"]:
                writer.writerow(data_point)
        
        # 状態をリセット
        measurement_data = self.current_measurement
        self.current_measurement = None
        self.is_measuring = False
        
        return measurement_data
    
    def add_measurement_data(self, value: float) -> bool:
        """
        計測データを追加
        
        Args:
            value: 計測値
            
        Returns:
            bool: 追加が成功したかどうか
        """
        if not self.is_measuring:
            return False
            
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "value": value
        }
        
        self.current_measurement["data"].append(data_point)
        return True
    
    def get_measurement_status(self) -> Dict:
        """現在の計測状態を取得"""
        return {
            "is_measuring": self.is_measuring,
            "current_measurement": self.current_measurement
        } 