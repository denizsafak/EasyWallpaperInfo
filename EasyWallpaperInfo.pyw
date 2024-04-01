import os
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser
from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
from PIL import Image
from ahk import AHK
import ctypes
import json
Image.MAX_IMAGE_PIXELS = None
with open("config.json", "r") as f:
    config = json.load(f)
version = "v1.5"
github_link = "https://github.com/denizsafak/EasyWallpaperInfo"
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
position = config["position"]
text_align = config["text_align"]
title_as_filename = config["title_as_filename"]
mutex = ctypes.windll.kernel32.CreateMutexW(None, 1, "Global\\EasyWallpaperInfoMutex")
if ctypes.windll.kernel32.GetLastError() == 183:
    ctypes.windll.kernel32.CloseHandle(mutex)
    messagebox.showwarning("Warning", "The program is already running. If you can't see the program, right click on your desktop.")
    os._exit(0)
ahk = AHK(version='v2')
next_wallpaper_trigger = '''\
#NoTrayIcon
try if ((pDesktopWallpaper := ComObject("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}", "{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}"))) {
        ComCall(16, pDesktopWallpaper, "Ptr", 0, "UInt", 0) 
        ObjRelease(pDesktopWallpaper)
}
'''
def get_wallpaper_path():
    try:
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(reg, r"Control Panel\Desktop")
        value, _ = QueryValueEx(key, "TranscodedImageCache")
        wallpaper_path = value[24:].decode('utf-16-le').rstrip('\x00')
        return wallpaper_path
    except FileNotFoundError:
        messagebox.showwarning("Warning", "Couldn't find wallpaper path. Make sure you have set a wallpaper.")
        os._exit(0)
    finally:
        key.Close()
        reg.Close()
def get_image_size(image_path):
    size = os.path.getsize(image_path)
    if size < 1024:
        size_str = f"{size} bytes"
    elif size < 1048576:
        size_str = f"{round(size / 1024, 2)} KB"
    elif size < 1073741824:
        size_str = f"{round(size / 1048576, 2)} MB"
    else:
        size_str = f"{round(size / 1073741824, 2)} GB"
    return size_str
def get_image_resolution(image_path):
    try:
        img = Image.open(image_path)
    finally:
        img.close()
    resolution = f"{img.width}x{img.height}"
    return resolution
def get_image_title(image_path):
    try:
        img = Image.open(image_path)
    finally:
        img.close()
    if config["title_as_filename"]:
        title = os.path.basename(image_path)
        title = os.path.splitext(title)[0]
    else:
        exif_data = img._getexif()
        try:
            title = exif_data.get(270)
            if title:
                title = title.encode('latin-1').decode('utf-8')
            else:
                title = None
        except AttributeError:
            title = None
    return title
def exit_application():
    indicator.destroy()
    os._exit(0)
def open_wallpaper_location():
    location = get_wallpaper_path()
    subprocess.Popen(['explorer', '/select,', location])
def open_wallpaper():
    location = get_wallpaper_path()
    subprocess.Popen(['start', '', location], shell=True)
def copy_title_text():
    wallpaper_path = get_wallpaper_path()
    title = get_image_title(wallpaper_path)
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
    # label.after(3, lambda: label.config(cursor="hand2"))
    ahk.run_script(next_wallpaper_trigger)
    # label.config(cursor="wait")
previous_details = ""
def update_label():
    global previous_details
    details = ""
    wallpaper_path = get_wallpaper_path()
    if config["show_title"]:
        title = get_image_title(wallpaper_path)
        details += f"Title: {title}\n"
    if config["show_size"]:
        size = get_image_size(wallpaper_path)
        details += f"Filesize: {size}\n"
    if config["show_resolution"]:
        resolution = get_image_resolution(wallpaper_path)
        details += f"Resolution: {resolution}\n"
    if config["show_location"]:
        details += f"Location: {wallpaper_path}\n"
    details = details[:-1]
    if details != previous_details:
        label.config(cursor="hand2")
        previous_details = details
        label.config(text=details)
    indicator.after(indicator_update_frequency, update_label)
def display_message(message):
    background_color = config["background_color"]
    text_color = config["text_color"]
    msg_window = tk.Tk()
    msg_window.title("Message")
    msg_window.overrideredirect(True)
    msg_window.attributes("-topmost", True)
    screen_width = msg_window.winfo_screenwidth()
    screen_height = msg_window.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 100) // 2
    msg_window.geometry(f"300x100+{x}+{y}")
    label2 = tk.Label(msg_window, text=message, font=(text_font, 14), bg=background_color, fg=text_color)
    label2.pack(expand=True, fill='both')
    msg_window.after(5000, msg_window.destroy)
    msg_window.mainloop()
def set_indicator_position(position):
    global indicator
    if position == "center":
        x = (indicator.winfo_screenwidth() - indicator.winfo_width()) // 2
        y = (indicator.winfo_screenheight() - indicator.winfo_height()) // 2
    elif position == "top_center":
        x = (indicator.winfo_screenwidth() - indicator.winfo_width()) // 2
        y = 0
    elif position == "bottom_center":
        x = (indicator.winfo_screenwidth() - indicator.winfo_width()) // 2
        y = indicator.winfo_screenheight() - config["bottom_margin"]  # Adjust based on bottom_margin
    elif position == "top_left":
        x, y = 0, 0
    elif position == "top_right":
        x = indicator.winfo_screenwidth() - indicator.winfo_width()
        y = 0
    elif position == "bottom_left":
        x, y = 0, indicator.winfo_screenheight() - config["bottom_margin"]  # Adjust based on bottom_margin
    elif position == "bottom_right":
        x = indicator.winfo_screenwidth() - indicator.winfo_width()
        y = indicator.winfo_screenheight() - config["bottom_margin"]  # Adjust based on bottom_margin
    else:
        messagebox.showwarning("Warning", "Invalid position value in config.json")
        os._exit(0)
    indicator.geometry("+{}+{}".format(x, y))
    config["position"] = position
def change_position(position, check_var):
    set_indicator_position(position)
    check_var.set(1)
    for other_position, other_var in position_vars.items():
        if other_position != position:
            other_var.set(0)
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
def update_label_text_align():
    if config["text_align"] == "center":
        anchor = "center"
    elif config["text_align"] == "left":
        anchor = "w"
    elif config["text_align"] == "right":
        anchor = "e"
    else:
        messagebox.showwarning("Warning", "Invalid text_align value in config.json")
        os._exit(0)
    label.config(anchor=anchor, justify=config["text_align"])
def change_text_align(align, check_var):
    check_var.set(1)
    for other_align, other_var in text_align_vars.items():
        if other_align != align:
            other_var.set(0)
    config["text_align"] = align
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label_text_align()
def change_bottom_margin():
    current_margin = config["bottom_margin"]
    new_margin = simpledialog.askinteger("Change Bottom Margin", "Enter the new bottom margin value:", initialvalue=current_margin)
    if new_margin is not None:
        config["bottom_margin"] = new_margin
        set_indicator_position(config["position"])  # Update position
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def change_background_color():
    # Open a color picker dialog with the current background color as default
    color = colorchooser.askcolor(title="Choose Background Color", initialcolor=config["background_color"])
    if color[1]:  # Check if a color was selected
        config["background_color"] = color[1]  # Update the background color in config
        label.config(bg=color[1])  # Update the background color of the label
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def change_text_color():
    # Open a color picker dialog with the current text color as default
    color = colorchooser.askcolor(title="Choose Text Color", initialcolor=config["text_color"])
    if color[1]:  # Check if a color was selected
        config["text_color"] = color[1]  # Update the text color in config
        label.config(fg=color[1])  # Update the text color of the label
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def change_transparency():
    # Ask the user for the new alpha value (transparency)
    new_alpha = simpledialog.askfloat("Change Transparency", "Enter the new alpha value (0.0 - 1.0):", initialvalue=config["alpha"], minvalue=0.1, maxvalue=1.0)
    if new_alpha is not None:
        config["alpha"] = new_alpha  # Update the alpha value in config
        indicator.attributes("-alpha", new_alpha)  # Update the alpha value of the indicator window
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def toggle_always_on_top(variable):
    config["always_on_top"] = bool(variable.get())
    indicator.attributes("-topmost", config["always_on_top"])
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
def change_min_width():
    current_min_width = config["min_width"]
    new_min_width = simpledialog.askinteger("Change Min Width", "Enter the new min width value:", initialvalue=current_min_width)
    if new_min_width is not None:
        config["min_width"] = new_min_width
        indicator.minsize(new_min_width, 0)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def toggle_show_title(variable):
    config["show_title"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label()
def toggle_title_as_filename(variable):
    config["title_as_filename"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label()
def toggle_show_size(variable):
    config["show_size"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label()
def toggle_show_resolution(variable):
    config["show_resolution"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label()
def toggle_show_location(variable):
    config["show_location"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    update_label()
def toggle_mouse_tips(variable):
    config["display_mouse_tips"] = bool(variable.get())
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
if __name__ == "__main__":
    if display_mouse_tips:
        display_message("Hover on widget,\nLeft Click: Next Wallpaper\nRight Click: Menu")
    indicator = tk.Tk()
    indicator.title("Easy Wallpaper Info")
    indicator.overrideredirect(True)
    indicator.minsize(min_width, 0)
    indicator.maxsize(indicator.winfo_screenwidth(), 0)
    indicator.attributes("-alpha", alpha)
    if always_on_top:
        indicator.attributes("-topmost", True)
    details = ""
    wallpaper_path = get_wallpaper_path()
    if show_title:
        title = get_image_title(wallpaper_path)
        details += f"Title: {title}\n"
    if show_size:
        size = get_image_size(wallpaper_path)
        details += f"Filesize: {size}\n"
    if show_resolution:
        resolution = get_image_resolution(wallpaper_path)
        details += f"Resolution: {resolution}\n"
    if show_location:
        details += f"Location: {wallpaper_path}\n"
    details = details[:-1]
    if text_align == "center":
        anchor = "center"
    elif text_align == "left":
        anchor = "w"
    elif text_align == "right":
        anchor = "e"
    else:
        messagebox.showwarning("Warning", "Invalid text_align value in config.json")
        os._exit(0)
    label = tk.Label(indicator, text=details, font=(text_font, text_size), bg=background_color, fg=text_color, anchor=anchor, justify=text_align)
    label.pack(expand=True, fill='both')
    label.config(cursor="hand2")
    label.bind("<Button-1>", on_left_click)
    label.bind("<Button-3>", on_right_click)
    label.bind("<ButtonRelease-1>", reset_cursor)
    menu = tk.Menu(indicator, tearoff=0)
    menu.add_command(label=f"EasyWallpaperInfo {version}", command=lambda: os.startfile(github_link), foreground="grey")
    menu.add_separator()
    menu.add_command(label="Open wallpaper", command=open_wallpaper)
    menu.add_command(label="Go to wallpaper location", command=open_wallpaper_location)
    menu.add_command(label="Copy title text", command=copy_title_text)
    menu.add_separator()
    position_menu = tk.Menu(indicator, tearoff=0)
    position_vars = {}
    for pos in ["center", "top_center", "bottom_center", "top_left", "top_right", "bottom_left", "bottom_right"]:
        label_text = pos.replace("_", " ").capitalize()
        var = tk.IntVar(value=1 if config["position"] == pos else 0)
        position_vars[pos] = var
        position_menu.add_checkbutton(label=label_text, variable=var, command=lambda p=pos, v=var: change_position(p, v))
    menu.add_cascade(label="Position", menu=position_menu)
    text_align_menu = tk.Menu(indicator, tearoff=0)
    text_align_vars = {}
    for align in ["left", "center", "right"]:
        label_text = align.capitalize()
        var = tk.IntVar(value=1 if config["text_align"] == align else 0)
        text_align_vars[align] = var
        text_align_menu.add_checkbutton(label=label_text, variable=var, command=lambda a=align, v=var: change_text_align(a, v))
    menu.add_cascade(label="Text Align", menu=text_align_menu)
    submenu_show_options = tk.Menu(menu, tearoff=0)
    title_as_filename_var = tk.IntVar(value=config["title_as_filename"])
    submenu_show_options.add_checkbutton(label="Title as Filename", variable=title_as_filename_var, command=lambda: toggle_title_as_filename(title_as_filename_var))
    show_title_var = tk.IntVar(value=config["show_title"])
    submenu_show_options.add_checkbutton(label="Show Title", variable=show_title_var, command=lambda: toggle_show_title(show_title_var))
    show_size_var = tk.IntVar(value=config["show_size"])
    submenu_show_options.add_checkbutton(label="Show Size", variable=show_size_var, command=lambda: toggle_show_size(show_size_var))
    show_resolution_var = tk.IntVar(value=config["show_resolution"])
    submenu_show_options.add_checkbutton(label="Show Resolution", variable=show_resolution_var, command=lambda: toggle_show_resolution(show_resolution_var))
    show_location_var = tk.IntVar(value=config["show_location"])
    submenu_show_options.add_checkbutton(label="Show Location", variable=show_location_var, command=lambda: toggle_show_location(show_location_var))
    menu.add_cascade(label="Show Options", menu=submenu_show_options)
    menu.add_command(label="Change Bottom Margin", command=change_bottom_margin)
    menu.add_command(label="Change Minimum Width", command=change_min_width)
    menu.add_separator()
    menu.add_command(label="Change Background Color", command=change_background_color)
    menu.add_command(label="Change Text Color", command=change_text_color)
    menu.add_command(label="Change Transparency", command=change_transparency)
    menu.add_separator()
    always_on_top_var = tk.IntVar(value=1 if config["always_on_top"] else 0)
    menu.add_checkbutton(label="Always on Top", variable=always_on_top_var, command=lambda: toggle_always_on_top(always_on_top_var))
    mouse_tips_var = tk.IntVar(value=1 if config["display_mouse_tips"] else 0)
    menu.add_checkbutton(label="Display Mouse Tips", variable=mouse_tips_var, command=lambda: toggle_mouse_tips(mouse_tips_var))
    menu.add_command(label="Edit config.json", command=lambda: os.startfile("config.json"))
    menu.add_command(label="Exit", command=exit_application)
    update_label()
    indicator.bind("<Configure>", lambda e: set_indicator_position(config["position"]))
    indicator.mainloop()
    ctypes.windll.kernel32.CloseHandle(mutex)