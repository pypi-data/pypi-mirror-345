import win32api
import win32con
import time as t

def clicker(newpos: bool, x: int, y: int, time: float, waittime: float, infinite: bool, times: int, action: int, scrolla: int):
    if action in [1, 2, 3]:  # Mouse buttons
        if action == 1:
            bt = win32con.MOUSEEVENTF_LEFTDOWN
            buttonup = win32con.MOUSEEVENTF_LEFTUP
        elif action == 2:
            bt = win32con.MOUSEEVENTF_RIGHTDOWN
            buttonup = win32con.MOUSEEVENTF_RIGHTUP
        elif action == 3:
            bt = win32con.MOUSEEVENTF_MIDDLEDOWN
            buttonup = win32con.MOUSEEVENTF_MIDDLEUP
    elif action in [4, 5]:  # Scroll up/down
        bt = win32con.MOUSEEVENTF_WHEEL
        scroll_amount = scrolla if action == 4 else -scrolla
    else:  # Assume it's a key press (virtual key code)
        bt = None

    if newpos:
        if infinite:
            while True:
                win32api.SetCursorPos((x, y))
                if action in [4, 5]:  # Handle scroll
                    win32api.mouse_event(bt, 0, 0, scroll_amount, 0)
                elif action in [1, 2, 3]:  # Handle mouse click
                    win32api.mouse_event(bt, x, y, 0, 0)
                    t.sleep(time)
                    win32api.mouse_event(buttonup, x, y, 0, 0)
                else:  # Handle key press
                    win32api.keybd_event(action, 0, 0, 0)  # Key down
                    t.sleep(0.05)
                    win32api.keybd_event(action, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                t.sleep(waittime)
        else:
            for i in range(times):
                win32api.SetCursorPos((x, y))
                if action in [4, 5]:  # Handle scroll
                    win32api.mouse_event(bt, 0, 0, scroll_amount, 0)
                elif action in [1, 2, 3]:  # Handle mouse click
                    win32api.mouse_event(bt, x, y, 0, 0)
                    t.sleep(time)
                    win32api.mouse_event(buttonup, x, y, 0, 0)
                else:  # Handle key press
                    win32api.keybd_event(action, 0, 0, 0)  # Key down
                    t.sleep(0.05)
                    win32api.keybd_event(action, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                t.sleep(waittime)
    else:
        if infinite:
            while True:
                xn, yn = win32api.GetCursorPos()
                if action in [4, 5]:  # Handle scroll
                    win32api.mouse_event(bt, 0, 0, scroll_amount, 0)
                elif action in [1, 2, 3]:  # Handle mouse click
                    win32api.mouse_event(bt, xn, yn, 0, 0)
                    t.sleep(time)
                    win32api.mouse_event(buttonup, xn, yn, 0, 0)
                else:  # Handle key press
                    win32api.keybd_event(action, 0, 0, 0)  # Key down
                    t.sleep(0.05)
                    win32api.keybd_event(action, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                t.sleep(waittime)
        else:
            for i in range(times):
                xn, yn = win32api.GetCursorPos()
                if action in [4, 5]:  # Handle scroll
                    win32api.mouse_event(bt, 0, 0, scroll_amount, 0)
                elif action in [1, 2, 3]:  # Handle mouse click
                    win32api.mouse_event(bt, xn, yn, 0, 0)
                    t.sleep(time)
                    win32api.mouse_event(buttonup, xn, yn, 0, 0)
                else:  # Handle key press
                    win32api.keybd_event(action, 0, 0, 0)  # Key down
                    t.sleep(0.05)
                    win32api.keybd_event(action, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                t.sleep(waittime)
               