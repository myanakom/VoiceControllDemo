"""
音声認識のテストスクリプト

このスクリプトでは以下の項目をテストします：
1. マイクの動作確認
2. 音声認識の基本機能
3. 音声認識の制御機能
"""
import sys
import os
import time
import logging
from pathlib import Path
import threading
import queue
import azure.cognitiveservices.speech as speechsdk

# プロジェクトルートへのパスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.speech.speech_recognizer import SpeechRecognizer

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def select_microphone(recognizer: SpeechRecognizer) -> bool:
    """
    使用するマイクを選択
    
    Returns:
        bool: マイクの選択が成功したかどうか
    """
    print("\n=== マイクの選択 ===")
    print("利用可能なマイクデバイスを検索中...")
    
    mics = recognizer.list_microphones()
    if not mics:
        print("利用可能なマイクが見つかりませんでした。デフォルトのマイクを使用します。")
        return True
    
    print("\n利用可能なマイク:")
    for i, (device_id, device_name) in enumerate(mics, 1):
        print(f"{i}: {device_name}")
    
    print("\nマイクを選択してください（番号を入力）")
    print("デフォルトのマイクを使用する場合は Enter キーを押してください: ", end='')
    
    selection = input().strip()
    if not selection:
        print("デフォルトのマイクを使用します")
        return True
    
    try:
        index = int(selection) - 1
        if 0 <= index < len(mics):
            device_id, device_name = mics[index]
            recognizer.select_microphone(device_id)
            print(f"\n選択されたマイク: {device_name}")
            return True
        else:
            print("\n無効な選択です。デフォルトのマイクを使用します。")
            return True
    except ValueError:
        print("\n無効な入力です。デフォルトのマイクを使用します。")
        return True

def test_microphone_and_recognition():
    """マイクと音声認識の基本機能テスト"""
    print("\n=== マイクと音声認識の基本機能テスト ===")
    print("このテストではマイクからの音声入力と音声認識の基本機能を確認します。")
    
    recognizer = SpeechRecognizer()
    
    # マイクの選択（オプション）
    print("\nマイクを選択しますか？ (y/n): ", end='')
    if input().lower() == 'y':
        select_microphone(recognizer)
    else:
        print("\nデフォルトのマイクを使用します。")
    
    recognition_event = threading.Event()
    recognition_result = None
    
    def handle_result(text: str):
        nonlocal recognition_result
        recognition_result = text
        recognition_event.set()
    
    try:
        print("\n手順1: マイクテスト")
        print("音声認識を開始します。「テスト」と話しかけてください。")
        print("10秒間の制限時間内に音声を認識できるか確認します。")
        print("\n準備ができたら Enter キーを押してください...")
        input()
        
        print("\n音声認識を開始します。「テスト」と話しかけてください...")
        recognizer.start_recognition(handle_result)
        
        # 10秒間待機
        recognition_success = recognition_event.wait(timeout=10.0)
        recognizer.stop_recognition()
        
        if recognition_success:
            print(f"\n✓ テスト成功: 音声を認識しました")
            print(f"認識されたテキスト: {recognition_result}")
        else:
            print("\n× テスト失敗: 音声を認識できませんでした")
            print("以下を確認してください：")
            print("- マイクが正しく接続されているか")
            print("- マイクが有効になっているか")
            print("- 音声入力レベルが適切か")
            print("\nもう一度試しますか？ (y/n): ", end='')
            retry = input().lower() == 'y'
            if retry:
                return test_microphone_and_recognition()
        
        return recognition_success
        
    except Exception as e:
        print(f"\n× テストエラー: {str(e)}")
        return False

def test_recognition_control():
    """音声認識の制御機能テスト"""
    print("\n=== 音声認識の制御機能テスト ===")
    print("このテストでは音声認識の開始/停止制御を確認します。")
    
    recognizer = SpeechRecognizer()
    results = []
    
    def handle_result(text: str):
        results.append(text)
    
    try:
        # テスト1: 開始と停止
        print("\n手順1: 音声認識の開始と停止")
        print("音声認識を開始します...")
        recognizer.start_recognition(handle_result)
        
        if recognizer.is_listening:
            print("✓ 音声認識が正常に開始されました")
        else:
            print("× 音声認識の開始に失敗しました")
            return False
        
        time.sleep(2)  # 動作確認のため少し待機
        
        print("\n音声認識を停止します...")
        recognizer.stop_recognition()
        
        if not recognizer.is_listening:
            print("✓ 音声認識が正常に停止されました")
        else:
            print("× 音声認識の停止に失敗しました")
            return False
        
        # テスト2: 多重開始の防止
        print("\n手順2: 多重開始の防止確認")
        print("音声認識を開始します（1回目）...")
        recognizer.start_recognition(handle_result)
        
        print("音声認識を開始します（2回目）...")
        recognizer.start_recognition(handle_result)
        
        if recognizer.is_listening:
            print("✓ 多重開始が正しく防止されました")
        else:
            print("× 多重開始の防止テストに失敗しました")
            return False
        
        # クリーンアップ
        recognizer.stop_recognition()
        return True
        
    except Exception as e:
        print(f"\n× テストエラー: {str(e)}")
        return False

def manual_test():
    """手動テストの実行"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("\n=== 音声認識テストプログラム ===")
    print("このプログラムでは音声認識システムの動作を確認します。")
    
    # ステップ1: マイクと音声認識の基本機能テスト
    if not test_microphone_and_recognition():
        print("\n基本機能テストに失敗しました。以降のテストをスキップします。")
        return
    
    # ステップ2: 音声認識の制御機能テスト
    if not test_recognition_control():
        print("\n制御機能テストに失敗しました。")
        return
    
    print("\n=== すべてのテストが完了しました ===")
    
    # 対話型テストの開始確認
    print("\n対話型テストを開始しますか？")
    print("このテストでは、実際のユースケースに基づいて音声認識を試すことができます。")
    response = input("開始する場合は 'y' を入力してください: ")
    
    if response.lower() == 'y':
        interactive_test()

def interactive_test():
    """対話型テスト"""
    print("\n=== 対話型テスト ===")
    print("以下のコマンドを音声で試してください：")
    print("- 「計測開始」または「測定開始」")
    print("- 「計測終了」または「測定終了」")
    print("- 「機種選択」")
    
    recognizer = SpeechRecognizer()
    
    def handle_result(text: str):
        print(f"\n認識されたテキスト: {text}")
        if "計測開始" in text or "測定開始" in text:
            print("→ 計測開始コマンドを認識しました")
        elif "計測終了" in text or "測定終了" in text:
            print("→ 計測終了コマンドを認識しました")
        elif "機種" in text:
            print("→ 機種選択コマンドを認識しました")
    
    try:
        print("\n音声認識を開始します。終了するには Enter キーを押してください。")
        recognizer.start_recognition(handle_result)
        input()
        recognizer.stop_recognition()
        print("\n対話型テストを終了します。")
        
    except KeyboardInterrupt:
        print("\n\nテストを中断します...")
        recognizer.stop_recognition()

if __name__ == "__main__":
    manual_test() 