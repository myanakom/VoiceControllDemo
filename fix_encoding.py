import os

def fix_file_encoding(file_path):
    try:
        # ファイルの内容を読み込む
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # UTF-8でデコードしてから再エンコード
        text = content.decode('utf-8', errors='ignore')
        
        # 新しいファイルとして保存
        with open(file_path, 'w', encoding='utf-8', newline='\n') as file:
            file.write(text)
        
        print(f"ファイル {file_path} のエンコーディングを修正しました。")
        return True
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    file_path = "src/ui/manual_test.py"
    fix_file_encoding(file_path) 