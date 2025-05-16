"""
UIテストスクリプト
"""
import time
from ui_controller import UIController

def test_ui():
    """UIの動作テスト"""
    controller = UIController()
    
    # 3秒後に計測情報を更新
    def update_info():
        time.sleep(3)
        controller.update_measurement_info({
            "機種": "K57",
            "試験名": "牽引力試験",
            "試験条件": "前進速度3km/h",
            "計測者": "テスト太郎"
        })
    
    # 5秒後に録音開始
    def start_recording():
        time.sleep(5)
        controller.set_recording_state(True)
        controller.update_system_status("計測中")
    
    # 8秒後に録音停止
    def stop_recording():
        time.sleep(8)
        controller.set_recording_state(False)
        controller.update_system_status("計測完了")
    
    # テストの実行
    import threading
    threading.Thread(target=update_info).start()
    threading.Thread(target=start_recording).start()
    threading.Thread(target=stop_recording).start()
    
    # UIの開始
    controller.start()

if __name__ == "__main__":
    test_ui() 