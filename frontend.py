import os
import tkinter as tk
from tkinter import ttk

from ttkbootstrap import Style

from backend import ImageEditorBackend


class ImageEditorFrontend:
    def __init__(self, root):
        self.style = Style(theme='flatly')  # ダークテーマを元に戻す
        self.root = self.style.master

        app_name = "Simple Mosaic Editor"
        self.root.title(app_name)
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        self.root.iconbitmap(icon_path)

        # ウィンドウの最小サイズを指定
        self.root.minsize(400, 300)

        # メインフレームを作成してスクロールバーを追加
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, cursor="cross")
        self.hbar = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.root, padding=(10, 5))
        self.control_frame.pack(fill=tk.X)

        self.mosaic_strength_label = ttk.Label(self.control_frame, text="モザイクの強さ:")
        self.mosaic_strength_label.pack(side=tk.LEFT, padx=5)

        self.mosaic_strength = tk.IntVar()
        self.mosaic_strength_slider = ttk.Scale(self.control_frame, from_=5, to=80, orient=tk.HORIZONTAL,
                                                variable=self.mosaic_strength,
                                                command=self.update_mosaic_strength_label)
        self.mosaic_strength_slider.pack(side=tk.LEFT, padx=5)

        # モザイクの強さの値を表示するラベルを追加
        self.mosaic_strength_value_label = ttk.Label(self.control_frame, text=str(self.mosaic_strength.get()))
        self.mosaic_strength_value_label.pack(side=tk.LEFT, padx=5)

        self.mosaic_type = tk.StringVar(value="mosaic")
        self.mosaic_radio_mosaic = ttk.Radiobutton(self.control_frame, text="モザイク", variable=self.mosaic_type,
                                                   value="mosaic")
        self.mosaic_radio_black = ttk.Radiobutton(self.control_frame, text="黒塗り", variable=self.mosaic_type,
                                                  value="black")
        self.mosaic_radio_mosaic.pack(side=tk.LEFT, padx=5)
        self.mosaic_radio_black.pack(side=tk.LEFT, padx=5)

        self.backend = ImageEditorBackend(self)
        self.backend.trial_flg = True
        if self.backend.trial_flg:
            self.root.title(f"{app_name} Trial")

        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="開く", command=self.backend.open_image, accelerator="Ctrl+O")
        self.filemenu.add_command(label="保存", command=self.backend.save_image, accelerator="Ctrl+S")
        self.filemenu.add_command(label="リサイズ", command=self.resize_window_to_image,
                                  accelerator="Ctrl+R")  # リサイズコマンドにショートカットを追加
        self.filemenu.add_separator()
        self.filemenu.add_command(label="終了", command=self.root.quit, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="ファイル", menu=self.filemenu)

        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="元に戻す", command=self.backend.undo, accelerator="Ctrl+Z")
        self.menubar.add_cascade(label="編集", menu=self.editmenu)

        self.root.config(menu=self.menubar)

        self.canvas.bind("<ButtonPress-1>", self.backend.on_button_press)
        self.canvas.bind("<B1-Motion>", self.backend.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.backend.on_button_release)
        self.canvas.bind("<MouseWheel>", self.backend.zoom)

        self.root.bind("<Control-o>", lambda event: self.backend.open_image())
        self.root.bind("<Control-s>", lambda event: self.backend.save_image())
        self.root.bind("<Control-z>", lambda event: self.backend.undo())
        self.root.bind("<Control-q>", lambda event: self.root.quit())
        self.root.bind("<Control-r>", lambda event: self.resize_window_to_image())  # リサイズショートカットを追加

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 設定からモザイクの強度をロードし、ラベルを更新
        self.update_mosaic_strength_label()

    def update_mosaic_strength_label(self, event=None):
        self.mosaic_strength_value_label.config(text=str(self.mosaic_strength.get()))

    def on_closing(self):
        self.backend.save_setting('mosaic_strength', self.mosaic_strength.get())
        self.root.destroy()

    def resize_window_to_image(self):
        self.backend.adjust_window_size()


if __name__ == "__main__":
    root = tk.Tk()
    editor = ImageEditorFrontend(root)
    root.mainloop()
