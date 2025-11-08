# start_point_page.py
import tkinter as tk
from tkinter import messagebox
import threading

import pyautogui  # for FailSafeException

from core import (
    APP_BG,
    CARD_BG,
    TEXT_FG,
    draw_image_with_mouse,
    FONT_TITLE,
    FONT_LABEL,
    FONT_BUTTON,
    FONT_ENTRY,
    FONT_COUNTDOWN,
)


class StartPointPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure(bg=APP_BG)

        # =========================
        # MAIN CONTAINER
        # =========================
        main = tk.Frame(self, bg=CARD_BG)
        main.pack(fill="both", expand=True)

        # Preview canvas represents the whole usable screen area
        self.preview_canvas = tk.Canvas(main, bg="#1E1E1E", highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True)
        self.preview_canvas.bind("<Configure>", lambda e: self.draw_preview_rect())

        # =========================
        # CENTERED UI OVERLAY
        # =========================
        self.center_frame = tk.Frame(self.preview_canvas, bg=CARD_BG)
        self.center_frame.place(relx=0.5, rely=0.25, anchor="center")

        title = tk.Label(
            self.center_frame,
            text="Choose Start Point & Area",
            font=FONT_ENTRY,
            bg=CARD_BG,
            fg=TEXT_FG,
            anchor="center",
        )
        title.pack(pady=(0, 15))

        # Inputs row
        controls_frame = tk.Frame(self.center_frame, bg=CARD_BG)
        controls_frame.pack(pady=(0, 5))

        tk.Label(
            controls_frame,
            text="Start X:",
            font=FONT_ENTRY,
            bg=CARD_BG,
            fg=TEXT_FG,
        ).grid(row=0, column=0, sticky="e", padx=(0, 5), pady=0)

        self.start_x_var = tk.StringVar(value="200")
        entry_x = tk.Entry(
            controls_frame,
            textvariable=self.start_x_var,
            width=8,
            font=FONT_ENTRY,
            justify="center",
        )
        entry_x.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=5)

        tk.Label(
            controls_frame,
            text="Start Y:",
            font=FONT_ENTRY,
            bg=CARD_BG,
            fg=TEXT_FG,
        ).grid(row=0, column=2, sticky="e", padx=(0, 5), pady=0)

        self.start_y_var = tk.StringVar(value="200")
        entry_y = tk.Entry(
            controls_frame,
            textvariable=self.start_y_var,
            width=8,
            font=FONT_ENTRY,
            justify="center",
        )
        entry_y.grid(row=0, column=3, sticky="w", pady=5)

        # Buttons row (centered)
        buttons_frame = tk.Frame(self.center_frame, bg=CARD_BG)
        buttons_frame.pack(pady=(10, 0))

        btn_back = tk.Button(
            buttons_frame,
            text="⬅ Back",
            command=lambda: controller.show_frame("config"),
            font=FONT_ENTRY,
            padx=12,
            pady=4,
        )
        btn_back.pack(side="left", padx=10)

        self.btn_start = tk.Button(
            buttons_frame,
            text="Start Drawing",
            command=self.start_drawing,
            font=FONT_ENTRY,
            padx=18,
            pady=5,
        )
        self.btn_start.pack(side="left", padx=10)

        # Live update of the red box when user edits X/Y
        self.start_x_var.trace_add("write", lambda *args: self.draw_preview_rect())
        self.start_y_var.trace_add("write", lambda *args: self.draw_preview_rect())

    # Called from ConfigPage when image is ready
    def update_info(self):
        if self.controller.img_width and self.controller.img_height:
            self.draw_preview_rect()

    def draw_preview_rect(self):
        """
        Preview the drawing area as a red dotted rectangle.
        The entire canvas corresponds to the full screen:
        (0,0) screen -> top-left of this canvas.
        """
        canvas = self.preview_canvas
        canvas.delete("all")

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10:
            return  # canvas not ready yet

        screen_w = self.controller.winfo_screenwidth()
        screen_h = self.controller.winfo_screenheight()
        if screen_w == 0 or screen_h == 0:
            return

        # Map full screen to full canvas
        scale_x = cw / screen_w
        scale_y = ch / screen_h

        try:
            sx = int(self.start_x_var.get())
            sy = int(self.start_y_var.get())
            w = self.controller.img_width
            h = self.controller.img_height
            ex = sx + w
            ey = sy + h
        except Exception:
            return

        # Screen -> canvas coordinates
        rsx = sx * scale_x
        rsy = sy * scale_y
        rex = ex * scale_x
        rey = ey * scale_y

        canvas.create_rectangle(
            rsx,
            rsy,
            rex,
            rey,
            outline="red",
            dash=(6, 4),
            width=2,
        )

    # =========================
    # START DRAWING + COUNTDOWN
    # =========================
    def start_drawing(self):
        if self.controller.img is None:
            messagebox.showerror("No image", "Go back and select an image first.")
            return

        try:
            start_x = int(self.start_x_var.get())
            start_y = int(self.start_y_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Start X and Y must be integers.")
            return

        if not messagebox.askokcancel(
            "Confirm",
            "The UI will disappear and a countdown will start.\n"
            "When it reaches 0, drawing will begin.\n\n"
            "Move the mouse to the TOP-LEFT corner of the screen to ABORT.\n\n"
            "Continue?"
        ):
            return

        img = self.controller.img
        params = self.controller.params

        # Hide all UI elements (panel with title, inputs, buttons)
        self.center_frame.place_forget()

        # Start a 5-second countdown on the canvas
        self._run_countdown(
            seconds=5,
            img=img,
            start_x=start_x,
            start_y=start_y,
            params=params,
        )

    def _run_countdown(self, seconds, img, start_x, start_y, params):
        canvas = self.preview_canvas
        canvas.delete("all")

        cw = canvas.winfo_width() or 1
        ch = canvas.winfo_height() or 1

        if seconds > 0:
            canvas.create_text(
                cw / 2,
                ch / 2,
                text=f"Starting in {seconds}…",
                fill=TEXT_FG,
                font=FONT_COUNTDOWN,
            )
            # schedule next tick
            self.after(
                1000,
                self._run_countdown,
                seconds - 1,
                img,
                start_x,
                start_y,
                params,
            )
        else:
            # countdown finished: show "Drawing..." and start in background thread
            canvas.delete("all")
            canvas.create_text(
                cw / 2,
                ch / 2,
                text="Drawing…",
                fill=TEXT_FG,
                font=FONT_COUNTDOWN,
            )

            def worker():
                aborted = False
                try:
                    # perform the drawing (blocking) in a separate thread
                    draw_image_with_mouse(
                        img,
                        start_x,
                        start_y,
                        params["step"],
                        params["threshold"],
                        params["delay"],
                    )
                except pyautogui.FailSafeException:
                    # user hit the TOP-LEFT failsafe
                    aborted = True
                except Exception as e:
                    # any other unexpected error -> treat as aborted but keep app alive
                    print("Error while drawing:", e)
                    aborted = True
                finally:
                    # when done, update UI in main thread
                    self.after(0, lambda: self._on_drawing_done(aborted))

            threading.Thread(target=worker, daemon=True).start()

    def _on_drawing_done(self, aborted=False):
        """Called when the background drawing thread finishes or is aborted."""
        # Restore controls (back to StartPointPage UI)
        self.center_frame.place(relx=0.5, rely=0.25, anchor="center")
        # Redraw preview rectangle
        self.draw_preview_rect()

        # Status text in bottom bar
        if hasattr(self.controller, "global_status_var"):
            if aborted:
                self.controller.global_status_var.set(
                    "Drawing aborted (failsafe: mouse moved to top-left)."
                )
            else:
                self.controller.global_status_var.set("Done drawing.")
