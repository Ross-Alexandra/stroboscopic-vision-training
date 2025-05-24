import time
import threading
import signal
import win32con
import win32gui
import win32api

class OverlayWindow:
    def __init__(self, displayCoverPeriod = 200, displayUncoverPeriod = 200):
        self.hideTime = displayCoverPeriod
        self.showTime = displayUncoverPeriod
    
        self.hInstance = win32api.GetModuleHandle()
        self.className = "StrobeOverlay"
        self.running = True

        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = self.wndProc
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = self.className
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        self.classAtom = win32gui.RegisterClass(wndClass)

        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)

        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT,
            self.className,
            None,
            win32con.WS_POPUP,
            0,
            0,
            self.screen_width,
            self.screen_height,
            None,
            None,
            self.hInstance,
            None
        )

        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0,
                              self.screen_width, self.screen_height,
                              win32con.SWP_SHOWWINDOW)

        # Start flashing
        threading.Thread(target=self.flash_loop, daemon=True).start()

    def flash_loop(self):
        while self.running:
            self.show_overlay(True)
            time.sleep(self.hideTime / 1000)
            self.show_overlay(False)
            time.sleep(self.showTime / 1000)

    def show_overlay(self, visible):
        hdc_screen = win32gui.GetDC(0)
        hdc_mem = win32gui.CreateCompatibleDC(hdc_screen)

        bmp = win32gui.CreateCompatibleBitmap(hdc_screen, self.screen_width, self.screen_height)
        win32gui.SelectObject(hdc_mem, bmp)

        brush = win32gui.CreateSolidBrush(win32api.RGB(0, 0, 0))  # white = transparent with alpha 0
        win32gui.FillRect(hdc_mem, (0, 0, self.screen_width, self.screen_height), brush)

        # Setup blend function for transparency
        blend = (win32con.AC_SRC_OVER, 0, 0, win32con.AC_SRC_ALPHA) if not visible else None
        win32gui.UpdateLayeredWindow(
            self.hwnd,
            hdc_screen,
            (0, 0),
            (self.screen_width, self.screen_height),
            hdc_mem,
            (0, 0),
            0,
            blend,
            win32con.ULW_ALPHA
        )

        win32gui.DeleteObject(bmp)
        win32gui.DeleteDC(hdc_mem)
        win32gui.ReleaseDC(0, hdc_screen)

    def wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_DESTROY:
            self.running = False
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def run(self):
        signal.signal(signal.SIGINT, lambda x, y: win32gui.PostQuitMessage(0))
        win32gui.PumpMessages()
