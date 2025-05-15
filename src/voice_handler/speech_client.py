"""
Azure Speech Serviceを使用した音声認識・合成クライアント

このモジュールは以下の機能を提供します：
1. 音声認識（音声→テキスト）
2. 音声合成（テキスト→音声）
"""

import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from pathlib import Path

class SpeechClient:
    def __init__(self):
        """音声クライアントの初期化"""
        # 環境変数の読み込み
        load_dotenv()
        
        # Azure Speech Service の設定
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.service_region = os.getenv('AZURE_SPEECH_REGION')
        self.language = os.getenv('AZURE_SPEECH_LANGUAGE', 'ja-JP')
        
        if not self.speech_key or not self.service_region:
            raise ValueError("Azure Speech Service の設定が見つかりません。.envファイルを確認してください。")
        
        # Speech SDK の設定
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.service_region
        )
        self.speech_config.speech_recognition_language = self.language
        self.speech_config.speech_synthesis_language = self.language
        
        # 音声認識の設定
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = None
        
    def start_recognition(self) -> str:
        """
        マイクからの音声入力をテキストに変換
        
        Returns:
            str: 認識されたテキスト。認識失敗時は空文字列
        """
        # 音声認識の初期化
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )
        
        # 音声認識の実行
        print("音声を認識しています...")
        result = self.speech_recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print(f"音声を認識できませんでした: {result.no_match_details}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"音声認識がキャンセルされました: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"エラー詳細: {cancellation_details.error_details}")
        
        return ""

    def stop_recognition(self):
        """音声認識を停止"""
        if self.speech_recognizer:
            self.speech_recognizer.stop_continuous_recognition_async()
            self.speech_recognizer = None
            print("音声認識を停止しました")
    
    def synthesize_speech(self, text: str, output_file: Path) -> bool:
        """
        テキストを音声に変換して保存
        
        Args:
            text: 音声に変換するテキスト
            output_file: 保存先のファイルパス
            
        Returns:
            bool: 音声合成が成功したかどうか
        """
        # 音声合成の設定
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_file))
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # 音声合成の実行
        print(f"テキストを音声に変換しています: {text}")
        result = speech_synthesizer.speak_text(text)
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("音声合成が完了しました")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"音声合成がキャンセルされました: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"エラー詳細: {cancellation_details.error_details}")
        
        return False