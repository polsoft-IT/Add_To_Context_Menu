import os
import shutil
import struct
import sys
import winreg
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Słowniki językowe
LANGUAGES = {
    'en': {
        'window_title': 'Add To Context Menu',
        'manage_window_title': 'Manage Entries',
        'app_label': 'Application name in menu:',
        'app_path_label': 'Path to application (.exe or .py):',
        'app_args_label': 'Launch arguments (Optional, e.g. %1):',
        'app_icon_label': 'Path to custom application icon .ico (Optional):',
        'browse': 'Browse...',
        'manage_apps': '🔍 Manage Apps',
        'submit': 'Add / Save',
        'edit_placeholder': '-- Select to edit --',
        'clear': 'Clear Form',
        'exit': 'Exit',
        'entries_label': 'Entries inside menu:',
        'delete_selected': 'Delete Selected',
        'close': 'Close',
        'confirm_delete': 'Are you sure you want to delete',
        'success_delete': 'Successfully deleted',
        'warning_select': 'Select an entry first!',
        'warning_fill': 'Fill in both entry name and app path first!',
        'warning_file_not_found': 'The specified application file does not exist!',
        'warning_icon_invalid': 'The specified icon file must exist and have a .ico extension!',
        'success_add': 'Successfully saved to menu!',
        'warning_remove_name': 'Enter the name of the entry you want to remove.',
        'warning_not_found': 'Entry not found.',
        'error_perm': 'Permission denied to write to user registry.',
        'error_generic': 'An error occurred:',
        'submenu_name': 'Programs',
        'choose_app': 'Choose an application or script',
        'supported_files': 'Supported files (*.exe *.py);;Python scripts (*.py);;Executable files (*.exe);;All files (*.*)',
        'choose_icon': 'Choose an icon file',
        'icon_files': 'Icon files (*.ico);;All files (*.*)',
        'python_launch_mode': 'Python launch mode:',
        'python_launch_console': 'Run with console',
        'python_launch_windowed': 'Run without console',
        'about_title': 'About',
        'about_desc': "A simple tool to manage context menu entries.\nAdd your favorite .exe or .py files to the context menu!",
        'about_created': "Created with Python and CustomTkinter",
        'author_label': "Author:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT",
        'management_panel': 'Management Panel:',
        'status_ready': 'Ready',
        'status_lang_changed': 'Language changed to',
        'status_loaded': 'Loaded entry:',
        'status_saved': 'Saved:'
    },
    'pl': {
        'window_title': 'Konfigurator Menu',
        'manage_window_title': 'Zarządzaj wpisami',
        'app_label': 'Nazwa aplikacji w menu:',
        'app_path_label': 'Ścieżka do aplikacji (.exe lub .py):',
        'app_args_label': 'Argumenty uruchamiania (Opcjonalnie, np. %1):',
        'app_icon_label': 'Ścieżka do własnej ikony aplikacji .ico (Opcjonalnie):',
        'browse': 'Przeglądaj...',
        'manage_apps': '🔍 Zarządzaj wpisami',
        'submit': 'Zatwierdź / Zapisz',
        'edit_placeholder': '-- Wybierz do edycji --',
        'clear': 'Wyczyść formularz',
        'exit': 'Wyjdź',
        'entries_label': 'Wpisy wewnątrz menu:',
        'delete_selected': 'Usuń zaznaczone',
        'close': 'Zamknij',
        'confirm_delete': 'Czy na pewno chcesz usunąć',
        'success_delete': 'Usunięto wpis',
        'warning_select': 'Wybierz najpierw wpis z listy!',
        'warning_fill': 'Wypełnij nazwę wpisu oraz ścieżkę do aplikacji przed zatwierdzeniem!',
        'warning_file_not_found': 'Wskazany plik aplikacji nie istnieje!',
        'warning_icon_invalid': 'Wskazany plik ikony musi istnieć i posiadać rozszerzenie .ico!',
        'success_add': 'Pomyślnie zapisano w menu!',
        'warning_remove_name': 'Wpisz nazwę etykiety, którą chcesz usunąć.',
        'warning_not_found': 'Nie znaleziono podanego wpisu.',
        'error_perm': 'Brak uprawnień do zapisu w rejestrze użytkownika.',
        'error_generic': 'Wystąpił błąd:',
        'submenu_name': 'Programy',
        'choose_app': 'Wybierz aplikację lub skrypt',
        'supported_files': 'Obsługiwane pliki (*.exe *.py);;Skrypty Python (*.py);;Pliki wykonywalne (*.exe);;Wszystkie pliki (*.*)',
        'choose_icon': 'Wybierz plik ikony',
        'icon_files': 'Pliki ikon (*.ico);;All files (*.*)',
        'python_launch_mode': 'Tryb uruchamiania Pythona:',
        'python_launch_console': 'Uruchamiaj z konsolą',
        'python_launch_windowed': 'Uruchamiaj bez konsoli',
        'about_title': 'O programie',
        'about_desc': "Proste narzędzie do zarządzania wpisami w menu kontekstowym.\nDodaj swoje ulubione pliki .exe lub .py do menu kontekstowego!",
        'about_created': "Utworzone za pomocą Pythona i CustomTkinter",
        'author_label': "Autor:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT",
        'management_panel': 'Panel zarządzania:',
        'status_ready': 'Gotowy',
        'status_lang_changed': 'Zmieniono język na',
        'status_loaded': 'Załadowano wpis:',
        'status_saved': 'Zapisano:'
    }
}

current_lang = 'en'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ICON_CANDIDATES = [
    os.path.join(SCRIPT_DIR, 'app_icon.ico'),
    os.path.join(SCRIPT_DIR, 'icon.ico'),
]
MENU_ICON_SOURCE = "app_icon.ico"


def get_app_icon_path():
    for candidate in APP_ICON_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return ''


def generate_default_app_ico(target_path):
    try:
        ico_header = struct.pack('<HHH', 0, 1, 1)
        icon_dir_entry = struct.pack('<BBBBHHII', 32, 32, 0, 0, 1, 32, 4160, 22)
        bitmap_info_header = struct.pack('<IiiHHIIiiii', 40, 32, 64, 1, 32, 0, 0, 0, 0, 0, 0)
        
        pixel_data = b''
        for y in range(32):
            for x in range(32):
                if x == 0 or x == 31 or y == 0 or y == 31:
                    pixel_data += struct.pack('<BBBB', 100, 100, 100, 255)
                else:
                    pixel_data += struct.pack('<BBBB', 240, 240, 240, 255)
            
        with open(target_path, 'wb') as f:
            f.write(ico_header)
            f.write(icon_dir_entry)
            f.write(bitmap_info_header)
            f.write(pixel_data)
        return True
    except Exception:
        return False


def build_command_string(app_path, current_executable=None, is_frozen=False, python_mode='console', args=""):
    absolute_path = os.path.abspath(app_path)
    suffix = f" {args}" if args.strip() else ""
    
    if absolute_path.lower().endswith('.py'):
        if python_mode == 'windowed':
            preferred_executable = shutil.which('pythonw')
            if preferred_executable and os.path.exists(preferred_executable):
                return f'"{preferred_executable}" "{absolute_path}"{suffix}'
        if is_frozen or getattr(sys, 'frozen', False):
            candidates = []
            for executable in [
                shutil.which('py'),
                shutil.which('python'),
                shutil.which('python3'),
                os.path.join(sys.base_prefix, 'python.exe'),
                os.path.join(sys.prefix, 'python.exe'),
                os.path.join(os.path.dirname(current_executable or sys.executable), 'python.exe'),
            ]:
                if executable and os.path.exists(executable):
                    candidates.append(executable)
            for executable in candidates:
                if os.path.exists(executable):
                    return f'"{executable}" "{absolute_path}"{suffix}'
        return f'"{current_executable or sys.executable}" "{absolute_path}"{suffix}'
    return f'"{absolute_path}"{suffix}'


def add_to_context_menu(label, app_path, icon_path="", python_mode='console', args=""):
    try:
        absolute_path = os.path.abspath(app_path)
        current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
        submenu_name = LANGUAGES[current_lang]['submenu_name']
        menu_icon_path = os.path.normpath(os.path.join(current_dir, MENU_ICON_SOURCE))
        
        command_string = build_command_string(
            app_path,
            current_executable=os.path.abspath(sys.executable),
            is_frozen=getattr(sys, 'frozen', False),
            python_mode=python_mode,
            args=args
        )

        if absolute_path.lower().endswith('.py'):
            if not icon_path or not os.path.exists(icon_path):
                generated_app_ico = os.path.join(os.path.dirname(absolute_path), f"{label}_icon.ico")
                if generate_default_app_ico(generated_app_ico):
                    icon_path = generated_app_ico
                else:
                    icon_path = sys.executable
        else:
            if not icon_path or not os.path.exists(icon_path):
                icon_path = absolute_path

        root_key = winreg.HKEY_CURRENT_USER
        base_menu_path = f"Software\\Classes\\Directory\\Background\\shell\\{submenu_name}"
        
        menu_key = winreg.CreateKey(root_key, base_menu_path)
        winreg.SetValueEx(menu_key, "MUIVerb", 0, winreg.REG_SZ, submenu_name)
        
        if os.path.exists(menu_icon_path):
            winreg.SetValueEx(menu_key, "Icon", 0, winreg.REG_SZ, menu_icon_path)
        else:
            winreg.SetValueEx(menu_key, "Icon", 0, winreg.REG_SZ, "shell32.dll,16")
            
        winreg.SetValueEx(menu_key, "SubCommands", 0, winreg.REG_SZ, "")
        winreg.CloseKey(menu_key)
        
        app_key_path = f"{base_menu_path}\\Shell\\{label}"
        app_key = winreg.CreateKey(root_key, app_key_path)
        winreg.SetValueEx(app_key, "", 0, winreg.REG_SZ, label)
        winreg.SetValueEx(app_key, "Icon", 0, winreg.REG_SZ, f'"{os.path.abspath(icon_path)}"')
        
        cmd_key = winreg.CreateKey(app_key, "command")
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command_string)
        
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(app_key)
        return True
    except PermissionError:
        return "perm_error"
    except Exception as e:
        return str(e)


def remove_from_context_menu(label):
    try:
        submenu_name = LANGUAGES[current_lang]['submenu_name']
        root_key = winreg.HKEY_CURRENT_USER
        base_menu_path = f"Software\\Classes\\Directory\\Background\\shell\\{submenu_name}"
        app_key_path = f"{base_menu_path}\\Shell\\{label}"
        
        try:
            winreg.DeleteKey(root_key, f"{app_key_path}\\command")
            winreg.DeleteKey(root_key, app_key_path)
        except FileNotFoundError:
            pass
            
        try:
            shell_key = winreg.OpenKey(root_key, f"{base_menu_path}\\Shell")
            subkeys_count = winreg.QueryInfoKey(shell_key)[0]
            winreg.CloseKey(shell_key)
            
            if subkeys_count == 0:
                winreg.DeleteKey(root_key, f"{base_menu_path}\\Shell")
                winreg.DeleteKey(root_key, base_menu_path)
        except FileNotFoundError:
            try:
                winreg.DeleteKey(root_key, base_menu_path)
            except FileNotFoundError:
                pass
        return True
    except Exception:
        return False


def get_installed_menus():
    menus = []
    submenu_name = LANGUAGES[current_lang]['submenu_name']
    root_key = winreg.HKEY_CURRENT_USER
    shell_path = f"Software\\Classes\\Directory\\Background\\shell\\{submenu_name}\\Shell"
    try:
        key = winreg.OpenKey(root_key, shell_path)
        i = 0
        while True:
            try:
                sub_key_name = winreg.EnumKey(key, i)
                menus.append(sub_key_name)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
    return sorted(menus)


def get_entry_details(label):
    submenu_name = LANGUAGES[current_lang]['submenu_name']
    root_key = winreg.HKEY_CURRENT_USER
    app_key_path = f"Software\\Classes\\Directory\\Background\\shell\\{submenu_name}\\Shell\\{label}"
    
    details = {"path": "", "icon": "", "windowed": False, "args": ""}
    try:
        key = winreg.OpenKey(root_key, app_key_path)
        try:
            icon_val, _ = winreg.QueryValueEx(key, "Icon")
            details["icon"] = icon_val.replace('"', '').strip()
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)

        cmd_key = winreg.OpenKey(root_key, f"{app_key_path}\\command")
        cmd_val, _ = winreg.QueryValueEx(cmd_key, "")
        winreg.CloseKey(cmd_key)

        if "pythonw.exe" in cmd_val.lower():
            details["windowed"] = True

        parts = [p.strip() for p in cmd_val.split('"') if p.strip()]
        if parts:
            details["path"] = parts[-1]
            
            last_quote_index = cmd_val.rfind('"')
            if last_quote_index != -1 and last_quote_index < len(cmd_val) - 1:
                details["args"] = cmd_val[last_quote_index + 1:].strip()
            
    except Exception:
        pass
    return details


class ManageWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_gui = parent
        self.title("")
        self.geometry("400x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        icon_path = get_app_icon_path()
        if icon_path and sys.platform.startswith("win"):
            self.after(200, lambda: self.iconbitmap(icon_path))
            
        self.init_ui()
        self.update_language()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.lbl_entries = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.lbl_entries.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scroll_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        
        self.selected_item = ctk.StringVar(value="")

        self.btn_layout = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_layout.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        self.btn_layout.grid_columnconfigure(1, weight=1)

        self.btn_delete = ctk.CTkButton(self.btn_layout, text="", fg_color="#d32f2f", hover_color="#b71c1c", command=self.delete_selected)
        self.btn_delete.grid(row=0, column=0, padx=(0, 5))

        self.btn_close = ctk.CTkButton(self.btn_layout, text="", fg_color="#555555", hover_color="#444444", command=self.destroy)
        self.btn_close.grid(row=0, column=2, padx=(5, 0))

    def update_language(self):
        self.title(LANGUAGES[current_lang]['manage_window_title'])
        self.lbl_entries.configure(text=f"{LANGUAGES[current_lang]['entries_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.btn_delete.configure(text=LANGUAGES[current_lang]['delete_selected'])
        self.btn_close.configure(text=LANGUAGES[current_lang]['close'])
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        menus = get_installed_menus()
        self.selected_item.set("")
        
        for menu in menus:
            rb = ctk.CTkRadioButton(self.scroll_frame, text=menu, variable=self.selected_item, value=menu, font=ctk.CTkFont(family="Segoe UI", size=12))
            rb.pack(anchor="w", padx=10, pady=5)

    def delete_selected(self):
        selected_label = self.selected_item.get()
        if not selected_label:
            messagebox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_select'])
            return

        reply = messagebox.askyesno(
            LANGUAGES[current_lang]['error_generic'], 
            f"{LANGUAGES[current_lang]['confirm_delete']} '{selected_label}'?"
        )
        
        if reply:
            if remove_from_context_menu(selected_label):
                messagebox.showinfo(LANGUAGES[current_lang]['success_add'], f"{LANGUAGES[current_lang]['success_delete']} '{selected_label}'")
                self.refresh_list()
                self.parent_gui.refresh_edit_combo()


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("")
        self.geometry("380x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        icon_path = get_app_icon_path()
        if icon_path and sys.platform.startswith("win"):
            self.after(200, lambda: self.iconbitmap(icon_path))
            
        self.init_ui()
        self.update_language()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="Add To Context Menu", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=("#0f4c81", "#3b8ed0"))
        self.lbl_title.grid(row=0, column=0, padx=15, pady=(15, 2), sticky="w")

        self.lbl_version = ctk.CTkLabel(self, text="Version 3.0 (CustomTkinter)", font=ctk.CTkFont(family="Segoe UI", size=11), justify="left")
        self.lbl_version.grid(row=1, column=0, padx=15, pady=2, sticky="w")

        self.lbl_desc = ctk.CTkLabel(self, text="", wraplength=340, justify="left", font=ctk.CTkFont(family="Segoe UI", size=12))
        self.lbl_desc.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.lbl_created = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=11))
        self.lbl_created.grid(row=3, column=0, padx=15, pady=2, sticky="w")

        self.line = ctk.CTkFrame(self, height=2, fg_color=("#d1d5db", "#404040"))
        self.line.grid(row=4, column=0, padx=15, pady=10, sticky="ew")

        self.lbl_author = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=12))
        self.lbl_author.grid(row=5, column=0, padx=15, pady=2, sticky="w")

        self.lbl_mail = ctk.CTkLabel(self, text="", text_color=("#1e88e5", "#64b5f6"), cursor="hand2", font=ctk.CTkFont(family="Segoe UI", size=12, underline=True))
        self.lbl_mail.bind("<Button-1>", lambda e: webbrowser.open(f"mailto:{LANGUAGES[current_lang]['mail_address']}"))
        self.lbl_mail.grid(row=6, column=0, padx=15, pady=2, sticky="w")

        self.lbl_github = ctk.CTkLabel(self, text="", text_color=("#1e88e5", "#64b5f6"), cursor="hand2", font=ctk.CTkFont(family="Segoe UI", size=12, underline=True))
        self.lbl_github.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{LANGUAGES[current_lang]['github_url']}"))
        self.lbl_github.grid(row=7, column=0, padx=15, pady=2, sticky="w")

        self.btn_close = ctk.CTkButton(self, text="", command=self.destroy, width=100)
        self.btn_close.grid(row=8, column=0, padx=15, pady=(15, 10))

    def update_language(self):
        self.title(LANGUAGES[current_lang]['about_title'])
        self.lbl_desc.configure(text=LANGUAGES[current_lang]['about_desc'])
        self.lbl_created.configure(text=LANGUAGES[current_lang]['about_created'])
        self.lbl_author.configure(text=f"{LANGUAGES[current_lang]['author_label']} {LANGUAGES[current_lang]['author_name']}")
        self.lbl_mail.configure(text=f"{LANGUAGES[current_lang]['mail_label']} {LANGUAGES[current_lang]['mail_address']}")
        self.lbl_github.configure(text=f"{LANGUAGES[current_lang]['github_label']} {LANGUAGES[current_lang]['github_url']}")
        self.btn_close.configure(text=LANGUAGES[current_lang]['close'])


class AppGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Domyślny start w trybie jasnym
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.geometry("520x680")
        self.resizable(False, False)
        
        icon_path = get_app_icon_path()
        if icon_path and sys.platform.startswith("win"):
            self.iconbitmap(icon_path)
            
        self.init_ui()
        self.update_language()
        self.refresh_edit_combo()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Nagłówek
        self.header_widget = ctk.CTkFrame(self, fg_color=("#0f4c81", "#1f1f1f"), corner_radius=8)
        self.header_widget.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        lbl_h_title = ctk.CTkLabel(self.header_widget, text="Add To Context Menu", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="white")
        lbl_h_title.pack(anchor="w", padx=15, pady=(10, 2))
        lbl_h_sub = ctk.CTkLabel(self.header_widget, text="Manage context menu applications", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("#dce7f5", "#aaaaaa"))
        lbl_h_sub.pack(anchor="w", padx=15, pady=(0, 10))

        # Pasek górny
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=1, column=0, padx=15, pady=5, sticky="e")
        
        self.btn_lang = ctk.CTkButton(top_bar, text="PL", width=50, command=self.switch_language)
        self.btn_lang.pack(side="left", padx=2)
        
        # Przełącznik motywu (ikona dostosowuje się na bazie aktualnego motywu CustomTkinter)
        self.btn_theme = ctk.CTkButton(top_bar, text="🌙", width=40, command=self.toggle_theme)
        self.btn_theme.pack(side="left", padx=2)
        
        self.btn_about = ctk.CTkButton(top_bar, text="ℹ️", width=40, command=self.show_about)
        self.btn_about.pack(side="left", padx=2)

        # Panel Zarządzania
        self.lbl_management = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.lbl_management.grid(row=2, column=0, padx=15, pady=(10, 2), sticky="w")

        self.mgmt_frame = ctk.CTkFrame(self)
        self.mgmt_frame.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        self.mgmt_frame.grid_columnconfigure(0, weight=1)

        self.combo_edit = ctk.CTkOptionMenu(self.mgmt_frame, values=[], command=self.load_selected_entry_to_form)
        self.combo_edit.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_manage = ctk.CTkButton(self.mgmt_frame, text="", command=self.open_manage_window)
        self.btn_manage.grid(row=0, column=1, padx=10, pady=10)

        # Separator Line
        line = ctk.CTkFrame(self, height=2, fg_color=("#d1d5db", "#404040"))
        line.grid(row=4, column=0, padx=15, pady=10, sticky="ew")

        # Formularz
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=5, column=0, padx=15, pady=5, sticky="ew")
        self.form_frame.grid_columnconfigure(0, weight=1)

        # Nazwa aplikacji
        self.lbl_label = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        self.lbl_label.pack(anchor="w", pady=(5, 2))
        self.entry_label = ctk.CTkEntry(self.form_frame)
        self.entry_label.pack(fill="x", pady=2)

        # Ścieżka do aplikacji
        self.lbl_path = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        self.lbl_path.pack(anchor="w", pady=(5, 2))
        path_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        path_box.pack(fill="x", pady=2)
        path_box.grid_columnconfigure(0, weight=1)
        
        self.entry_path = ctk.CTkEntry(path_box)
        self.entry_path.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.btn_browse_path = ctk.CTkButton(path_box, text="", width=90, command=self.browse_app)
        self.btn_browse_path.grid(row=0, column=1, sticky="e")

        # Argumenty
        self.lbl_args = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        self.lbl_args.pack(anchor="w", pady=(5, 2))
        self.entry_args = ctk.CTkEntry(self.form_frame)
        self.entry_args.pack(fill="x", pady=2)

        # Ikona
        self.lbl_icon = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        self.lbl_icon.pack(anchor="w", pady=(5, 2))
        icon_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        icon_box.pack(fill="x", pady=2)
        icon_box.grid_columnconfigure(0, weight=1)
        
        self.entry_icon = ctk.CTkEntry(icon_box)
        self.entry_icon.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.btn_browse_icon = ctk.CTkButton(icon_box, text="", width=90, command=self.browse_icon)
        self.btn_browse_icon.grid(row=0, column=1, sticky="e")

        # Tryb uruchamiania Pythona
        self.lbl_python_mode = ctk.CTkLabel(self.form_frame, text="", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        self.lbl_python_mode.pack(anchor="w", pady=(5, 2))
        
        self.radio_var = ctk.IntVar(value=0)
        radio_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        radio_box.pack(fill="x", pady=2)
        
        self.console_radio = ctk.CTkRadioButton(radio_box, text="", variable=self.radio_var, value=0)
        self.console_radio.pack(side="left", padx=(0, 15))
        self.windowed_radio = ctk.CTkRadioButton(radio_box, text="", variable=self.radio_var, value=1)
        self.windowed_radio.pack(side="left")

        # Dolne przyciski akcji
        self.bottom_box = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_box.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        self.bottom_box.grid_columnconfigure(1, weight=1)

        self.btn_exit = ctk.CTkButton(self.bottom_box, text="", fg_color="#555555", hover_color="#444444", command=self.destroy)
        self.btn_exit.grid(row=0, column=0, padx=(0, 5))

        self.btn_clear = ctk.CTkButton(self.bottom_box, text="", fg_color="#757575", hover_color="#616161", command=self.clear_form)
        self.btn_clear.grid(row=0, column=2, padx=5)

        self.btn_submit = ctk.CTkButton(self.bottom_box, text="", fg_color=("#0f4c81", "#1f538d"), hover_color=("#0b4d84", "#1a4677"), command=self.submit)
        self.btn_submit.grid(row=0, column=3, padx=(5, 0))

        # Status Bar
        self.lbl_status = ctk.CTkLabel(self, text="", anchor="w", font=ctk.CTkFont(family="Segoe UI", size=11), fg_color=("#e7ebf0", "#2e2e2e"), text_color=("#333333", "#ffffff"), height=25)
        self.lbl_status.grid(row=7, column=0, sticky="ew")

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Light":
            ctk.set_appearance_mode("dark")
            self.btn_theme.configure(text="☀️")
        else:
            ctk.set_appearance_mode("light")
            self.btn_theme.configure(text="🌙")

    def switch_language(self):
        global current_lang
        current_lang = 'pl' if current_lang == 'en' else 'en'
        self.lbl_status.configure(text=f"{LANGUAGES[current_lang]['status_lang_changed']} {current_lang.upper()}")
        self.update_language()

    def update_language(self):
        self.title(LANGUAGES[current_lang]['window_title'])
        self.btn_lang.configure(text="PL" if current_lang == "en" else "EN")
        self.lbl_management.configure(text=LANGUAGES[current_lang]['management_panel'])
        self.lbl_label.configure(text=f"{LANGUAGES[current_lang]['app_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.lbl_path.configure(text=LANGUAGES[current_lang]['app_path_label'])
        self.lbl_args.configure(text=LANGUAGES[current_lang]['app_args_label'])
        self.lbl_icon.configure(text=LANGUAGES[current_lang]['app_icon_label'])
        self.btn_browse_path.configure(text=LANGUAGES[current_lang]['browse'])
        self.btn_browse_icon.configure(text=LANGUAGES[current_lang]['browse'])
        self.lbl_python_mode.configure(text=LANGUAGES[current_lang]['python_launch_mode'])
        self.console_radio.configure(text=LANGUAGES[current_lang]['python_launch_console'])
        self.windowed_radio.configure(text=LANGUAGES[current_lang]['python_launch_windowed'])
        self.btn_manage.configure(text=LANGUAGES[current_lang]['manage_apps'])
        self.btn_submit.configure(text=LANGUAGES[current_lang]['submit'])
        self.btn_clear.configure(text=LANGUAGES[current_lang]['clear'])
        self.btn_exit.configure(text=LANGUAGES[current_lang]['exit'])
        self.lbl_status.configure(text=LANGUAGES[current_lang]['status_ready'])
        self.refresh_edit_combo()

    def refresh_edit_combo(self):
        menus = get_installed_menus()
        placeholder = LANGUAGES[current_lang]['edit_placeholder']
        all_values = [placeholder] + menus
        
        self.combo_edit.configure(values=all_values)
        self.combo_edit.set(placeholder)

    def load_selected_entry_to_form(self, selected_label):
        if selected_label == LANGUAGES[current_lang]['edit_placeholder']:
            return
            
        details = get_entry_details(selected_label)
        
        self.entry_label.delete(0, 'end')
        self.entry_label.insert(0, selected_label)
        
        self.entry_path.delete(0, 'end')
        self.entry_path.insert(0, details["path"])
        
        self.entry_args.delete(0, 'end')
        self.entry_args.insert(0, details["args"])
        
        self.entry_icon.delete(0, 'end')
        self.entry_icon.insert(0, details["icon"])
        
        if details["windowed"]:
            self.radio_var.set(1)
        else:
            self.radio_var.set(0)
            
        self.lbl_status.configure(text=f"{LANGUAGES[current_lang]['status_loaded']} {selected_label}")

    def browse_app(self):
        file_path = filedialog.askopenfilename(
            title=LANGUAGES[current_lang]['choose_app'],
            filetypes=[("Supported files", "*.exe *.py"), ("Python scripts", "*.py"), ("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            norm_path = os.path.normpath(file_path)
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, norm_path)
            self.lbl_status.configure(text=f"App: {os.path.basename(norm_path)}")

    def browse_icon(self):
        icon_path = filedialog.askopenfilename(
            title=LANGUAGES[current_lang]['choose_icon'],
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if icon_path:
            norm_path = os.path.normpath(icon_path)
            self.entry_icon.delete(0, 'end')
            self.entry_icon.insert(0, norm_path)
            self.lbl_status.configure(text=f"Icon: {os.path.basename(norm_path)}")

    def clear_form(self):
        self.entry_label.delete(0, 'end')
        self.entry_path.delete(0, 'end')
        self.entry_args.delete(0, 'end')
        self.entry_icon.delete(0, 'end')
        self.radio_var.set(0)
        self.refresh_edit_combo()
        self.lbl_status.configure(text=LANGUAGES[current_lang]['status_ready'])

    def submit(self):
        label = self.entry_label.get().strip()
        app_path = self.entry_path.get().strip()
        args = self.entry_args.get().strip()
        icon_path = self.entry_icon.get().strip()

        if not label or not app_path:
            messagebox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_fill'])
            return

        if not os.path.exists(app_path):
            messagebox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_file_not_found'])
            return

        if icon_path:
            if not os.path.exists(icon_path) or not icon_path.lower().endswith('.ico'):
                messagebox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_icon_invalid'])
                return

        python_mode = 'windowed' if (app_path.lower().endswith('.py') and self.radio_var.get() == 1) else 'console'

        result = add_to_context_menu(label, app_path, icon_path, python_mode=python_mode, args=args)
        if result is True:
            messagebox.showinfo(
                LANGUAGES[current_lang]['success_add'], 
                f"{LANGUAGES[current_lang]['success_add']} '{label}' -> {LANGUAGES[current_lang]['submenu_name']}!"
            )
            self.lbl_status.configure(text=f"{LANGUAGES[current_lang]['status_saved']} {label}")
            self.clear_form()
        elif result == "perm_error":
            messagebox.showerror(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['error_perm'])
        else:
            messagebox.showerror(LANGUAGES[current_lang]['error_generic'], f"{LANGUAGES[current_lang]['error_generic']} {result}")

    def open_manage_window(self):
        ManageWindow(self)

    def show_about(self):
        AboutWindow(self)


if __name__ == "__main__":
    app = AppGui()
    app.mainloop()