# EasyWallpaperInfo: Desktop Wallpaper Info Widget / One Click Next Wallpaper / Find Desktop Background Path
EasyWallpaperInfo is a handy Python app that lets you explore your desktop wallpaper. With a simple and customizable widget, you can see your current wallpaper’s metadata title, filesize, resolution, and location on your screen. You can also cycle to the next wallpaper with a click, or open the wallpaper in file explorer or your default image viewer. EasyWallpaperInfo is a great tool for wallpaper enthusiasts who want to know more about their desktop backgrounds.

<img title="EasyWallpaperInfo" src='examples/preview1.png' width='100%'>

> # [Download the Latest Executable (.exe) Release](https://github.com/denizsafak/EasyWallpaperInfo/releases/latest)
> You can download the executable (.exe) version of the same script, making it easy to use without the need to install Python or other libraries.

## `Features`
- Display wallpaper details on the screen.
- Go to next desktop wallpaper with a single click.
- Context menu for quick actions (open wallpaper, go to location, copy title).
- Customizable appearance (font size, text color, background color).
- Options to show/hide title, size, resolution, and location.
- Options to select position or text align.
- Mouse tips for user guidance.
- Prevents multiple instances from running simultaneously.

<img title="EasyWallpaperInfo Options" src='examples/preview2.png' width='100%'>

## `Configuration`
Open the config.json file to customize settings:
```json
{
    "always_on_top": false,
    "display_mouse_tips": false,
    "position": "bottom_left",
    "text_align": "left",
    "text_size": 10,
    "text_font": "Arial",
    "text_color": "white",
    "background_color": "black",
    "alpha": 0.6,
    "bottom_margin": 118,
    "min_width": 200,
    "show_title": true,
    "title_as_filename": false,
    "show_size": true,
    "show_resolution": true,
    "show_location": true,
    "indicator_update_frequency": 1000
}
```

- `"always_on_top":` Set it true, if you want the widget always on top of the screen.
- `"display_mouse_tips":` Display mouse tips.
- `"position":` Where the widget located. `(Please change it on widget menu.)`
- `"text_align":` Align of the text. `(Please change it on widget menu.)`
- `text_size`, `text_font`, `text_color`, `background_color`: Appearance settings.
- `alpha:` Transparency level of the display window.
- `bottom_margin:` Margin from bottom. (Applies only when it is located on bottom.)
- `min_width:` Minimum width of the display window.
- `title_as_filename:` Instead of using meta title, use the filename as title.
- `show_title`, `show_size`, `show_resolution`, `show_location`: Toggle display of information.
- `indicator_update_frequency:` Update frequency of wallpaper details.

## `How to Run?`

### Option 1: Executable Script
- If you don't want to install Python and dependencies, you can download the precompiled executable version from the Releases section.
[Download the Latest Executable (.exe) Release](https://github.com/denizsafak/EasyWallpaperInfo/releases/latest)
- Double-click on EasyWallpaperInfo.exe to launch the application. The wallpaper information display will appear on your screen.

### Option 2: Run with Python
- Clone or download the repository to your local machine.
- Install Python to your computer.
- Run "run.bat" file.
- The wallpaper information display will appear on your screen.

## `Useage`
- Left Click (Next Wallpaper): Click on the display to cycle to the next wallpaper.
- Right Click (Menu): Right-click on the display to open a context menu with options to open the wallpaper, go to its location, copy the title text, and exit the application.
- To exit the application, right click on the window and select "Exit."

<img title="EasyWallpaperInfo Mouse Tips" src='examples/preview3.png' width='100%'>

> [!NOTE]
> - This script is primarily intended for Windows. Adaptations might be needed for other operating systems.

> Tags: easywallpaperinfo, current wallpaper information, wallpaper details, background details, background information, next desktop wallpaper, desktop wallpaper details, desktop wallpaper info, python wallpaper script, wallpaper location finder, easy wallpaper management, wallpaper utilities, wallpaper changer, wallpaper viewer, background image details, wallpaper tools, wallpaper filesize, wallpaper accessibility, windows desktop
