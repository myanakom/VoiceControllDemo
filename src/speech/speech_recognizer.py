"""
音声認識モジュール
"""
import os
import yaml
import azure.cognitiveservices.speech as speechsdk
from typing import Optional, Callable, Dict, List, Tuple
import logging
from dotenv import load_dotenv
import subprocess
import json

class SpeechRecognizer:
    """音声認識クラス"""
    
    def __init__(self, config_path: str = "config/speech_config.yaml"):
        """
        音声認識クラスの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        # 環境変数の読み込み
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.speech_config = self._create_speech_config()
        self.speech_recognizer = None
        self.is_listening = False
        self.callback = None
        self.selected_mic_id = None
    
    def _load_config(self, config_path: str) -> dict:
        """設定ファイルを読み込む"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 環境変数から値を取得
            config['azure_speech']['subscription_key'] = os.getenv('AZURE_SPEECH_KEY')
            config['azure_speech']['region'] = os.getenv('AZURE_SPEECH_REGION')
            config['azure_speech']['language'] = os.getenv('AZURE_SPEECH_LANGUAGE', 'ja-JP')
            
            # 設定値の検証
            if not config['azure_speech']['subscription_key'] or not config['azure_speech']['region']:
                raise ValueError("Azure Speech Serviceの設定が不完全です。環境変数を確認してください。")
            
            return config
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗: {str(e)}")
            raise
    
    def _create_speech_config(self) -> speechsdk.SpeechConfig:
        """Speech SDKの設定を作成"""
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.config['azure_speech']['subscription_key'],
                region=self.config['azure_speech']['region']
            )
            speech_config.speech_recognition_language = self.config['azure_speech']['language']
            
            # 音声認識の詳細設定
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, 
                "15000"  # 初期サイレンスタイムアウトを15秒に設定
            )
            speech_config.set_property(
                speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, 
                "1000"   # セグメント間のサイレンスタイムアウトを1秒に設定
            )
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, 
                "1000"   # 終了サイレンスタイムアウトを1秒に設定
            )
            
            return speech_config
        except Exception as e:
            self.logger.error(f"Speech SDK設定の作成に失敗: {str(e)}")
            raise
    
    @staticmethod
    def list_microphones() -> List[Tuple[str, str]]:
        """
        利用可能なマイクデバイスの一覧を取得
        
        Returns:
            List[Tuple[str, str]]: (デバイスID, デバイス名)のリスト
        """
        try:
            # PowerShellコマンドを作成
            ps_command = """
            Add-Type -AssemblyName System.Windows.Forms
            $devices = Get-WmiObject Win32_SoundDevice | Where-Object { $_.StatusInfo -eq 1 }
            $devices | ForEach-Object {
                @{
                    'ID' = $_.DeviceID;
                    'Name' = $_.Name;
                }
            } | ConvertTo-Json
            """
            
            # PowerShellを実行
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # JSON出力をパース
                devices = json.loads(result.stdout)
                if not isinstance(devices, list):
                    devices = [devices]
                
                return [(dev['ID'], dev['Name']) for dev in devices]
            else:
                logging.warning("マイクデバイスの一覧取得に失敗しました。デフォルトのマイクを使用します。")
                return []
                
        except Exception as e:
            logging.error(f"マイクデバイスの一覧取得でエラー: {str(e)}")
            return []

    def select_microphone(self, device_id: str) -> None:
        """
        使用するマイクデバイスを選択
        
        Args:
            device_id (str): マイクデバイスのID
        """
        self.selected_mic_id = device_id
        self.logger.info(f"マイクデバイスを選択: {device_id}")

    def start_recognition(self, callback: Callable[[str], None]) -> None:
        """
        音声認識を開始する
        
        Args:
            callback (Callable[[str], None]): 認識結果を受け取るコールバック関数
        """
        if self.is_listening:
            self.logger.warning("音声認識は既に実行中です")
            return
        
        try:
            self.callback = callback
            
            # マイクの設定
            if self.selected_mic_id:
                # 選択されたマイクを使用
                audio_config = speechsdk.audio.AudioConfig(device_name=self.selected_mic_id)
                self.logger.info(f"選択されたマイクを使用: {self.selected_mic_id}")
            else:
                # デフォルトのマイクを使用
                audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                self.logger.info("デフォルトのマイクを使用")
            
            # 音声認識の設定
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # イベントハンドラの設定
            self.speech_recognizer.recognizing.connect(self._handle_recognizing)
            self.speech_recognizer.recognized.connect(self._handle_result)
            self.speech_recognizer.session_started.connect(self._handle_session_started)
            self.speech_recognizer.session_stopped.connect(self._handle_session_stopped)
            self.speech_recognizer.canceled.connect(self._handle_canceled)
            
            # 音声認識の開始
            self.speech_recognizer.start_continuous_recognition()
            self.is_listening = True
            self.logger.info("音声認識を開始しました: マイクを使用して音声入力を待機しています")
            
        except Exception as e:
            self.logger.error(f"音声認識の開始に失敗: {str(e)}")
            raise

    def _handle_recognizing(self, evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        """音声認識中のイベントを処理"""
        try:
            text = evt.result.text
            if text:
                self.logger.debug(f"音声認識中: {text}")
        except Exception as e:
            self.logger.error(f"音声認識中のイベント処理でエラー: {str(e)}")

    def _handle_session_started(self, evt: speechsdk.SessionEventArgs) -> None:
        """セッション開始イベントを処理"""
        try:
            self.logger.info("音声認識セッション開始: マイクからの入力を待機中...")
            # マイクの状態を確認
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            if not audio_config:
                self.logger.error("マイクの初期化に失敗しました")
        except Exception as e:
            self.logger.error(f"セッション開始イベントの処理でエラー: {str(e)}")

    def _handle_session_stopped(self, evt: speechsdk.SessionEventArgs) -> None:
        """セッション終了イベントを処理"""
        try:
            self.logger.info("音声認識セッション終了: マイクの使用を停止しました")
        except Exception as e:
            self.logger.error(f"セッション終了イベントの処理でエラー: {str(e)}")

    def _handle_canceled(self, evt: speechsdk.SpeechRecognitionCanceledEventArgs) -> None:
        """キャンセルイベントを処理"""
        try:
            cancellation_details = evt.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                self.logger.error(f"音声認識エラー: {cancellation_details.error_details}")
                
                # エラーの詳細な分析
                error_details = cancellation_details.error_details.lower()
                if "401" in error_details:
                    self.logger.error("認証エラー: Azure Speech Serviceの設定を確認してください")
                elif "connectionfailure" in error_details:
                    self.logger.error("接続エラー: インターネット接続を確認してください")
                elif "nomatch" in error_details:
                    self.logger.warning("音声が認識できませんでした: マイクの設定を確認してください")
                elif "microphone" in error_details:
                    self.logger.error("マイクが利用できません: マイクの接続と設定を確認してください")
            else:
                self.logger.warning(f"音声認識がキャンセルされました: {cancellation_details.reason}")
        except Exception as e:
            self.logger.error(f"キャンセルイベントの処理でエラー: {str(e)}")

    def _handle_result(self, evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        """
        認識結果を処理する
        
        Args:
            evt (speechsdk.SpeechRecognitionEventArgs): 認識結果イベント
        """
        try:
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text
                self.logger.info(f"音声認識成功: {text}")
                if self.callback:
                    self.callback(text)
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                no_match_detail = evt.result.no_match_details
                if no_match_detail.reason == speechsdk.NoMatchReason.InitialSilenceTimeout:
                    self.logger.warning("音声入力がタイムアウトしました: 話し始めるまでに時間がかかりすぎました")
                elif no_match_detail.reason == speechsdk.NoMatchReason.EndSilenceTimeout:
                    self.logger.warning("音声入力が途切れました: 発話の間隔が長すぎました")
                else:
                    self.logger.warning(f"音声を認識できませんでした: {no_match_detail.reason}")
        except Exception as e:
            self.logger.error(f"認識結果の処理でエラー: {str(e)}")
    
    def stop_recognition(self) -> None:
        """音声認識を停止する"""
        if not self.is_listening:
            self.logger.warning("音声認識は既に停止しています")
            return
        
        try:
            self.speech_recognizer.stop_continuous_recognition()
            self.is_listening = False
            self.logger.info("音声認識を停止しました")
        except Exception as e:
            self.logger.error(f"音声認識の停止に失敗: {str(e)}")
            raise 