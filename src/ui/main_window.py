"""
音声操作計測システムのメインウィンドウ
"""
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from typing import Optional, Dict, Any
import logging

class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self):
        """メインウィンドウの初期化"""
        # ウィンドウの基本設定
        self.root = ThemedTk(theme="arc")  # モダンなテーマを使用
        self.root.title("音声操作計測システム")
        self.root.geometry("800x600")
        
        # ステータス変数の初期化
        self.status_var = tk.StringVar(value="待機中")
        self.recording_status_var = tk.StringVar(value="音声認識: 停止")
        
        # スタイル設定
        self.style = ttk.Style()
        self._setup_styles()
        
        # UI要素の初期化
        self._init_ui()
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
    
    def _setup_styles(self):
        """スタイルの設定"""
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Status.TLabel", font=("Helvetica", 12))
        self.style.configure("Recording.TLabel", font=("Helvetica", 12), foreground="blue")
    
    def _init_ui(self):
        """UI要素の初期化"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # ヘッダー部分
        self._create_header()
        
        # 情報表示部分
        self._create_info_display()
        
        # ステータス表示部分
        self._create_status_display()
        
        # 操作ガイド部分
        self._create_operation_guide()
        
        # グリッド設定
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_header(self):
        """ヘッダー部分の作成"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # タイトル
        title_label = ttk.Label(
            header_frame, 
            text="音声操作計測システム", 
            style="Header.TLabel"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # ステータス
        status_label = ttk.Label(
            header_frame, 
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        status_label.grid(row=0, column=1, sticky="e", padx=(20, 0))
    
    def _create_info_display(self):
        """情報表示部分の作成"""
        info_frame = ttk.LabelFrame(self.main_frame, text="計測情報", padding="10")
        info_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # 情報グリッド
        self.info_vars = {
            "機種": tk.StringVar(),
            "試験名": tk.StringVar(),
            "試験条件": tk.StringVar(),
            "計測者": tk.StringVar()
        }
        
        for i, (label, var) in enumerate(self.info_vars.items()):
            ttk.Label(info_frame, text=f"{label}:").grid(
                row=i, column=0, sticky="w", pady=2
            )
            ttk.Label(info_frame, textvariable=var).grid(
                row=i, column=1, sticky="w", padx=(10, 0), pady=2
            )
    
    def _create_status_display(self):
        """ステータス表示部分の作成"""
        status_frame = ttk.LabelFrame(self.main_frame, text="状態", padding="10")
        status_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # 音声認識状態
        recording_label = ttk.Label(
            status_frame,
            textvariable=self.recording_status_var,
            style="Recording.TLabel"
        )
        recording_label.grid(row=0, column=0, sticky="w")
    
    def _create_operation_guide(self):
        """操作ガイド部分の作成"""
        guide_frame = ttk.LabelFrame(self.main_frame, text="操作ガイド", padding="10")
        guide_frame.grid(row=3, column=0, sticky="nsew")
        
        guide_text = """
        音声コマンド例：
        ・「計測開始」 - 計測を開始します
        ・「計測終了」 - 計測を終了します
        ・「機種選択 K57」 - 機種を選択します
        ・「試験選択 牽引力試験」 - 試験を選択します
        """
        guide_label = ttk.Label(guide_frame, text=guide_text, justify="left")
        guide_label.grid(row=0, column=0, sticky="w")
    
    def update_info(self, info_dict: Dict[str, Any]) -> None:
        """情報表示を更新する"""
        for key, value in info_dict.items():
            if key in self.info_vars:
                self.info_vars[key].set(str(value))
    
    def update_status(self, status: str) -> None:
        """状態表示を更新する"""
        self.status_var.set(status)
    
    def update_recording_status(self, is_recording: bool) -> None:
        """音声認識状態を更新する"""
        status = "音声認識: 実行中" if is_recording else "音声認識: 停止"
        self.recording_status_var.set(status)
    
    def run(self) -> None:
        """メインループの実行"""
        self.root.mainloop()
    
    def stop(self) -> None:
        """ウィンドウを閉じる"""
        self.root.quit() 