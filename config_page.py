# config_page.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from core import (
    APP_BG,
    CARD_BG,
    TEXT_FG,
    SUBTLE_FG,
    load_and_prepare_image,
    FONT_TITLE,
    FONT_LABEL,
    FONT_BUTTON,
    FONT_ENTRY,
)


class ConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=APP_BG)

        self.preview_img = None
        self.original_img = None   # keep original so we can resize nicely
        self.is_hover = False

        # --- Appearance constants ---
        self.DEFAULT_BG = "#252526"  # default drop area background
        self.HOVER_BG = "#3a3a3a"    # hover drop area background
        self.DROP_BOX_WIDTH = 1200   # drop area width (None for full width)
        self.DROP_BOX_HEIGHT = 800   # drop area height
        self.PARAM_WIDTH = 800       # target width of "Drawing parameters" section

        # =========================
        # MAIN CONTAINER
        # =========================
        main = tk.Frame(self, bg=CARD_BG)
        main.pack(fill="both", expand=True, padx=60, pady=40)
        for c in range(4):
            main.columnconfigure(c, weight=1)

        # --- TITLE ---
        title = tk.Label(
            main,
            text="Choose Image & Configuration",
            font=FONT_TITLE,
            bg=CARD_BG,
            fg=TEXT_FG,
            anchor="center",
        )
        title.grid(row=0, column=0, columnspan=4, pady=(10, 30), sticky="ew")

        # =========================
        # IMAGE DROP AREA
        # =========================
        self.image_canvas = tk.Canvas(
            main,
            bg=self.DEFAULT_BG,
            highlightthickness=0,
            cursor="hand2",
            height=self.DROP_BOX_HEIGHT,
            width=self.DROP_BOX_WIDTH if self.DROP_BOX_WIDTH else 1,
        )

        if self.DROP_BOX_WIDTH:
            self.image_canvas.grid(row=1, column=0, columnspan=4, pady=(0, 50))
        else:
            self.image_canvas.grid(
                row=1, column=0, columnspan=4, pady=(0, 50), sticky="nsew"
            )

        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # Hover & resize bindings
        self.image_canvas.bind("<Configure>", lambda e: self.redraw_canvas())
        self.image_canvas.bind("<Button-1>", lambda e: self.choose_image())
        self.image_canvas.bind("<Enter>", self.on_hover_enter)
        self.image_canvas.bind("<Leave>", self.on_hover_leave)

        # =========================
        # PARAMETERS SECTION
        # =========================
        params_container = tk.Frame(main, bg=CARD_BG)
        params_container.grid(row=2, column=0, columnspan=4, pady=(20, 60))

        params_frame = tk.LabelFrame(
            params_container,
            text=" Drawing parameters ",
            font=FONT_LABEL,
            bg=CARD_BG,
            fg=TEXT_FG,
            bd=1,
            relief="groove",
            labelanchor="nw",
        )
        params_frame.pack()

        row = tk.Frame(params_frame, bg=CARD_BG)
        row.pack(fill="x", expand=True, padx=40, pady=15)

        def add_param(label_text, var, width=10):
            frame = tk.Frame(row, bg=CARD_BG)
            frame.pack(side="left", expand=True)
            tk.Label(
                frame,
                text=label_text,
                font=FONT_LABEL,
                bg=CARD_BG,
                fg=TEXT_FG,
            ).pack(anchor="center", pady=(0, 3))
            tk.Entry(
                frame,
                textvariable=var,
                width=width,
                font=FONT_ENTRY,
                justify="center",
            ).pack(anchor="center")

        # Variables
        self.scale_var = tk.StringVar(value="0.25")
        self.step_var = tk.StringVar(value="2")
        self.threshold_var = tk.StringVar(value="200")
        self.delay_var = tk.StringVar(value="0")

        add_param("Scale:", self.scale_var)
        add_param("Step:", self.step_var)
        add_param("Threshold:", self.threshold_var)
        add_param("Draw delay (s):", self.delay_var)

        # Freeze params_frame width to PARAM_WIDTH
        params_frame.update_idletasks()
        natural_height = params_frame.winfo_reqheight()
        params_frame.config(width=self.PARAM_WIDTH, height=natural_height)
        params_frame.pack_propagate(False)

        # =========================
        # NEXT BUTTON
        # =========================
        btn_next = tk.Button(
            main,
            text="Next",
            command=self.on_next,
            font=FONT_BUTTON,
            padx=20,
            pady=8,
        )
        btn_next.grid(row=3, column=0, columnspan=4, pady=(0, 20))

    # ===============================================================
    # HOVER BEHAVIOR
    # ===============================================================
    def on_hover_enter(self, event):
        self.is_hover = True
        self.redraw_canvas()

    def on_hover_leave(self, event):
        self.is_hover = False
        self.redraw_canvas()

    # ===============================================================
    # CANVAS DRAWING
    # ===============================================================
    def redraw_canvas(self):
        canvas = self.image_canvas
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w <= 10 or h <= 10:
            return

        canvas.delete("all")

        margin = 1  # small inset so the border isn't clipped
        border_color = SUBTLE_FG
        fill_color = self.HOVER_BG if self.is_hover else self.DEFAULT_BG

        # Fill the whole drop area
        canvas.create_rectangle(0, 0, w, h, fill=fill_color, outline="")

        # Dotted border almost at the edge
        canvas.create_rectangle(
            margin,
            margin,
            w - margin,
            h - margin,
            outline=border_color,
            dash=(6, 5),
            width=2,
        )

        # Content
        if not self.preview_img:
            canvas.create_text(
                w / 2,
                h / 2,
                text="Browse image…",
                fill=TEXT_FG,
                font=FONT_LABEL,
            )
        else:
            canvas.create_image(w / 2, h / 2, image=self.preview_img)

    # ===============================================================
    # IMAGE SELECTION & PREVIEW
    # ===============================================================
        # ===============================================================
    # IMAGE SELECTION & PREVIEW
    # ===============================================================
    def choose_image(self):
        # choose a safe initial directory
        # try Pictures, fall back to home folder
        initial_dir = os.path.expanduser("~/Pictures")
        if not os.path.isdir(initial_dir):
            initial_dir = os.path.expanduser("~")

        path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        self.controller.image_path = path

        # Load the original image once
        self.original_img = Image.open(path)

        # Use current canvas size (or fallback if not yet realized)
        w = self.image_canvas.winfo_width()
        h = self.image_canvas.winfo_height()
        if w <= 0 or h <= 0:
            w, h = self.DROP_BOX_WIDTH or 800, self.DROP_BOX_HEIGHT

        margin = 1
        inner_w = w - 2 * margin - 4   # little padding so it doesn't touch border
        inner_h = h - 2 * margin - 4

        # Copy and fit image INTO that inner box, preserving aspect ratio
        img = self.original_img.copy()
        img.thumbnail((inner_w, inner_h), Image.LANCZOS)

        # Save preview
        self.preview_img = ImageTk.PhotoImage(img)
        self.redraw_canvas()

    # ===============================================================
    # NEXT BUTTON HANDLER
    # ===============================================================
    def on_next(self):
        if not self.controller.image_path:
            messagebox.showwarning("No image", "Please choose an image first.")
            return

        try:
            scale = float(self.scale_var.get())
            step = int(self.step_var.get())
            threshold = int(self.threshold_var.get())
            delay = float(self.delay_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please check your numeric parameters.")
            return

        if scale <= 0:
            messagebox.showerror("Invalid scale", "Scale must be greater than 0.")
            return
        if step <= 0:
            messagebox.showerror("Invalid step", "Step must be positive.")
            return
        if not (0 <= threshold <= 255):
            messagebox.showerror(
                "Invalid threshold", "Threshold must be between 0 and 255."
            )
            return
        if delay < 0:
            messagebox.showerror("Invalid delay", "Delay cannot be negative.")
            return

        try:
            img = load_and_prepare_image(self.controller.image_path, scale)
        except Exception as e:
            messagebox.showerror("Error loading image", str(e))
            return

        self.controller.img = img
        self.controller.img_width, self.controller.img_height = img.size
        self.controller.params = {
            "scale": scale,
            "step": step,
            "threshold": threshold,
            "delay": delay,
        }

        self.controller.frames["start"].update_info()
        self.controller.show_frame("start")
