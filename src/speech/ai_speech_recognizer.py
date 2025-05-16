"""
AIを活用した音声認識モジュール
"""
import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
import queue
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv

class AISpeechRecognizer:
    """AI音声認識クラス"""
    
    def __init__(self, config_path: str = "config/speech_config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        self.is_listening = False
        self.callback = None
        
        # Azure OpenAI クライアントの初期化
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",  # 最新のAPI version
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # 音声設定
        self.sample_rate = 16000  # Whisperの要件に合わせる
        self.channels = 1  # モノラル
        self.dtype = np.float32
        self.buffer_duration = 0.5  # バッファ時間（秒）
        self.buffer_size = int(self.sample_rate * self.buffer_duration)
        
        # 音声バッファ
        self.audio_buffer = queue.Queue()
        self.buffer_thread = None
        
        # デバイス情報の取得とログ出力
        self.input_device = sd.default.device[0]
        self.output_device = sd.default.device[1]
        device_info = sd.query_devices(self.input_device)
        self.logger.info(f"Using input device: {device_info['name']}")
        
        # 一時ファイル用のディレクトリ
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 音声処理スレッド
        self.processing_thread = None
        self.should_stop = False
    
    def _get_default_devices(self) -> tuple:
        """デフォルトのオーディオデバイスを取得"""
        devices = sd.query_devices()
        default_input = sd.query_devices(kind='input')
        default_output = sd.query_devices(kind='output')
        
        self.logger.info(f"デフォルト入力デバイス: {default_input['name']}")
        self.logger.info(f"デフォルト出力デバイス: {default_output['name']}")
        
        return default_input, default_output
    
    def start_recognition(self, callback: Callable[[str], None]) -> None:
        """
        音声認識を開始
        
        Args:
            callback (Callable[[str], None]): 認識結果を受け取るコールバック関数
        """
        if self.is_listening:
            self.logger.warning("音声認識は既に実行中です")
            return
        
        try:
            self.callback = callback
            self.is_listening = True
            self.should_stop = False
            
            # デフォルトデバイスの取得
            default_input, _ = self._get_default_devices()
            
            # 音声録音の開始
            self.stream = sd.InputStream(
                device=default_input['index'],
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.buffer_size,
                callback=self._audio_callback
            )
            
            # 処理スレッドの開始
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.start()
            
            self.stream.start()
            self.logger.info("音声認識を開始しました")
            
        except Exception as e:
            self.logger.error(f"音声認識の開始に失敗: {str(e)}")
            raise
    
    def stop_recognition(self) -> None:
        """音声認識を停止"""
        if not self.is_listening:
            return
            
        try:
            self.should_stop = True
            self.is_listening = False
            
            # ストリームの停止
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
            
            # 処理スレッドの終了待ち
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join()
            
            self.logger.info("音声認識を停止しました")
            
        except Exception as e:
            self.logger.error(f"音声認識の停止に失敗: {str(e)}")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
        """
        音声データを受信した際のコールバック
        
        Args:
            indata (np.ndarray): 音声データ
            frames (int): フレーム数
            time (Any): タイムスタンプ
            status (Any): ストリームのステータス
        """
        if status:
            self.logger.warning(f"音声ストリームでエラー: {status}")
            return
        
        # 音声データをキューに追加
        self.audio_buffer.put(indata.copy())
    
    def _process_audio(self) -> None:
        """音声データの処理スレッド"""
        while not self.should_stop:
            try:
                # キューから音声データを取得
                audio_data = self.audio_buffer.get(timeout=1.0)
                
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data, self.sample_rate)
                    
                    # Whisperで音声認識
                    try:
                        with open(temp_file.name, "rb") as audio_file:
                            transcript = self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                language="ja"
                            )
                            
                            if transcript.text:
                                # コマンドの生成と実行
                                command = self._create_command(transcript.text)
                                if self.callback and command:
                                    self.callback(command)
                    except Exception as e:
                        self.logger.error(f"音声認識でエラー: {str(e)}")
                    finally:
                        # 一時ファイルの削除
                        os.unlink(temp_file.name)
                            
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"音声処理でエラー: {str(e)}")
    
    def _create_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        音声テキストからコマンドを生成
        
        Args:
            text (str): 音声認識テキスト
            
        Returns:
            Optional[Dict[str, Any]]: コマンド情報
        """
        try:
            # システムプロンプトの作成
            system_prompt = """
            あなたは計測システムの音声アシスタントです。
            ユーザーの発話から意図を理解し、適切なコマンドに変換してください。
            
            以下のような発話を適切に解釈してください：
            
            1. セッション管理
               入力例: "山田が担当で計測を始めます"
               期待出力: {"command_type": "session", "action": "start", "params": {"operator_name": "山田"}}
            
            2. 車両情報
               入力例: "テスト車両A123、名前はプロトタイプ1号、種別は電気自動車です"
               期待出力: {
                   "command_type": "vehicle",
                   "action": "register",
                   "params": {
                       "vehicle_id": "A123",
                       "vehicle_name": "プロトタイプ1号",
                       "vehicle_type": "電気自動車"
                   }
               }
            
            3. 試験情報
               入力例: "加速試験を開始します。試験IDはACC001、試験名は加速性能評価、種別は性能試験です"
               期待出力: {
                   "command_type": "test",
                   "action": "register",
                   "params": {
                       "test_id": "ACC001",
                       "test_name": "加速性能評価",
                       "test_type": "性能試験"
                   }
               }
            
            4. 計測データ
               入力例: "速度が60キロメートルです"
               期待出力: {
                   "command_type": "measurement",
                   "action": "add",
                   "params": {
                       "item_name": "速度",
                       "value": 60
                   }
               }
            
            5. メモ追加
               入力例: "路面が濡れているため、スリップに注意が必要です"
               期待出力: {
                   "command_type": "note",
                   "action": "add",
                   "params": {
                       "content": "路面が濡れているため、スリップに注意が必要です"
                   }
               }
            
            必ず上記のJSON形式で出力してください。
            """
            
            # ChatGPTで意図を解釈
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_MODEL"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            
            if response.choices[0].message.content:
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    self.logger.error("コマンドのJSONパースに失敗しました")
                    return None
            
        except Exception as e:
            self.logger.error(f"コマンド生成でエラー: {str(e)}")
            return None 