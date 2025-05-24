import win32gui
from strobe import OverlayWindow



if __name__ == "__main__":
    overlay = OverlayWindow(200, 1000)
    try:
        overlay.run()
    except KeyboardInterrupt:
        overlay.running = False
        win32gui.DestroyWindow(overlay.hwnd)
