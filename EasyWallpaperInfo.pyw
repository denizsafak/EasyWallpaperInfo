import os
from sys import exit
import subprocess
import tkinter as tk
from tkinter import messagebox
from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
from PIL import Image
import time
import ctypes
import json
with open("config.json", "r") as f:
    config = json.load(f)
bottom_margin = config["bottom_margin"]
min_width = config["min_width"]
alpha = config["alpha"]
indicator_update_frequency = config["indicator_update_frequency"]
text_size = config["text_size"]
text_font = config["text_font"]
text_color = config["text_color"]
background_color = config["background_color"]
show_title = config["show_title"]
show_size = config["show_size"]
show_resolution = config["show_resolution"]
show_location = config["show_location"]
display_mouse_tips = config["display_mouse_tips"]
always_on_top = config["always_on_top"]
mutex = ctypes.windll.kernel32.CreateMutexW(None, 1, "Global\\EasyWallpaperInfoMutex")
if ctypes.windll.kernel32.GetLastError() == 183:
    ctypes.windll.kernel32.CloseHandle(mutex)
    messagebox.showwarning("Warning", "The program is already running. If you can't see the program, right click on your desktop.")
    exit()
def get_wallpaper_info():
    reg = ConnectRegistry(None, HKEY_CURRENT_USER)
    key = OpenKey(reg, r"Control Panel\Desktop")
    value, _ = QueryValueEx(key, "TranscodedImageCache")
    wallpaper_path = value[24:].decode('utf-16-le').rstrip('\x00')
    filename = os.path.basename(wallpaper_path)
    size = os.path.getsize(wallpaper_path)
    location = wallpaper_path
    img = Image.open(wallpaper_path)
    resolution = f"{img.width}x{img.height}"
    exif_data = img._getexif()
    try:
        exif_data.get(270)
        title = exif_data.get(270)
    except AttributeError:
        title = None
    if title:
        title = title.encode('latin-1').decode('utf-8')
    if size < 1024:
        size = f"{size} bytes"
    elif size < 1048576:
        size = f"{round(size / 1024, 2)} KB"
    elif size < 1073741824:
        size = f"{round(size / 1048576, 2)} MB"
    else:
        size = f"{round(size / 1073741824, 2)} GB"
    return title, size, resolution, location
def exit_application():
    indicator.destroy()
    os._exit(0)
def open_wallpaper_location():
    title, _, _, location = get_wallpaper_info()
    subprocess.Popen(['explorer', '/select,', location])
def open_wallpaper():
    title, _, _, location = get_wallpaper_info()
    subprocess.Popen(['start', '', location], shell=True)
def copy_title_text():
    title, _, _, _ = get_wallpaper_info()
    indicator.clipboard_clear()
    indicator.clipboard_append(title)
    indicator.update()
def show_menu(event):
    menu.post(event.x_root, event.y_root)
def on_left_click(event):
    label.config(cursor="arrow")
def on_right_click(event):
    show_menu(event)
def reset_cursor(event):
    label.after(10, lambda: label.config(cursor="hand2"))
    subprocess.call("NextBackground.exe")
    update_label()
def display_message(message):
    indicator.attributes("-alpha", 1)
    label.config(text=message, font=(text_font, 14))
    indicator.attributes("-topmost", True)
    indicator.update()
    time.sleep(5)
    label.config(text=details)
    label.config(font=(text_font, text_size))
    indicator.attributes("-alpha", alpha)
    indicator.attributes("-topmost", False)
    indicator.update()
def update_label():
    title, size, resolution, location = get_wallpaper_info()
    details = ""
    if show_title:
        details += f"Title: {title}\n"
    if show_size:
        details += f"Filesize: {size}\n"
    if show_resolution:
        details += f"Resolution: {resolution}\n"
    if show_location:
        details += f"Location: {location}\n"
    details = details[:-1]
    label.config(text=details)
    indicator.after(indicator_update_frequency, update_label)
if __name__ == "__main__":
    indicator = tk.Tk()
    indicator.title("Easy Wallpaper Info")
    indicator.geometry("+{}+{}".format(0, indicator.winfo_screenheight() - bottom_margin))
    indicator.overrideredirect(True)
    indicator.minsize(min_width, 0)
    indicator.maxsize(indicator.winfo_screenwidth(), 0)
    indicator.attributes("-alpha", alpha)
    if always_on_top:
        indicator.attributes("-topmost", True)
    title, size, resolution, location = get_wallpaper_info()
    details = ""
    if show_title:
        details += f"Title: {title}\n"
    if show_size:
        details += f"Filesize: {size}\n"
    if show_resolution:
        details += f"Resolution: {resolution}\n"
    if show_location:
        details += f"Location: {location}\n"
    details = details[:-1]
    label = tk.Label(indicator, text=details, font=(text_font, text_size), bg=background_color, fg=text_color, anchor="w", justify="left")
    label.pack(expand=True, fill='both')
    label.config(cursor="hand2")
    label.bind("<Button-1>", on_left_click)
    label.bind("<Button-3>", on_right_click)
    label.bind("<ButtonRelease-1>", reset_cursor)
    menu = tk.Menu(indicator, tearoff=0)
    menu.add_command(label="Open wallpaper", command=open_wallpaper)
    menu.add_command(label="Go to wallpaper location", command=open_wallpaper_location)
    menu.add_command(label="Copy title text", command=copy_title_text)
    menu.add_command(label="Exit", command=exit_application)
    if display_mouse_tips:
        display_message("Hover here, \nLeft Click: Next Wallpaper\nRight Click: Menu")
    update_label()
    indicator.mainloop()
    ctypes.windll.kernel32.CloseHandle(mutex)
