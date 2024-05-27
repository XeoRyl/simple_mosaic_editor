import os
import shelve
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw, ImageFont, ImageTk

import pillow_avif as _

_dummy = _


class ImageEditorBackend:
    def __init__(self, frontend):
        self.frontend = frontend
        self.root = frontend.root
        self.canvas = frontend.canvas
        self.control_frame = frontend.control_frame
        self.mosaic_strength = frontend.mosaic_strength
        self.mosaic_type = frontend.mosaic_type

        self.image = None
        self.original_image = None
        self.history = []
        self.file_path = None
        self.zoom_factor = 1.0
        self.trial_flg = True  # 体験版フラグを追加

        self.local_files_dir = 'localfiles'
        if not os.path.exists(self.local_files_dir):
            os.makedirs(self.local_files_dir)

        self.load_settings()

        # 画像ドラッグ用のデータ
        self.drag_data = {"x": 0, "y": 0, "item": None, "offset_x": 0, "offset_y": 0}
        self.rect = None  # 初期化

    def get_canvas_coords(self, x, y):
        return self.canvas.canvasx(x), self.canvas.canvasy(y)

    def get_setting(self, key, default):
        with shelve.open(os.path.join(self.local_files_dir, 'settings.db')) as settings:
            return settings.get(key, default)

    def save_setting(self, key, value):
        with shelve.open(os.path.join(self.local_files_dir, 'settings.db')) as settings:
            settings[key] = value

    def load_settings(self):
        self.mosaic_strength.set(self.get_setting('mosaic_strength', 5))

    def open_image(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.avif")])
        if self.file_path:
            self.image = Image.open(self.file_path)
            self.original_image = self.image.copy()
            self.reset_drag_data()  # 移動座標をリセット
            self.zoom_factor = 1.0  # 拡大率を初期化
            self.canvas.xview_moveto(0)  # 水平方向のスクロール位置をリセット
            self.canvas.yview_moveto(0)  # 垂直方向のスクロール位置をリセット
            self.drag_data["offset_x"] = 0  # offset_xを0にリセット
            self.drag_data["offset_y"] = 0  # offset_yを0にリセット
            self.display_image()
            self.adjust_window_size()

    def reset_drag_data(self):
        self.drag_data = {"x": 0, "y": 0, "item": None, "offset_x": 0, "offset_y": 0}

    def save_image(self):
        if self.original_image:
            base, ext = os.path.splitext(os.path.basename(self.file_path))
            default_file_name = f"{base}_mosaic{ext}"
            filetypes = [("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"),
                         ("BMP files", "*.bmp"), ("WEBP files", "*.webp"),
                         ("AVIF files", "*.avif")]

            defaultextension = ext
            initialdir = os.path.dirname(self.file_path)

            # 拡張子に基づいてデフォルトのファイルタイプを選択
            selected_filetype = None
            for filetype in filetypes:
                if defaultextension in filetype[1]:
                    selected_filetype = filetype
                    break

            if selected_filetype:
                # 選択されたファイルタイプをリストの先頭に移動
                filetypes.remove(selected_filetype)
                filetypes.insert(0, selected_filetype)

            # ファイルダイアログを開く
            file_path = filedialog.asksaveasfilename(defaultextension=defaultextension, initialfile=default_file_name,
                                                     filetypes=filetypes, initialdir=initialdir)
            if file_path:
                if self.trial_flg:
                    # 体験版の場合、透かしを追加
                    self.add_watermark()
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    self.original_image.convert('RGB').save(file_path)
                else:
                    self.original_image.save(file_path)

    def add_watermark(self):
        # 透かしを追加する関数
        width, height = self.original_image.size
        watermark_text = "Trial Version\n@maruo_bb"
        font_size = int(min(width, height) / 12)
        font = ImageFont.truetype("arial.ttf", font_size)
        draw = ImageDraw.Draw(self.original_image)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        # 背景の長方形を描画
        background_color = (0, 0, 0, 128)  # 半透明の黒
        padding = font_size // 4  # テキストの周囲のパディング
        background_bbox = (x - padding, y - padding, x + text_width + padding, y + text_height + padding)

        # 半透明の背景を描画するために、新しい画像を作成
        background = Image.new('RGBA', self.original_image.size, (0, 0, 0, 0))
        background_draw = ImageDraw.Draw(background)
        background_draw.rectangle(background_bbox, fill=background_color)

        # 元の画像と背景を合成
        self.original_image = Image.alpha_composite(self.original_image.convert('RGBA'), background)

        # 新しい描画コンテキストを取得
        draw = ImageDraw.Draw(self.original_image)

        # テキストを描画
        text_color = (255, 255, 255, 255)  # 白
        draw.text((x, y), watermark_text, font=font, fill=text_color)

    def display_image(self):
        if self.image:
            new_size = (int(self.image.width * self.zoom_factor), int(self.image.height * self.zoom_factor))
            self.display_image_zoom = self.image.resize(new_size, Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(self.display_image_zoom)
            if self.drag_data["item"]:
                self.canvas.delete(self.drag_data["item"])
            self.drag_data["item"] = self.canvas.create_image(self.drag_data["offset_x"], self.drag_data["offset_y"],
                                                              anchor=tk.NW, image=self.tk_image)

            # キャンバスのスクロール領域を画像のサイズに合わせて設定
            self.canvas.config(scrollregion=(0, 0, self.display_image_zoom.width, self.display_image_zoom.height))

    def adjust_window_size(self):
        if self.image:
            new_size = (int(self.image.width * self.zoom_factor), int(self.image.height * self.zoom_factor))
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # スクロールバーのサイズを取得
            self.root.update_idletasks()  # スクロールバーのサイズが正しく取得されるように
            scrollbar_width = self.frontend.vbar.winfo_width()
            scrollbar_height = self.frontend.hbar.winfo_height()

            window_width = min(new_size[0] + scrollbar_width, screen_width)
            window_height = min(new_size[1] + self.frontend.control_frame.winfo_height() + scrollbar_height,
                                screen_height)

            self.root.geometry(f"{window_width}x{window_height}")

    def zoom(self, event):
        if self.image:
            scale = 1.1 if event.delta > 0 else 0.9
            self.zoom_factor *= scale
            self.display_image()

    def on_button_press(self, event):
        if self.image:
            self.start_x, self.start_y = self.get_canvas_coords(event.x, event.y)
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                     outline='red')

    def on_mouse_drag(self, event):
        if self.rect:
            x, y = self.get_canvas_coords(event.x, event.y)
            self.canvas.coords(self.rect, self.start_x, self.start_y, x, y)

    def on_button_release(self, event):
        if self.rect:
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            if (x1 - x0) > 0 and (y1 - y0) > 0:  # 幅または高さが0の場合はスキップ
                self.apply_mosaic(x0, y0, x1, y1)
            self.canvas.delete(self.rect)
            self.rect = None

    def apply_mosaic(self, x0, y0, x1, y1):
        if self.image:
            self.history.append({
                "image": self.original_image.copy(),
                "offset_x": self.drag_data["offset_x"],
                "offset_y": self.drag_data["offset_y"]
            })
            # ズーム倍率を考慮して座標を変換
            actual_x0 = int((x0 - self.drag_data["offset_x"]) / self.zoom_factor)
            actual_y0 = int((y0 - self.drag_data["offset_y"]) / self.zoom_factor)
            actual_x1 = int((x1 - self.drag_data["offset_x"]) / self.zoom_factor)
            actual_y1 = int((y1 - self.drag_data["offset_y"]) / self.zoom_factor)

            cropped_area = (actual_x0, actual_y0, actual_x1, actual_y1)
            cropped_image = self.original_image.crop(cropped_area)
            if self.mosaic_type.get() == "mosaic":
                mosaic_size = max(1, 85 - self.mosaic_strength.get())
                if mosaic_size > 0 and cropped_image.size[0] > 0 and cropped_image.size[1] > 0:
                    mosaic_image = cropped_image.resize((mosaic_size, mosaic_size), Image.NEAREST).resize(
                        cropped_image.size, Image.NEAREST)
                    self.original_image.paste(mosaic_image, cropped_area)
            elif self.mosaic_type.get() == "black":
                black_image = Image.new("RGB", cropped_image.size, (0, 0, 0))
                self.original_image.paste(black_image, cropped_area)
            self.image = self.original_image.copy()
            self.display_image()

    def undo(self):
        if self.history:
            last_state = self.history.pop()
            self.original_image = last_state["image"]
            self.image = self.original_image.copy()
            self.drag_data["offset_x"] = last_state["offset_x"]
            self.drag_data["offset_y"] = last_state["offset_y"]
            self.display_image()
