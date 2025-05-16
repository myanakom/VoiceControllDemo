"""
マイク動作確認用のテストスクリプト
"""
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

def test_microphone():
    # 環境変数の読み込み
    load_dotenv()
    
    # Azure Speech Service の設定
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    service_region = os.getenv('AZURE_SPEECH_REGION')
    
    if not speech_key or not service_region:
        print("Error: AZURE_SPEECH_KEY または AZURE_SPEECH_REGION が設定されていません")
        return
    
    # Speech SDK の設定
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=service_region
    )
    speech_config.speech_recognition_language = "ja-JP"
    
    # 音声認識のプロパティを設定
    speech_config.set_property(
        speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "2000"
    )
    speech_config.set_property(
        speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "10000"
    )
    
    # マイクの設定
    audio_config = speechsdk.audio.AudioConfig(
        use_default_microphone=True
    )
    
    # 音声認識の初期化
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    print("マイクのテストを開始します...")
    print("何か話しかけてください（10秒間）")
    print("音声入力を待機中...")
    
    # 単発の音声認識を実行
    result = recognizer.recognize_once_async().get()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"認識されたテキスト: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print(f"音声を認識できませんでした: {result.no_match_details}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"音声認識がキャンセルされました: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"エラー詳細: {cancellation_details.error_details}")

if __name__ == "__main__":
    test_microphone() 