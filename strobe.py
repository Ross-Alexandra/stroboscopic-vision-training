import time
import threading
import win32con
import win32gui
import win32api
import keyboard
class OverlayWindow:
    def __init__(self, displayCoverPeriod = 200, displayUncoverPeriod = 200):
        self.hide_time = displayCoverPeriod
        self.show_time = displayUncoverPeriod
    
        self.hInstance = win32api.GetModuleHandle()
        self.className = "StrobeOverlay"
        self.running = True
        self.resumed = True

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

        # Start various background processes
        print('Please press CTRL+q to stop the strobing, or CTRL+p to pause the strobing')
        threading.Thread(target=self.flash_loop, daemon=True).start()
        threading.Thread(target=self.detect_stop_loop, daemon=True).start()
        threading.Thread(target=self.pause_loop, daemon=True).start()
        threading.Thread(target=self.quit_loop, daemon=True).start()

    def flash_loop(self):
        while self.running:
            while self.resumed:
                self.show_overlay(True)
                time.sleep(self.hide_time / 1000)
                self.show_overlay(False)
                time.sleep(self.show_time / 1000)

            time.sleep(.2)
 
    def detect_stop_loop(self):
        while self.running:
            time.sleep(1)
        
        print('Detected that running has stopped. Killing event loop.')
        win32api.PostMessage(self.hwnd, win32con.WM_DESTROY, 0, 0)
         
    def quit_loop(self):
        keyboard.wait('ctrl+q')
        self.running = False
 
    def pause_loop(self):
        while self.running:
            keyboard.wait('ctrl+p')
            self.resumed = not self.resumed
 
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
        win32gui.PumpMessages()
