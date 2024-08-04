import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class SymmetryApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.btn_load = tk.Button(window, text="画像を読み込む", width=20, command=self.load_image)
        self.btn_load.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_save = tk.Button(window, text="画像を保存", width=20, command=self.save_image)
        self.btn_save.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_switch = tk.Button(window, text="左右切り替え", width=20, command=self.switch_side)
        self.btn_switch.pack(side=tk.LEFT, padx=10, pady=10)

        self.symmetry_line = self.canvas_width // 2
        self.line = self.canvas.create_line(self.symmetry_line, 0, self.symmetry_line, self.canvas_height, fill="red", width=2)

        self.canvas.bind("<B1-Motion>", self.move_line)
        self.canvas.bind("<ButtonRelease-1>", self.update_symmetry)

        self.image = None
        self.symmetrical_image = None
        self.photo = None
        self.image_on_canvas = None
        self.start_from_left = True  # 左端からスタートするフラグ

        self.window.mainloop()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                pil_image = Image.open(file_path)
                self.image = np.array(pil_image)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
                self.image = self.resize_image(self.image)
                self.symmetry_line = self.canvas_width // 2
                self.update_symmetry()
            except Exception as e:
                print(f"画像の読み込みに失敗しました: {e}")

    def resize_image(self, image):
        h, w = image.shape[:2]
        aspect = w / h
        if aspect > self.canvas_width / self.canvas_height:
            new_w = self.canvas_width
            new_h = int(new_w / aspect)
        else:
            new_h = self.canvas_height
            new_w = int(new_h * aspect)
        resized = cv2.resize(image, (new_w, new_h))
        result = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        y_offset = (self.canvas_height - new_h) // 2
        x_offset = (self.canvas_width - new_w) // 2
        result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return result

    def update_symmetry(self, event=None):
        if self.image is not None:
            if self.start_from_left:
                left = self.image[:, :max(1, self.symmetry_line)]
                right = cv2.flip(left, 1)
            else:
                right = self.image[:, max(0, self.symmetry_line-1):]
                left = cv2.flip(right, 1)
            
            if left.shape[1] == 0:
                self.symmetrical_image = np.hstack((right, right))
            elif right.shape[1] == 0:
                self.symmetrical_image = np.hstack((left, left))
            else:
                self.symmetrical_image = np.hstack((left, right))
            
            self.show_image(self.symmetrical_image)
    
    def show_image(self, img):
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
        if self.image_on_canvas:
            self.canvas.delete(self.image_on_canvas)
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.update_line_position()

    def save_image(self):
        if self.symmetrical_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.symmetrical_image)

    def move_line(self, event):
        x = max(0, min(event.x, self.canvas_width))
        if self.start_from_left:
            self.symmetry_line = x
        else:
            self.symmetry_line = self.canvas_width - x
        self.update_line_position()
        if self.image is not None:
            self.update_symmetry()

    def update_line_position(self):
        line_position = self.symmetry_line if self.start_from_left else self.canvas_width - self.symmetry_line
        self.canvas.coords(self.line, line_position, 0, line_position, self.canvas_height)
        self.canvas.tag_raise(self.line)

    def switch_side(self):
        self.start_from_left = not self.start_from_left
        self.symmetry_line = self.canvas_width - self.symmetry_line
        if self.image is not None:
            self.update_symmetry()
        else:
            self.update_line_position()
            
SymmetryApp(tk.Tk(), "リアルタイムシンメトリー画像ジェネレーター")
