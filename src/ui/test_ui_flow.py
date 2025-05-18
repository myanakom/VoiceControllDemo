import time
import threading
from src.ui.ui_controller import UIController

def test_ui():
    controller = UIController()
    def update():
        time.sleep(2)
        # ユーザー入力（ダミー）
        user_input_machine = "K57"
        user_input_test = "牽引力試験"
        user_input_condition = "前進速度3km/h"
        user_input_operator = "テスト太郎"
        # 計測情報をユーザー入力から更新
        controller.update_measurement_info({
            "機種": user_input_machine,
            "試験名": user_input_test,
            "試験条件": user_input_condition,
            "計測者": user_input_operator
        })
        controller.update_system_status("計測名リストと新規計測の選択肢を提示")
        time.sleep(2)
        # 以降もユーザー入力を使って必要に応じて更新可能
        controller.update_system_status("計測項目リストを提示")
        time.sleep(2)
        controller.update_system_status("計測条件を受け付け")
        time.sleep(2)
        controller.update_system_status("機種名を受け付け")
        time.sleep(2)
        controller.update_system_status("計測開始")
        time.sleep(2)
        controller.update_system_status("計測終了とダミーデータ保存")
    threading.Thread(target=update).start()
    controller.start()

if __name__ == "__main__":
    test_ui()
    