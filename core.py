# core.py
import time
from PIL import Image
import pyautogui

# =======================
# STYLE CONSTANTS
# =======================

APP_BG = "#1e1e1e"
CARD_BG = "#252526"
TEXT_FG = "#ffffff"
SUBTLE_FG = "#bbbbbb"
ACCENT_FG = "#3fa9f5"

BLUE = "#0065a8"

# =======================
# GLOBAL FONT SETTINGS
# =======================

# Change this single line to swap fonts app-wide
FONT_FAMILY = "Snowstorm"

FONT_TITLE     = (FONT_FAMILY, 25, "bold")
FONT_LABEL     = (FONT_FAMILY, 20)
FONT_BUTTON    = (FONT_FAMILY, 16, "bold")
FONT_ENTRY     = (FONT_FAMILY, 15)
FONT_STATUS    = (FONT_FAMILY, 20)
FONT_COUNTDOWN = (FONT_FAMILY, 100, "bold")


# =======================
# CORE DRAWING LOGIC
# =======================

def load_and_prepare_image(path, scale: float) -> Image.Image:
    """Load an image, convert to grayscale and scale it."""
    img = Image.open(path).convert("L")

    w, h = img.size
    new_w = int(w * scale)
    new_h = int(h * scale)
    img = img.resize((new_w, new_h))

    print(f"Original size: {w}x{h}, resized to: {new_w}x{new_h}")
    return img


def draw_image_with_mouse(img: Image.Image,
                          start_x: int,
                          start_y: int,
                          step: int,
                          threshold: int,
                          delay: float) -> None:
    """Use pyautogui to 'draw' the grayscale image on the screen."""
    pixels = img.load()
    width, height = img.size

    # Safety: allow moving mouse to top-left corner to abort
    pyautogui.FAILSAFE = True
    # Extra speed: remove global pause between actions
    pyautogui.PAUSE = 0

    print("Starting drawing... Move mouse to TOP-LEFT corner of the screen to ABORT.")

    for y in range(0, height, step):
        drawing = False  # are we currently holding the mouse button?

        for x in range(0, width, step):
            brightness = pixels[x, y]  # 0 = black, 255 = white
            screen_x = start_x + x
            screen_y = start_y + y

            if brightness < threshold:
                # dark pixel -> we should be drawing
                if not drawing:
                    pyautogui.moveTo(screen_x, screen_y)
                    pyautogui.mouseDown()
                    drawing = True
                else:
                    pyautogui.moveTo(screen_x, screen_y)
            else:
                # bright pixel -> we should stop drawing if we were
                if drawing:
                    pyautogui.mouseUp()
                    drawing = False

            if delay > 0:
                time.sleep(delay)

        # at end of row, make sure we release the mouse if still drawing
        if drawing:
            pyautogui.mouseUp()
            drawing = False

    print("Done!")
