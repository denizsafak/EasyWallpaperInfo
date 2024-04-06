import os
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, Scrollbar
import tkinter.font as tkFont
from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
from PIL import Image
from ahk import AHK
import ctypes
import json
Image.MAX_IMAGE_PIXELS = None
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
with open("config.json", "r") as f:
    config = json.load(f)
version = "v1.7"
github_link = "https://github.com/denizsafak/EasyWallpaperInfo"
bottom_margin = config["bottom_margin"]
min_width = config["min_width"]
alpha = config["alpha"]
indicator_update_frequency = config["indicator_update_frequency"]
text_size = config["text_size"]
text_font = config["text_font"]
text_style = config["text_style"]
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
    label2 = tk.Label(msg_window, text=message, font=(text_font, 14, text_style), bg=background_color, fg=text_color)
    label2.pack(expand=True, fill='both')
    msg_window.after(5000, msg_window.destroy)
    msg_window.mainloop()
def set_indicator_position(position):
    global indicator
    screen_width = indicator.winfo_screenwidth()
    screen_height = indicator.winfo_screenheight()
    if position == "center":
        x = (screen_width - indicator.winfo_width()) // 2
        y = (screen_height - indicator.winfo_height()) // 2
    elif position == "top_center":
        x = (screen_width - indicator.winfo_width()) // 2
        y = 0
    elif position == "bottom_center":
        x = (screen_width - indicator.winfo_width()) // 2
        y = screen_height - indicator.winfo_height() - config["bottom_margin"]
    elif position == "top_left":
        x, y = 0, 0
    elif position == "top_right":
        x = screen_width - indicator.winfo_width()
        y = 0
    elif position == "bottom_left":
        x, y = 0, screen_height - indicator.winfo_height() - config["bottom_margin"]
    elif position == "bottom_right":
        x = screen_width - indicator.winfo_width()
        y = screen_height - indicator.winfo_height() - config["bottom_margin"]
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
    initial_bottom_margin = config["bottom_margin"]  # Store the initial value
    bottom_margin_dialog = tk.Toplevel(indicator)
    bottom_margin_dialog.title("Change Bottom Margin")
    bottom_margin_dialog.minsize(500, 0)
    bottom_margin_dialog.resizable(True, False)
    label = tk.Label(bottom_margin_dialog, text="Set Bottom Margin (0 - 400):")
    label.pack(padx=10, pady=(15, 0))
    bottom_margin_slider = tk.Scale(bottom_margin_dialog, from_=0, to=400, orient=tk.HORIZONTAL, cursor="hand2")
    bottom_margin_slider.set(initial_bottom_margin)  # Set slider to initial value
    bottom_margin_slider.pack(padx=10, pady=(0, 10), fill="x")
    def update_bottom_margin(value):
        bottom_margin_dialog.update_idletasks()
        # Calculate the change in bottom margin
        margin_change = int(initial_bottom_margin - int(value))
        # Update the bottom margin
        config["bottom_margin"] = int(value)
        # Set the new indicator position
        set_indicator_position(config["position"])
    bottom_margin_slider.config(command=update_bottom_margin)
    def apply_bottom_margin():
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        bottom_margin_dialog.destroy()
    def cancel_bottom_margin():
        bottom_margin_slider.set(initial_bottom_margin)  # Reset slider to initial value
        config["bottom_margin"] = initial_bottom_margin  # Restore initial value in config
        bottom_margin_dialog.destroy()
    bottom_margin_dialog.protocol("WM_DELETE_WINDOW", cancel_bottom_margin)
    button_frame_margin = tk.Frame(bottom_margin_dialog)
    button_frame_margin.pack(padx=10, pady=(0, 10), fill="x")
    cancel_button = tk.Button(button_frame_margin, text="Cancel", pady=5, fg="white", bg="gray50", activebackground="gray40",
                              activeforeground="white", relief=tk.RAISED, borderwidth=2, cursor="hand2",
                              command=cancel_bottom_margin)
    cancel_button.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
    apply_button = tk.Button(button_frame_margin, text="Apply", pady=5, fg="white", bg="#00a31e", activebackground="#007d17",
                             activeforeground="white", relief=tk.RAISED, borderwidth=2, cursor="hand2",
                             command=apply_bottom_margin)
    apply_button.pack(side=tk.RIGHT, fill="x", expand=True)
def change_background_color():
    # Open a color picker dialog with the current background color as default
    color = colorchooser.askcolor(title="Choose Background Color", initialcolor=config["background_color"])
    if color[1]:  # Check if a color was selected
        config["background_color"] = color[1]  # Update the background color in config
        label.config(bg=color[1])  # Update the background color of the label
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def change_text_color():
    color = colorchooser.askcolor(title="Choose Font Color", initialcolor=config["text_color"])
    if color[1]:  # Check if a color was selected
        config["text_color"] = color[1]  # Update the text color in config
        label.config(fg=color[1])  # Update the text color of the label
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
def change_transparency():
    initial_alpha = config["alpha"]
    transparency_dialog = tk.Toplevel(indicator)
    transparency_dialog.title("Change Transparency")
    transparency_dialog.minsize(300, 0)
    transparency_dialog.resizable(True, False)
    label = tk.Label(transparency_dialog, text="Set Transparency (0.1 - 1.0):")
    label.pack(padx=10, pady=(15, 0))
    transparency_slider = tk.Scale(transparency_dialog, from_=0.1, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, cursor="hand2",
                                   command=lambda value: update_transparency(value, indicator))
    transparency_slider.set(config["alpha"])
    transparency_slider.pack(padx=10, pady=(0, 10), fill="x")
    button_frame = tk.Frame(transparency_dialog)
    button_frame.pack(padx=10, pady=(0, 10), fill="x")
    cancel_button = tk.Button(button_frame, text="Cancel", pady=5, fg="white", bg="gray50", activebackground="gray40",
                              activeforeground="white", relief=tk.RAISED, borderwidth=2, cursor="hand2",
                              command=lambda: cancel_transparency(initial_alpha, transparency_dialog))
    cancel_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    apply_button = tk.Button(button_frame, text="Apply", pady=5, fg="white", bg="#00a31e", activebackground="#007d17",
                             activeforeground="white", relief=tk.RAISED, borderwidth=2, cursor="hand2",
                             command=lambda: apply_transparency(transparency_slider.get(), transparency_dialog))
    apply_button.pack(side="right", fill="x", expand=True)

    def update_transparency(value, widget):
        widget.attributes("-alpha", value)
    def apply_transparency(alpha, dialog):
        config["alpha"] = alpha
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        dialog.destroy()
    def cancel_transparency(alpha, dialog):
        indicator.attributes("-alpha", alpha)
        dialog.destroy()
    transparency_dialog.protocol("WM_DELETE_WINDOW", lambda: cancel_transparency(initial_alpha, transparency_dialog))
    transparency_dialog.mainloop()
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
    label = tk.Label(indicator, text=details, font=(text_font, text_size, text_style), bg=background_color, fg=text_color, anchor=anchor, justify=text_align)
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
    for pos in ["center", "top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right"]:
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
    menu.add_command(label="Change Bottom Margin", command=change_bottom_margin)
    menu.add_command(label="Change Minimum Width", command=change_min_width)
    menu.add_separator()
    def change_font():
        initial_config = {
            "text_font": config["text_font"],
            "text_size": config["text_size"],
            "text_style": config["text_style"]
        }
        def apply_changes():
            selected_font_index = font_listbox.curselection()
            if selected_font_index:
                selected_font = font_listbox.get(selected_font_index[0])
                selected_size = custom_size_var.get()
                try:
                    text_size = int(selected_size)
                    if text_size <= 0:
                        raise ValueError("Font size must be a positive integer.")
                except ValueError:
                    text_size = 10
                font_styles = []
                if bold_var.get():
                    font_styles.append("bold")
                if italic_var.get():
                    font_styles.append("italic")
                if underline_var.get():
                    font_styles.append("underline")
                if strikethrough_var.get():
                    font_styles.append("overstrike")
                font_style = " ".join(font_styles)
                text_style = "normal" if not font_style else font_style
                label.config(font=(selected_font, text_size, text_style))
                with open("config.json", "w") as f:
                    config["text_font"] = selected_font
                    config["text_size"] = text_size
                    config["text_style"] = text_style
                    json.dump(config, f, indent=4)
        def update_label(*args):
            apply_changes()
        def update_font_size_entry(event):
            selection = font_size_listbox.curselection()
            if selection:
                custom_size_var.set(sizes[selection[0]])
        def cancel_changes():
            config.update(initial_config)
            label.config(font=(config["text_font"], config["text_size"], config["text_style"]))
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            font_dialog.destroy()
        def on_closing():
            cancel_changes()
        def close_window():
            apply_changes()
            font_dialog.destroy()
        def move_selection(event):
            if font_listbox == indicator.focus_get():
                current_selection = font_listbox.curselection()
                if current_selection:
                    if event.keysym == "Up":
                        font_listbox.select_clear(0, tk.END)
                        current_index = max(current_selection[0] - 1, 0)
                        font_listbox.selection_set(current_index)
                        font_listbox.see(current_index)
                    elif event.keysym == "Down":
                        font_listbox.select_clear(0, tk.END)
                        current_index = min(current_selection[0] + 1, len(fonts) - 1)
                        font_listbox.selection_set(current_index)
                        font_listbox.see(current_index)
                    update_label()
            elif font_size_listbox == indicator.focus_get():
                current_selection = font_size_listbox.curselection()
                if current_selection:
                    if event.keysym == "Up":
                        font_size_listbox.select_clear(0, tk.END)
                        current_index = max(current_selection[0] - 1, 0)
                        font_size_listbox.selection_set(current_index)
                        font_size_listbox.see(current_index)
                    elif event.keysym == "Down":
                        font_size_listbox.select_clear(0, tk.END)
                        current_index = min(current_selection[0] + 1, len(sizes) - 1)
                        font_size_listbox.selection_set(current_index)
                        font_size_listbox.see(current_index)
                    update_font_size_entry(event)  # Update font size entry after moving selection
            else:
                current_selection = None
        font_dialog = tk.Toplevel(indicator)
        font_dialog.title("Change Font/Font Size/Style")
        font_dialog.geometry("500x400")  # Increased width for font styles
        font_dialog.minsize(500, 400)  # Minimum width and height
        font_dialog.protocol("WM_DELETE_WINDOW", on_closing)
        current_font = config["text_font"]
        current_size = str(config["text_size"])
        current_style = config["text_style"]
        font_label = tk.Label(font_dialog, text="Select Font Family:")
        font_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        fonts = tkFont.families()
        font_listbox = tk.Listbox(font_dialog, selectmode=tk.SINGLE, exportselection=0)
        for font in fonts:
            font_listbox.insert(tk.END, font)
        font_listbox.grid(row=1, column=0, padx=(10,2.5), pady=(0, 5), sticky="nsew", rowspan=2)
        font_listbox_scrollbar = tk.Scrollbar(font_listbox, orient="vertical", command=font_listbox.yview)
        font_listbox.config(yscrollcommand=font_listbox_scrollbar.set)
        font_listbox_scrollbar.pack(side="right", fill="y")
        font_listbox.bind("<<ListboxSelect>>", update_label)
        font_listbox.bind("<Up>", move_selection)
        font_listbox.bind("<Down>", move_selection)
        try:
            font_index = fonts.index(current_font)
            font_listbox.selection_set(font_index)
            font_listbox.see(font_index - 8)
        except ValueError:
            pass
        font_size_label = tk.Label(font_dialog, text="Select Font Size:")
        font_size_label.grid(row=0, column=1, padx=(2.5,10), pady=5, sticky="w")
        custom_size_var = tk.StringVar(value=current_size)
        custom_size_entry = tk.Entry(font_dialog, textvariable=custom_size_var)
        custom_size_entry.grid(row=1, column=1, padx=(2.5,10), pady=(0, 5), sticky="ew")
        custom_size_entry.config(validate="key", validatecommand=(custom_size_entry.register(validate_size_entry), "%P"))
        sizes = [str(size) for size in range(6, 43)]
        font_size_listbox = tk.Listbox(font_dialog, selectmode=tk.SINGLE, exportselection=0)
        for size in sizes:
            font_size_listbox.insert(tk.END, size)
        font_size_listbox.grid(row=2, column=1, padx=(2.5,10), pady=(0, 5), sticky="nsew")
        font_size_listbox_scrollbar = tk.Scrollbar(font_size_listbox, orient="vertical", command=font_size_listbox.yview)
        font_size_listbox.config(yscrollcommand=font_size_listbox_scrollbar.set)
        font_size_listbox_scrollbar.pack(side="right", fill="y")
        font_size_listbox.bind("<<ListboxSelect>>", update_label)
        font_size_listbox.bind("<ButtonRelease-1>", update_font_size_entry)
        custom_size_var.trace_add("write", update_label)
        font_size_listbox.bind("<Up>", move_selection)
        font_size_listbox.bind("<Down>", move_selection)
        font_style_frame = tk.Frame(font_dialog)
        font_style_frame.grid(row=3, column=0, columnspan=2, sticky="nw")
        font_style_label = tk.Label(font_style_frame, text="Select Font Style:")
        font_style_label.grid(row=0, column=0, padx=10, pady=(0,5), sticky="w", columnspan=4)
        # Font Style Checkboxes
        bold_var = tk.BooleanVar()
        bold_checkbox = tk.Checkbutton(font_style_frame, text="Bold", variable=bold_var, command=update_label)
        italic_var = tk.BooleanVar()
        italic_checkbox = tk.Checkbutton(font_style_frame, text="Italic", variable=italic_var, command=update_label)
        underline_var = tk.BooleanVar()
        underline_checkbox = tk.Checkbutton(font_style_frame, text="Underline", variable=underline_var, command=update_label)
        strikethrough_var = tk.BooleanVar()
        strikethrough_checkbox = tk.Checkbutton(font_style_frame, text="Strikethrough", variable=strikethrough_var, command=update_label)
        bold_checkbox.grid(row=1, column=0, padx=(10, 5), pady=(0, 5), sticky="w")
        italic_checkbox.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")
        underline_checkbox.grid(row=1, column=2, padx=5, pady=(0, 5), sticky="w")
        strikethrough_checkbox.grid(row=1, column=3, padx=5, pady=(0, 5), sticky="w")
        # Apply and Cancel Buttons
        button_frame = tk.Frame(font_dialog)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=(0,10))
        # Apply button closes the window
        apply_button = tk.Button(button_frame, text="Apply", command=close_window,  padx=100,
        pady=5,
        fg="white",
        bg="#00a31e",
        activebackground="#007d17",
        activeforeground="white",
        relief=tk.RAISED,
        borderwidth=2,
        cursor="hand2")
        apply_button.pack(side=tk.RIGHT, padx=(2.5, 0))  # Add padding after the Apply button
        cancel_button = tk.Button(
        button_frame,
        text="Cancel",
        command=cancel_changes,
        padx=100,
        pady=5,
        fg="white",
        bg="gray50",
        activebackground="gray40",
        activeforeground="white",
        relief=tk.RAISED,
        borderwidth=2,
        cursor="hand2")
        cancel_button.pack(side=tk.LEFT, padx=(0, 2.5))  # Add padding before the Cancel button
        font_dialog.grid_rowconfigure(2, weight=1)
        font_dialog.grid_columnconfigure(0, weight=3)
        font_dialog.grid_columnconfigure(1, weight=0)
        # Select currently applied font style
        if "bold" in current_style:
            bold_var.set(True)
        if "italic" in current_style:
            italic_var.set(True)
        if "underline" in current_style:
            underline_var.set(True)
        if "overstrike" in current_style:
            strikethrough_var.set(True)
        try:
            font_size_index = sizes.index(current_size)
            font_size_listbox.selection_set(font_size_index)
            font_size_listbox.see(font_size_index - 6)
        except ValueError:
            pass
    def validate_size_entry(input):
        if input.isdigit():
            return True
        elif input == "":
            return True
        else:
            return False
    menu.add_command(label="Change Background Color", command=change_background_color)
    menu.add_command(label="Change Transparency", command=change_transparency)
    menu.add_command(label="Change Font Color", command=change_text_color)
    menu.add_command(label="Change Font Styling", command=change_font)
    menu.add_separator()
    menu.add_cascade(label="Settings", menu=submenu_show_options)
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