"""
音声認識クライアントのテストモジュール

このモジュールでは、音声認識の基本機能をテストします。
以下の機能について検証を行います：
1. クライアントの初期化
2. マイクからの音声認識
3. 音声認識の停止

作成日: 2024-03-27
作成者: 開発チーム
"""

import sys
import os
from pathlib import Path
import time

# プロジェクトルートからの相対パスを設定
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

from voice_handler.speech_client import SpeechClient

def test_speech_client_initialization():
    """SpeechClientの初期化テスト"""
    try:
        client = SpeechClient()
        print("クライアント初期化テスト: 成功")
        assert client is not None
    except Exception as e:
        print(f"クライアント初期化テスト: 失敗 - {str(e)}")
        raise

def test_speech_recognition():
    """
    マイクからの音声認識テスト
    
    テスト手順:
    1. 音声認識を開始
    2. テスト用の音声を入力（手動）
    3. 認識結果を確認
    4. 音声認識を停止
    
    注意:
    - このテストは手動での音声入力が必要です
    - テスト実行前にマイクの設定を確認してください
    """
    client = SpeechClient()
    
    print("\n=== 音声認識テスト ===")
    print("3秒後に音声認識を開始します...")
    time.sleep(3)
    
    print("音声を入力してください（例：「テスト」）")
    result = client.start_recognition()
    
    print(f"認識結果: {result}")
    assert result != "", "音声認識に失敗しました"
    
    client.stop_recognition()
    print("音声認識テスト: 成功")

if __name__ == "__main__":
    print("音声認識クライアントのテストを開始します")
    test_speech_client_initialization()
    test_speech_recognition()
    print("\nすべてのテストが完了しました")