"""
計測データのモデルクラス
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

@dataclass
class VehicleInfo:
    """計測車両情報"""
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    description: Optional[str] = None

@dataclass
class TestInfo:
    """試験情報"""
    test_id: str
    test_name: str
    test_type: str
    conditions: Dict[str, str]
    description: Optional[str] = None

@dataclass
class MeasurementSession:
    """計測セッション情報"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    operator_name: str
    vehicle_info: VehicleInfo
    test_info: TestInfo
    recording_path: Optional[Path] = None
    notes: Optional[str] = None

@dataclass
class MeasurementData:
    """計測データ"""
    session: MeasurementSession
    data_points: List[Dict[str, float]]
    metadata: Dict[str, str]
    
    def to_dict(self) -> dict:
        """データを辞書形式に変換"""
        return {
            "session": {
                "session_id": self.session.session_id,
                "start_time": self.session.start_time.isoformat(),
                "end_time": self.session.end_time.isoformat() if self.session.end_time else None,
                "operator_name": self.session.operator_name,
                "vehicle_info": {
                    "vehicle_id": self.session.vehicle_info.vehicle_id,
                    "vehicle_name": self.session.vehicle_info.vehicle_name,
                    "vehicle_type": self.session.vehicle_info.vehicle_type,
                    "description": self.session.vehicle_info.description
                },
                "test_info": {
                    "test_id": self.session.test_info.test_id,
                    "test_name": self.session.test_info.test_name,
                    "test_type": self.session.test_info.test_type,
                    "conditions": self.session.test_info.conditions,
                    "description": self.session.test_info.description
                },
                "recording_path": str(self.session.recording_path) if self.session.recording_path else None,
                "notes": self.session.notes
            },
            "data_points": self.data_points,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MeasurementData':
        """辞書形式からデータを作成"""
        session_data = data["session"]
        vehicle_info = VehicleInfo(
            vehicle_id=session_data["vehicle_info"]["vehicle_id"],
            vehicle_name=session_data["vehicle_info"]["vehicle_name"],
            vehicle_type=session_data["vehicle_info"]["vehicle_type"],
            description=session_data["vehicle_info"].get("description")
        )
        
        test_info = TestInfo(
            test_id=session_data["test_info"]["test_id"],
            test_name=session_data["test_info"]["test_name"],
            test_type=session_data["test_info"]["test_type"],
            conditions=session_data["test_info"]["conditions"],
            description=session_data["test_info"].get("description")
        )
        
        session = MeasurementSession(
            session_id=session_data["session_id"],
            start_time=datetime.fromisoformat(session_data["start_time"]),
            end_time=datetime.fromisoformat(session_data["end_time"]) if session_data.get("end_time") else None,
            operator_name=session_data["operator_name"],
            vehicle_info=vehicle_info,
            test_info=test_info,
            recording_path=Path(session_data["recording_path"]) if session_data.get("recording_path") else None,
            notes=session_data.get("notes")
        )
        
        return cls(
            session=session,
            data_points=data["data_points"],
            metadata=data["metadata"]
        ) 