# app.py
import os
import tkinter as tk

from core import (
    APP_BG,
    TEXT_FG,
    SUBTLE_FG,
    BLUE,
    FONT_TITLE,
    FONT_STATUS,
)
from config_page import ConfigPage
from start_point_page import StartPointPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------- WINDOW ICON ----------
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "brush.ico")

            print("Attempting to use icon:", icon_path)  # optional debug

            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                print("Icon file not found:", icon_path)
        except Exception as e:
            print("Could not set window icon:", e)

        # ---------- WINDOW SETUP ----------
        self.title("Ghost Brush")
        self.configure(bg=APP_BG)

        # Optional: initial size (used before zoom)
        self.geometry("1920x1000+0+0")
        self.minsize(900, 550)

        # 👉 Start maximized (not minimized)
        self.update_idletasks()
        self.state("zoomed")

        # Fullscreen handling
        self.is_fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # =========================
        # HEADER BAR
        # =========================
        self.header_frame = tk.Frame(self, bg=BLUE)
        self.header_frame.pack(fill="x", side="top")

        title_label = tk.Label(
            self.header_frame,
            text="Ghost Brush",
            font=FONT_TITLE,
            bg=BLUE,
            fg=TEXT_FG,
            anchor="w",
        )
        title_label.pack(fill="x", padx=15, pady=10)

        # =========================
        # SEPARATOR LINE
        # =========================
        self.header_sep = tk.Frame(self, bg="#333333", height=1)
        self.header_sep.pack(fill="x")

        # =========================
        # MAIN CONTENT CONTAINER
        # =========================
        self.main_container = tk.Frame(self, bg=APP_BG)
        self.main_container.pack(fill="both", expand=True, pady=(10, 0))

        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Shared state
        self.image_path = None
        self.img = None
        self.params = {}  # scale, step, threshold, delay
        self.img_width = 0
        self.img_height = 0

        # Create pages
        self.frames["config"] = ConfigPage(parent=self.main_container, controller=self)
        self.frames["start"] = StartPointPage(parent=self.main_container, controller=self)

        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        # =========================
        # BOTTOM STATUS BAR
        # =========================
        self.global_status_var = tk.StringVar(
            value="Tip: Press F11 to toggle fullscreen. Press Esc to exit fullscreen or cancel dialogs."
        )
        self.status_bar = tk.Label(
            self,
            textvariable=self.global_status_var,
            font=FONT_STATUS,
            bg=APP_BG,        # default for config page
            fg=SUBTLE_FG,
            anchor="w",
        )
        self.status_bar.pack(fill="x", side="bottom", pady=(5, 0), padx=2)

        # show first page
        self.show_frame("config")

    # -------------------------
    # PAGE CONTROL
    # -------------------------
    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

        if name == "start":
            # Hide header & separator, let main_container fill full height
            self.main_container.pack_forget()
            self.header_frame.pack_forget()
            self.header_sep.pack_forget()

            self.main_container.pack(fill="both", expand=True)

            # Match tip bar to the dark canvas background on start page
            self.status_bar.config(bg="#202020")
        else:
            # Show header & separator again
            self.main_container.pack_forget()
            self.header_frame.pack_forget()
            self.header_sep.pack_forget()

            self.header_frame.pack(fill="x", side="top")
            self.header_sep.pack(fill="x")
            self.main_container.pack(fill="both", expand=True, pady=(10, 0))

            # Back to normal app background on config page
            self.status_bar.config(bg=APP_BG)

    # -------------------------
    # FULLSCREEN CONTROL
    # -------------------------
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)
