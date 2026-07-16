
import os
import shutil
import struct
import sys
import winreg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Language dictionaries
LANGUAGES = {
    'en': {
        'window_title': 'Add To Context Menu',
        'manage_window_title': 'Manage Entries',
        'app_label': 'Application name in menu:',
        'app_path_label': 'Path to application (.exe or .py):',
        'app_icon_label': 'Path to custom application icon .ico (Optional):',
        'browse': 'Browse...',
        'manage_apps': '🔍 Manage Apps / Show Added',
        'submit': 'Add',
        'cancel': 'Remove',
        'exit': 'Exit',
        'entries_label': 'Entries inside menu:',
        'delete_selected': 'Delete Selected',
        'close': 'Close',
        'confirm_delete': 'Are you sure you want to delete',
        'success_delete': 'Successfully deleted',
        'warning_select': 'Select an entry first!',
        'warning_fill': 'Fill in both entry name and app path first!',
        'success_add': 'Successfully added to menu!',
        'warning_remove_name': 'Enter the name of the entry you want to remove.',
        'warning_not_found': 'Entry not found.',
        'error_perm': 'Permission denied to write to user registry.',
        'error_generic': 'An error occurred:',
        'submenu_name': 'Programs',
        'choose_app': 'Choose an application or script',
        'supported_files': 'Supported files',
        'python_scripts': 'Python scripts',
        'exe_files': 'Executable files',
        'all_files': 'All files',
        'choose_icon': 'Choose an icon file',
        'icon_files': 'Icon files',
        'python_launch_mode': 'Python launch mode:',
        'python_launch_console': 'Run with console',
        'python_launch_windowed': 'Run without console',
        'about_title': 'About',
        'about_desc': "A simple tool to manage context menu entries.\nAdd your favorite .exe or .py files to the context menu!",
        'about_created': "Created with Python and Tkinter",
        'author_label': "Author:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT"
    },
    'pl': {
        'window_title': 'Konfigurator Menu',
        'manage_window_title': 'Zarządzaj wpisami',
        'app_label': 'Nazwa aplikacji w menu:',
        'app_path_label': 'Ścieżka do aplikacji (.exe lub .py):',
        'app_icon_label': 'Ścieżka do własnej ikony aplikacji .ico (Opcjonalnie):',
        'browse': 'Przeglądaj...',
        'manage_apps': '🔍 Zarządzaj aplikacjami / Wyświetl dodane',
        'submit': 'Zatwierdź',
        'cancel': 'Anuluj (Usuń)',
        'exit': 'Wyjdź',
        'entries_label': 'Wpisy wewnątrz menu:',
        'delete_selected': 'Usuń zaznaczone',
        'close': 'Zamknij',
        'confirm_delete': 'Czy na pewno chcesz usunąć',
        'success_delete': 'Usunięto wpis',
        'warning_select': 'Wybierz najpierw wpis z listy!',
        'warning_fill': 'Wypełnij nazwę wpisu oraz ścieżkę do aplikacji przed zatwierdzeniem!',
        'success_add': 'Pomyślnie dodano do menu!',
        'warning_remove_name': 'Wpisz nazwę etykiety, którą chcesz usunąć.',
        'warning_not_found': 'Nie znaleziono podanego wpisu.',
        'error_perm': 'Brak uprawnień do zapisu w rejestrze użytkownika.',
        'error_generic': 'Wystąpił błąd:',
        'submenu_name': 'Programy',
        'choose_app': 'Wybierz aplikację lub skrypt',
        'supported_files': 'Obsługiwane pliki',
        'python_scripts': 'Skrypty Python',
        'exe_files': 'Pliki wykonywalne',
        'all_files': 'Wszystkie pliki',
        'choose_icon': 'Wybierz plik ikony',
        'icon_files': 'Pliki ikon',
        'python_launch_mode': 'Tryb uruchamiania Pythona:',
        'python_launch_console': 'Uruchamiaj z konsolą',
        'python_launch_windowed': 'Uruchamiaj bez konsoli',
        'about_title': 'O programie',
        'about_desc': "Proste narzędzie do zarządzania wpisami w menu kontekstowym.\nDodaj swoje ulubione pliki .exe lub .py do menu kontekstowego!",
        'about_created': "Utworzone za pomocą Pythona i Tkinter",
        'author_label': "Autor:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT"
    }
}

# Current language (default: English)
current_lang = 'en'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ICON_CANDIDATES = [
    os.path.join(SCRIPT_DIR, 'app_icon.ico'),
    os.path.join(SCRIPT_DIR, 'icon.ico'),
]

def get_app_icon_path():
    for candidate in APP_ICON_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return ''


# Nazwa pliku z ikoną podmenu
MENU_ICON_SOURCE = "app_icon.ico"

ICON_IMAGE = None

def load_header_icon(size=(48, 48)):
    global ICON_IMAGE
    icon_path = get_app_icon_path()
    if not icon_path or not PIL_AVAILABLE:
        return None
    try:
        image = Image.open(icon_path)
        image = image.resize(size, Image.LANCZOS)
        ICON_IMAGE = ImageTk.PhotoImage(image)
        return ICON_IMAGE
    except Exception:
        return None

def convert_png_to_ico_fallback(png_path, ico_path):
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
        return True
    except ImportError:
        try:
            ico_header = struct.pack('<HHH', 0, 1, 1)
            icon_dir_entry = struct.pack('<BBBBHHII', 32, 32, 0, 0, 1, 32, 4160, 22)
            bitmap_info_header = struct.pack('<IiiHHIIiiii', 40, 32, 64, 1, 32, 0, 0, 0, 0, 0, 0)
            
            pixel_data = b''
            for y in range(32):
                for x in range(32):
                    if 6 <= x <= 25 and 6 <= y <= 25:
                        pixel_data += struct.pack('<BBBB', 204, 112, 38, 255)
                    else:
                        pixel_data += struct.pack('<BBBB', 0, 0, 0, 0)
                        
            with open(ico_path, 'wb') as f:
                f.write(ico_header)
                f.write(icon_dir_entry)
                f.write(bitmap_info_header)
                f.write(pixel_data)
            return True
        except Exception:
            return False

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

def build_command_string(app_path, current_executable=None, is_frozen=False, python_mode='console'):
    absolute_path = os.path.abspath(app_path)
    if absolute_path.lower().endswith('.py'):
        if python_mode == 'windowed':
            preferred_executable = shutil.which('pythonw')
            if preferred_executable and os.path.exists(preferred_executable):
                return f'"{preferred_executable}" "{absolute_path}"'
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
                    return f'"{executable}" "{absolute_path}"'
            return f'"{current_executable or sys.executable}" "{absolute_path}"'
        return f'"{current_executable or sys.executable}" "{absolute_path}"'
    return f'"{absolute_path}"'


def add_to_context_menu(label, app_path, icon_path="", python_mode='console'):
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
        messagebox.showerror(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['error_perm'])
        return False
    except Exception as e:
        messagebox.showerror(LANGUAGES[current_lang]['error_generic'], f"{LANGUAGES[current_lang]['error_generic']} {e}")
        return False

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
    except Exception as e:
        messagebox.showerror(LANGUAGES[current_lang]['error_generic'], f"{LANGUAGES[current_lang]['error_generic']} {e}")
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


class ManageWindow(tk.Toplevel):
    def __init__(self, parent, lang_switch_callback):
        super().__init__(parent)
        self.lang_switch_callback = lang_switch_callback
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        self.title(LANGUAGES[current_lang]['manage_window_title'])
        self.geometry("500x380")
        self.resizable(False, False)
        self.minsize(420, 320)
        self.grab_set()
        
        icon_path = get_app_icon_path()
        if icon_path:
            self.iconbitmap(default=icon_path)
            
        self.configure(bg='#f3f4f6')

        main_frame = ttk.Frame(self, padding="20 20 20 20", style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.lbl_entries = ttk.Label(main_frame, text=f"{LANGUAGES[current_lang]['entries_label']} '{LANGUAGES[current_lang]['submenu_name']}':", style='Card.TLabel', font=("Segoe UI", 10, "bold"))
        self.lbl_entries.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        list_frame = ttk.Frame(main_frame, style='Card.TFrame')
        list_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 15))
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=self.scrollbar.set, selectmode=tk.SINGLE, font=("Segoe UI", 9), bg='#ffffff', selectbackground='#d8e3f0', selectforeground='#000000', relief=tk.FLAT, bd=0)
        
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        btn_frame = ttk.Frame(main_frame, style='Card.TFrame')
        btn_frame.grid(row=3, column=0, columnspan=2, sticky='ew')

        self.btn_delete = ttk.Button(btn_frame, text=LANGUAGES[current_lang]['delete_selected'], style='Secondary.TButton', command=self.delete_selected)
        self.btn_delete.pack(side=tk.LEFT)

        self.btn_close = ttk.Button(btn_frame, text=LANGUAGES[current_lang]['close'], style='Secondary.TButton', command=self.destroy)
        self.btn_close.pack(side=tk.RIGHT)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        menus = get_installed_menus()
        for item in menus:
            self.listbox.insert(tk.END, item)

    def delete_selected(self):
        try:
            selected_index = self.listbox.curselection()[0]
            selected_label = self.listbox.get(selected_index)
            
            if messagebox.askyesno(LANGUAGES[current_lang]['error_generic'], f"{LANGUAGES[current_lang]['confirm_delete']} '{selected_label}'?"):
                remove_from_context_menu(selected_label)
                messagebox.showinfo(LANGUAGES[current_lang]['success_add'], f"{LANGUAGES[current_lang]['success_delete']} '{selected_label}'")
                self.refresh_list()
        except IndexError:
            messagebox.showwarning(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_select'])

    def update_language(self):
        self.title(LANGUAGES[current_lang]['manage_window_title'])
        self.lbl_entries.config(text=f"{LANGUAGES[current_lang]['entries_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.btn_delete.config(text=LANGUAGES[current_lang]['delete_selected'])
        self.btn_close.config(text=LANGUAGES[current_lang]['close'])
        self.refresh_list()


class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.title(LANGUAGES[current_lang]['about_title'])
        self.resizable(False, False)
        self.grab_set()
        
        icon_path = get_app_icon_path()
        if icon_path:
            self.iconbitmap(default=icon_path)
            
        self.configure(bg='#f0f0f0')

        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        lbl_title = ttk.Label(main_frame, text="Add To Context Menu", font=("Segoe UI", 14, "bold"))
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky='ew')
        
        lbl_version = ttk.Label(main_frame, text="Version 1.2", font=("Segoe UI", 9))
        lbl_version.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky='ew')

        # Description
        desc_lines = LANGUAGES[current_lang]['about_desc'].split('\n')
        for line in desc_lines:
            ttk.Label(main_frame, text=line, font=("Segoe UI", 9)).grid(row=2+desc_lines.index(line), column=0, columnspan=2, sticky='w', pady=2)
        
        ttk.Label(main_frame, text=LANGUAGES[current_lang]['about_created'], font=("Segoe UI", 9)).grid(row=2+len(desc_lines), column=0, columnspan=2, sticky='w', pady=(10, 15))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=3+len(desc_lines), column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Author info
        row_start = 4 + len(desc_lines)
        
        ttk.Label(main_frame, text=LANGUAGES[current_lang]['author_label'], font=("Segoe UI", 9, "bold")).grid(row=row_start, column=0, sticky='w', padx=(0, 10))
        ttk.Label(main_frame, text=LANGUAGES[current_lang]['author_name'], font=("Segoe UI", 9)).grid(row=row_start, column=1, sticky='w')
        
        ttk.Label(main_frame, text=LANGUAGES[current_lang]['mail_label'], font=("Segoe UI", 9, "bold")).grid(row=row_start+1, column=0, sticky='w', padx=(0, 10), pady=2)
        lbl_mail = ttk.Label(main_frame, text=LANGUAGES[current_lang]['mail_address'], font=("Segoe UI", 9), foreground='blue', cursor='hand2')
        lbl_mail.grid(row=row_start+1, column=1, sticky='w', pady=2)
        lbl_mail.bind("<Button-1>", lambda e: self.open_mail())
        
        ttk.Label(main_frame, text=LANGUAGES[current_lang]['github_label'], font=("Segoe UI", 9, "bold")).grid(row=row_start+2, column=0, sticky='w', padx=(0, 10), pady=2)
        lbl_github = ttk.Label(main_frame, text=LANGUAGES[current_lang]['github_url'], font=("Segoe UI", 9), foreground='blue', cursor='hand2')
        lbl_github.grid(row=row_start+2, column=1, sticky='w', pady=2)
        lbl_github.bind("<Button-1>", lambda e: self.open_github())
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row_start+3, column=0, columnspan=2, sticky='ew', pady=15)

        # Close button
        btn_close = ttk.Button(main_frame, text=LANGUAGES[current_lang]['close'], command=self.destroy)
        btn_close.grid(row=row_start+4, column=0, columnspan=2)

    def open_mail(self):
        import webbrowser
        webbrowser.open(f"mailto:{LANGUAGES[current_lang]['mail_address']}")

    def open_github(self):
        import webbrowser
        webbrowser.open(f"https://github.com/{LANGUAGES[current_lang]['github_url']}")

    def update_language(self):
        self.title(LANGUAGES[current_lang]['about_title'])
        # Refresh all widgets
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()


class AppGui:
    def __init__(self, root):
        self.root = root
        self.manage_window = None
        self.about_window = None
        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background='#f3f4f6')
        style.configure('Card.TFrame', background='#ffffff', borderwidth=1, relief='flat')
        style.configure('Header.TFrame', background='#0f4c81')
        style.configure('Status.TFrame', background='#e7ebf0')

        style.configure('TLabel', font=('Segoe UI', 9), background='#f3f4f6', foreground='#333333')
        style.configure('Card.TLabel', font=('Segoe UI', 9), background='#ffffff', foreground='#333333')
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background='#0f4c81', foreground='white')
        style.configure('HeaderSub.TLabel', font=('Segoe UI', 9), background='#0f4c81', foreground='#dce7f5')
        style.configure('Status.TLabel', font=('Segoe UI', 8), background='#e7ebf0', foreground='#4a4a4a')

        style.configure('TEntry', font=('Segoe UI', 9), fieldbackground='#ffffff', bordercolor='#c8c8c8', background='#ffffff')
        style.configure('TButton', font=('Segoe UI', 9, 'bold'), padding=8)
        style.configure('Primary.TButton', foreground='white', background='#0f4c81')
        style.configure('Secondary.TButton', foreground='#333333', background='#e1e3e6')

        style.map('Primary.TButton',
                  foreground=[('pressed', 'white'), ('active', 'white')],
                  background=[('pressed', '#07315a'), ('active', '#0b4d84')])
        style.map('Secondary.TButton',
                  foreground=[('pressed', '#333333'), ('active', '#333333')],
                  background=[('pressed', '#cfd3d8'), ('active', '#d9dde3')])

        self.root.configure(bg='#f3f4f6')

    def create_widgets(self):
        self.root.title(LANGUAGES[current_lang]['window_title'])
        self.root.resizable(False, False)
        self.root.configure(bg='#f3f4f6')

        icon_path = get_app_icon_path()
        if icon_path:
            self.root.iconbitmap(default=icon_path)

        container = ttk.Frame(self.root, padding="20 20 20 20", style='Card.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        icon_image = load_header_icon((48, 48))
        if icon_image:
            ttk.Label(header_frame, image=icon_image, background='#0f4c81').pack(side=tk.LEFT, padx=(15, 10))
        ttk.Label(header_frame, text="Add To Context Menu", style='Header.TLabel').pack(side=tk.LEFT, padx=(10, 10))
        ttk.Label(header_frame, text="Add apps or scripts to the Windows desktop context menu", style='HeaderSub.TLabel').pack(side=tk.LEFT)

        status_frame = ttk.Frame(container, relief=tk.SUNKEN, style='Status.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        lbl_status = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W, style='Status.TLabel')
        lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=4)
        lbl_author = ttk.Label(status_frame, text="by Sebastian Januchowski", anchor=tk.E, style='Status.TLabel')
        lbl_author.pack(side=tk.RIGHT, padx=8, pady=4)

        top_frame = ttk.Frame(container, style='Card.TFrame')
        top_frame.pack(fill=tk.X, pady=(0, 10))

        right_frame = ttk.Frame(top_frame, style='Card.TFrame')
        right_frame.pack(side=tk.RIGHT)

        self.about_btn = ttk.Button(right_frame, text="ℹ️", width=4, style='Secondary.TButton', command=self.show_about)
        self.about_btn.pack(side=tk.RIGHT, padx=(10, 0))

        self.lang_toggle_btn = ttk.Button(right_frame, text="PL", width=6, style='Secondary.TButton', command=self.switch_language)
        self.lang_toggle_btn.pack(side=tk.RIGHT)

        self.lbl_label = ttk.Label(container, text=f"{LANGUAGES[current_lang]['app_label']} '{LANGUAGES[current_lang]['submenu_name']}':", style='Card.TLabel', font=("Segoe UI", 9, "bold"))
        self.lbl_label.pack(anchor=tk.W, pady=(0, 5))
        self.entry_label = ttk.Entry(container)
        self.entry_label.pack(fill=tk.X, pady=(0, 10))

        self.lbl_path = ttk.Label(container, text=LANGUAGES[current_lang]['app_path_label'], style='Card.TLabel', font=("Segoe UI", 9, "bold"))
        self.lbl_path.pack(anchor=tk.W, pady=(0, 5))
        self.frame_path = ttk.Frame(container, style='Card.TFrame')
        self.frame_path.pack(fill=tk.X, pady=(0, 10))

        self.entry_path = ttk.Entry(self.frame_path)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.btn_browse = ttk.Button(self.frame_path, text=LANGUAGES[current_lang]['browse'], style='Secondary.TButton', command=self.browse_app)
        self.btn_browse.pack(side=tk.RIGHT)

        self.lbl_icon = ttk.Label(container, text=LANGUAGES[current_lang]['app_icon_label'], style='Card.TLabel', font=("Segoe UI", 9, "bold"))
        self.lbl_icon.pack(anchor=tk.W, pady=(0, 5))
        self.frame_icon = ttk.Frame(container, style='Card.TFrame')
        self.frame_icon.pack(fill=tk.X, pady=(0, 10))

        self.lbl_python_mode = ttk.Label(container, text=LANGUAGES[current_lang]['python_launch_mode'], style='Card.TLabel', font=("Segoe UI", 9, "bold"))
        self.lbl_python_mode.pack(anchor=tk.W, pady=(0, 5))
        self.python_mode_var = tk.StringVar(value='console')
        self.frame_python_mode = ttk.Frame(container, style='Card.TFrame')
        self.frame_python_mode.pack(fill=tk.X, pady=(0, 15))

        self.console_radio = ttk.Radiobutton(self.frame_python_mode, text=LANGUAGES[current_lang]['python_launch_console'], variable=self.python_mode_var, value='console')
        self.console_radio.pack(side=tk.LEFT, padx=(0, 15))
        self.windowed_radio = ttk.Radiobutton(self.frame_python_mode, text=LANGUAGES[current_lang]['python_launch_windowed'], variable=self.python_mode_var, value='windowed')
        self.windowed_radio.pack(side=tk.LEFT)

        self.entry_icon = ttk.Entry(self.frame_icon)
        self.entry_icon.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.btn_browse_icon = ttk.Button(self.frame_icon, text=LANGUAGES[current_lang]['browse'], style='Secondary.TButton', command=self.browse_icon)
        self.btn_browse_icon.pack(side=tk.RIGHT)

        self.btn_manage = ttk.Button(container, text=LANGUAGES[current_lang]['manage_apps'], style='Primary.TButton', command=self.open_manage_window)
        self.btn_manage.pack(fill=tk.X, pady=(0, 15))

        self.frame_buttons = ttk.Frame(container, style='Card.TFrame')
        self.frame_buttons.pack(fill=tk.X)

        self.btn_submit = ttk.Button(self.frame_buttons, text=LANGUAGES[current_lang]['submit'], style='Primary.TButton', command=self.submit)
        self.btn_submit.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_cancel = ttk.Button(self.frame_buttons, text=LANGUAGES[current_lang]['cancel'], style='Secondary.TButton', command=self.cancel)
        self.btn_cancel.pack(side=tk.LEFT)

        self.btn_exit = ttk.Button(self.frame_buttons, text=LANGUAGES[current_lang]['exit'], style='Secondary.TButton', command=self.root.quit)
        self.btn_exit.pack(side=tk.RIGHT)

    def switch_language(self):
        global current_lang
        current_lang = 'pl' if current_lang == 'en' else 'en'
        self.status_var.set(f"Language changed to {current_lang.upper()}")
        self.update_language()

    def update_language(self):
        self.root.title(LANGUAGES[current_lang]['window_title'])
        self.lang_toggle_btn.config(text="PL" if current_lang == "en" else "EN")
        self.lbl_label.config(text=f"{LANGUAGES[current_lang]['app_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.lbl_path.config(text=LANGUAGES[current_lang]['app_path_label'])
        self.lbl_icon.config(text=LANGUAGES[current_lang]['app_icon_label'])
        self.btn_browse.config(text=LANGUAGES[current_lang]['browse'])
        self.btn_browse_icon.config(text=LANGUAGES[current_lang]['browse'])
        self.lbl_python_mode.config(text=LANGUAGES[current_lang]['python_launch_mode'])
        self.console_radio.config(text=LANGUAGES[current_lang]['python_launch_console'])
        self.windowed_radio.config(text=LANGUAGES[current_lang]['python_launch_windowed'])
        self.btn_manage.config(text=LANGUAGES[current_lang]['manage_apps'])
        self.btn_submit.config(text=LANGUAGES[current_lang]['submit'])
        self.btn_cancel.config(text=LANGUAGES[current_lang]['cancel'])
        self.btn_exit.config(text=LANGUAGES[current_lang]['exit'])
        if self.manage_window and self.manage_window.winfo_exists():
            self.manage_window.update_language()
        if self.about_window and self.about_window.winfo_exists():
            self.about_window.update_language()

    def browse_app(self):
        file_path = filedialog.askopenfilename(
            title=LANGUAGES[current_lang]['choose_app'],
            filetypes=[(LANGUAGES[current_lang]['supported_files'], "*.exe;*.py"), (LANGUAGES[current_lang]['python_scripts'], "*.py"), (LANGUAGES[current_lang]['exe_files'], "*.exe"), (LANGUAGES[current_lang]['all_files'], "*.*")]
        )
        if file_path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, file_path)
            self.status_var.set(f"Selected app: {os.path.basename(file_path)}")

    def browse_icon(self):
        icon_path = filedialog.askopenfilename(
            title=LANGUAGES[current_lang]['choose_icon'],
            filetypes=[(LANGUAGES[current_lang]['icon_files'], "*.ico"), (LANGUAGES[current_lang]['all_files'], "*.*")]
        )
        if icon_path:
            self.entry_icon.delete(0, tk.END)
            self.entry_icon.insert(0, icon_path)
            self.status_var.set(f"Selected icon: {os.path.basename(icon_path)}")

    def submit(self):
        label = self.entry_label.get().strip()
        app_path = self.entry_path.get().strip()
        icon_path = self.entry_icon.get().strip()

        if not label or not app_path:
            messagebox.showwarning(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_fill'])
            return

        python_mode = self.python_mode_var.get() if self.entry_path.get().strip().lower().endswith('.py') else 'console'

        if add_to_context_menu(label, app_path, icon_path, python_mode=python_mode):
            messagebox.showinfo(LANGUAGES[current_lang]['success_add'], f"{LANGUAGES[current_lang]['success_add']} '{label}' {LANGUAGES[current_lang]['submenu_name']}!")
            self.status_var.set(f"Added: {label}")

    def cancel(self):
        label = self.entry_label.get().strip()
        if not label:
            messagebox.showwarning(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_remove_name'])
            return

        if remove_from_context_menu(label):
            messagebox.showinfo(LANGUAGES[current_lang]['success_add'], f"{LANGUAGES[current_lang]['success_delete']} '{label}'.")
            self.status_var.set(f"Removed: {label}")
        else:
            messagebox.showwarning(LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_not_found'])

    def show_about(self):
        if self.about_window and self.about_window.winfo_exists():
            self.about_window.deiconify()
            self.about_window.lift()
        else:
            self.about_window = AboutWindow(self.root)

    def open_manage_window(self):
        if self.manage_window and self.manage_window.winfo_exists():
            self.manage_window.deiconify()
            self.manage_window.lift()
        else:
            self.manage_window = ManageWindow(self.root, self.switch_language)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGui(root)
    root.mainloop()
