# Add To Context Menu v1.2 🛠️

![Windows](https://img.shields.io/badge/OS-Windows-blue?logo=windows&logoColor=white)

![Application screenshot](screenshot.png)

Add To Context Menu is a lightweight Windows utility that lets you add `.exe` files and Python scripts (`.py`) directly to the desktop right-click menu.

All added shortcuts appear in a dedicated submenu called **Programs** (or **Programy**, if Polish is selected).

## 🚀 Features

- **Add Apps and Scripts**: Add executable files and Python scripts as desktop context menu shortcuts.
- **Custom Icons**: Assign a `.ico` file to any entry for a polished look.
- **Fallback Icon Support**: If you do not choose a custom icon for a Python script, a default fallback icon is generated automatically.
- **Entry Management**: Open the management window to view or remove installed menu entries.
- **Bilingual Interface**: Switch instantly between English and Polish.
- **No Admin Required**: Changes are written to the current user's registry hive (`HKEY_CURRENT_USER`).

## 🛠️ What’s New in v1.2

- Updated app name and packaging metadata.
- Modernized main window styling.
- Fixed-size GUI windows for consistent layout.
- Header icon support using `app_icon.ico`.

## Requirements

- Windows 10 / 11
- Python 3.6 or newer
- Optional: Pillow library for improved icon rendering

## Getting Started

Run the application directly from the project folder:

```bash
python Add_To_Context_Menu.py
```

If you are using the included virtual environment:

```bash
.venv\Scripts\python.exe Add_To_Context_Menu.py
```

## How to Use

1. Enter a label in **Application name in menu**.
2. Click **Browse...** and select the `.exe` or `.py` file.
3. (Optional) Choose a `.ico` icon file.
4. Click **Add**.
5. Right-click the desktop and open the **Programs** submenu to launch your new shortcut.

### Removing an entry

1. Click **🔍 Manage Apps / Show Added**.
2. Select the entry you want to remove.
3. Click **Delete Selected**.

## Author
- Sebastian Januchowski
- Email: polsoft.its@mail.com
- GitHub: [polsoft-seb07uk](https://github.com/polsoft-seb07uk)

## License
This project is licensed under the MIT License. See `LICENSE` for details.