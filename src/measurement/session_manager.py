"""
計測セッション管理モジュール
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import logging

from src.models.measurement_data import (
    MeasurementData,
    MeasurementSession,
    VehicleInfo,
    TestInfo
)

class SessionManager:
    """計測セッション管理クラス"""
    
    def __init__(self, data_dir: Path):
        """
        初期化
        
        Args:
            data_dir (Path): データ保存ディレクトリ
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        self.current_session: Optional[MeasurementSession] = None
        self.data_points: List[Dict[str, float]] = []
        self.metadata: Dict[str, str] = {}
        
        # データディレクトリの作成
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # セッションデータ保存用のディレクトリ
        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # 音声録音保存用のディレクトリ
        self.recordings_dir = self.data_dir / "recordings"
        self.recordings_dir.mkdir(exist_ok=True)
    
    def start_session(
        self,
        operator_name: str,
        vehicle_info: VehicleInfo,
        test_info: TestInfo
    ) -> MeasurementSession:
        """
        新しいセッションを開始
        
        Args:
            operator_name (str): 計測者名
            vehicle_info (VehicleInfo): 車両情報
            test_info (TestInfo): 試験情報
            
        Returns:
            MeasurementSession: 作成されたセッション
        """
        if self.current_session:
            self.logger.warning("既存のセッションが終了していません")
            self.end_session()
        
        session_id = str(uuid.uuid4())
        self.current_session = MeasurementSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            operator_name=operator_name,
            vehicle_info=vehicle_info,
            test_info=test_info
        )
        
        self.data_points = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "session_type": "measurement"
        }
        
        self.logger.info(f"セッションを開始: {session_id}")
        return self.current_session
    
    def end_session(self) -> Optional[MeasurementData]:
        """
        現在のセッションを終了
        
        Returns:
            Optional[MeasurementData]: 終了したセッションのデータ
        """
        if not self.current_session:
            self.logger.warning("アクティブなセッションがありません")
            return None
        
        self.current_session.end_time = datetime.now()
        measurement_data = MeasurementData(
            session=self.current_session,
            data_points=self.data_points,
            metadata=self.metadata
        )
        
        # データの保存
        self._save_session_data(measurement_data)
        
        self.logger.info(f"セッションを終了: {self.current_session.session_id}")
        
        # セッション情報のクリア
        session_data = measurement_data
        self.current_session = None
        self.data_points = []
        self.metadata = {}
        
        return session_data
    
    def add_data_point(self, data: Dict[str, float]) -> None:
        """
        データポイントを追加
        
        Args:
            data (Dict[str, float]): 計測データ
        """
        if not self.current_session:
            self.logger.error("アクティブなセッションがありません")
            raise RuntimeError("セッションが開始されていません")
        
        self.data_points.append({
            "timestamp": datetime.now().isoformat(),
            **data
        })
    
    def set_recording_path(self, path: Path) -> None:
        """
        音声録音のパスを設定
        
        Args:
            path (Path): 録音ファイルのパス
        """
        if not self.current_session:
            self.logger.error("アクティブなセッションがありません")
            raise RuntimeError("セッションが開始されていません")
        
        self.current_session.recording_path = path
    
    def add_notes(self, notes: str) -> None:
        """
        セッションにノートを追加
        
        Args:
            notes (str): 追加するノート
        """
        if not self.current_session:
            self.logger.error("アクティブなセッションがありません")
            raise RuntimeError("セッションが開始されていません")
        
        if self.current_session.notes:
            self.current_session.notes += f"\n{notes}"
        else:
            self.current_session.notes = notes
    
    def _save_session_data(self, data: MeasurementData) -> None:
        """
        セッションデータをファイルに保存
        
        Args:
            data (MeasurementData): 保存するデータ
        """
        session_id = data.session.session_id
        file_path = self.sessions_dir / f"session_{session_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info(f"セッションデータを保存: {file_path}")
        except Exception as e:
            self.logger.error(f"セッションデータの保存に失敗: {str(e)}")
            raise
    
    def load_session(self, session_id: str) -> Optional[MeasurementData]:
        """
        保存されたセッションデータを読み込む
        
        Args:
            session_id (str): セッションID
            
        Returns:
            Optional[MeasurementData]: 読み込まれたデータ
        """
        file_path = self.sessions_dir / f"session_{session_id}.json"
        
        if not file_path.exists():
            self.logger.warning(f"セッションデータが見つかりません: {session_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return MeasurementData.from_dict(data)
        except Exception as e:
            self.logger.error(f"セッションデータの読み込みに失敗: {str(e)}")
            raise 