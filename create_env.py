#!/usr/bin/env python
# -*- coding: utf-8 -*-

env_content = """# Azure Speech Service設定
AZURE_SPEECH_KEY=your_speech_key_here
AZURE_SPEECH_REGION=your_region_here

# アプリケーション設定
APP_DEBUG=False
DATA_DIR=src/data
VOICE_RECORDING_DIR=data/recordings
LOG_LEVEL=INFO

# 音声設定
SPEECH_LANGUAGE=ja-JP
SPEECH_RECOGNITION_TIMEOUT=5
VOICE_NAME=ja-JP-NanamiNeural  # Azure Neural Voice
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("環境変数設定ファイル(.env)を作成しました。") 