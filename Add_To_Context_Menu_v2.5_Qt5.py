import os
import shutil
import struct
import sys
import winreg
import webbrowser

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QFileDialog, QMessageBox, QListWidget, QDialog, QFrame, QComboBox
)

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
        'about_created': "Created with Python and PyQt5",
        'author_label': "Author:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT",
        'management_panel': 'Management Panel:'
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
        'icon_files': 'Pliki ikon (*.ico);;Wszystkie pliki (*.*)',
        'python_launch_mode': 'Tryb uruchamiania Pythona:',
        'python_launch_console': 'Uruchamiaj z konsolą',
        'python_launch_windowed': 'Uruchamiaj bez konsoli',
        'about_title': 'O programie',
        'about_desc': "Proste narzędzie do zarządzania wpisami w menu kontekstowym.\nDodaj swoje ulubione pliki .exe lub .py do menu kontekstowego!",
        'about_created': "Utworzone za pomocą Pythona i PyQt5",
        'author_label': "Autor:",
        'author_name': "Sebastian Januchowski",
        'mail_label': "Mail:",
        'mail_address': "polsoft.its@mail.com",
        'github_label': "GitHub:",
        'github_url': "polsoft-IT",
        'management_panel': 'Panel zarządzania:'
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


class ManageWindow(QDialog):
    entry_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.parent_gui = parent
        self.init_ui()

    def init_ui(self):
        self.resize(400, 350)
        
        icon_path = get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_entries = QLabel()
        self.lbl_entries.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(self.lbl_entries)

        self.listbox = QListWidget()
        layout.addWidget(self.listbox)

        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton()
        self.btn_delete.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.btn_delete)

        btn_layout.addStretch()

        self.btn_close = QPushButton()
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)
        self.update_language()

    def update_language(self):
        self.setWindowTitle(LANGUAGES[current_lang]['manage_window_title'])
        self.lbl_entries.setText(f"{LANGUAGES[current_lang]['entries_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.btn_delete.setText(LANGUAGES[current_lang]['delete_selected'])
        self.btn_close.setText(LANGUAGES[current_lang]['close'])
        self.refresh_list()

    def refresh_list(self):
        self.listbox.clear()
        menus = get_installed_menus()
        self.listbox.addItems(menus)

    def delete_selected(self):
        selected_item = self.listbox.currentItem()
        if not selected_item:
            QMessageBox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_select'])
            return

        selected_label = selected_item.text()
        reply = QMessageBox.question(
            self, 
            LANGUAGES[current_lang]['error_generic'], 
            f"{LANGUAGES[current_lang]['confirm_delete']} '{selected_label}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if remove_from_context_menu(selected_label):
                QMessageBox.information(self, LANGUAGES[current_lang]['success_add'], f"{LANGUAGES[current_lang]['success_delete']} '{selected_label}'")
                self.refresh_list()
                self.entry_changed.emit()


class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(360, 280)
        
        icon_path = get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_title = QLabel("Add To Context Menu")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f4c81;")
        layout.addWidget(self.lbl_title)

        self.lbl_version = QLabel("Version 2.5 (PyQt5)")
        layout.addWidget(self.lbl_version)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)

        self.lbl_created = QLabel()
        layout.addWidget(self.lbl_created)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.lbl_author = QLabel()
        layout.addWidget(self.lbl_author)

        self.lbl_mail = QLabel()
        self.lbl_mail.setStyleSheet("color: blue; text-decoration: underline;")
        self.lbl_mail.setCursor(Qt.PointingHandCursor)
        self.lbl_mail.mousePressEvent = lambda e: webbrowser.open(f"mailto:{LANGUAGES[current_lang]['mail_address']}")
        layout.addWidget(self.lbl_mail)

        self.lbl_github = QLabel()
        self.lbl_github.setStyleSheet("color: blue; text-decoration: underline;")
        self.lbl_github.setCursor(Qt.PointingHandCursor)
        self.lbl_github.mousePressEvent = lambda e: webbrowser.open(f"https://github.com/{LANGUAGES[current_lang]['github_url']}")
        layout.addWidget(self.lbl_github)

        layout.addSpacing(10)
        self.btn_close = QPushButton()
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

        self.update_language()

    def update_language(self):
        self.setWindowTitle(LANGUAGES[current_lang]['about_title'])
        self.lbl_desc.setText(LANGUAGES[current_lang]['about_desc'])
        self.lbl_created.setText(LANGUAGES[current_lang]['about_created'])
        self.lbl_author.setText(f"<b>{LANGUAGES[current_lang]['author_label']}</b> {LANGUAGES[current_lang]['author_name']}")
        self.lbl_mail.setText(f"<b>{LANGUAGES[current_lang]['mail_label']}</b> {LANGUAGES[current_lang]['mail_address']}")
        self.lbl_github.setText(f"<b>{LANGUAGES[current_lang]['github_label']}</b> {LANGUAGES[current_lang]['github_url']}")
        self.btn_close.setText(LANGUAGES[current_lang]['close'])


class AppGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_style()
        self.update_language()
        self.refresh_edit_combo()

    def init_ui(self):
        self.setFixedSize(480, 560)
        
        icon_path = get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header Area
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        
        self.lbl_header_icon = QLabel()
        if icon_path:
            pixmap = QPixmap(icon_path).scaled(35, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_header_icon.setPixmap(pixmap)
            header_layout.addWidget(self.lbl_header_icon)

        header_text_layout = QVBoxLayout()
        lbl_h_title = QLabel("Add To Context Menu")
        lbl_h_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        lbl_h_sub = QLabel("Manage context menu applications")
        lbl_h_sub.setStyleSheet("font-size: 9px; color: #dce7f5;")
        header_text_layout.addWidget(lbl_h_title)
        header_text_layout.addWidget(lbl_h_sub)
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        main_layout.addWidget(header_widget)

        # Top bar (Lang / About)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        self.btn_lang = QPushButton("PL")
        self.btn_lang.setFixedWidth(50)
        self.btn_lang.clicked.connect(self.switch_language)
        self.btn_about = QPushButton("ℹ️")
        self.btn_about.setFixedWidth(40)
        self.btn_about.clicked.connect(self.show_about)
        top_bar_layout.addWidget(self.btn_lang)
        top_bar_layout.addWidget(self.btn_about)
        main_layout.addLayout(top_bar_layout)

        # [Sugestia 1] PANEL ZARZĄDZANIA NA GÓRZE
        self.lbl_management = QLabel()
        self.lbl_management.setStyleSheet("font-weight: bold; color: #0f4c81; font-size: 12px;")
        main_layout.addWidget(self.lbl_management)

        mgmt_frame = QFrame()
        mgmt_frame.setObjectName("ManagementPanel")
        mgmt_frame.setFrameShape(QFrame.StyledPanel)
        mgmt_layout = QHBoxLayout(mgmt_frame)
        mgmt_layout.setContentsMargins(10, 10, 10, 10)

        self.combo_edit = QComboBox()
        self.combo_edit.setMinimumWidth(200)
        self.combo_edit.currentIndexChanged.connect(self.load_selected_entry_to_form)
        mgmt_layout.addWidget(self.combo_edit)

        self.btn_manage = QPushButton()
        self.btn_manage.clicked.connect(self.open_manage_window)
        mgmt_layout.addWidget(self.btn_manage)
        
        main_layout.addWidget(mgmt_frame)
        
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Form Inputs
        self.lbl_label = QLabel()
        self.lbl_label.setStyleSheet("font-weight: bold;")
        self.entry_label = QLineEdit()
        main_layout.addWidget(self.lbl_label)
        main_layout.addWidget(self.entry_label)

        self.lbl_path = QLabel()
        self.lbl_path.setStyleSheet("font-weight: bold;")
        path_layout = QHBoxLayout()
        self.entry_path = QLineEdit()
        self.btn_browse_path = QPushButton()
        self.btn_browse_path.clicked.connect(self.browse_app)
        path_layout.addWidget(self.entry_path)
        path_layout.addWidget(self.btn_browse_path)
        main_layout.addWidget(self.lbl_path)
        main_layout.addLayout(path_layout)

        # Launch arguments
        self.lbl_args = QLabel()
        self.lbl_args.setStyleSheet("font-weight: bold;")
        self.entry_args = QLineEdit()
        main_layout.addWidget(self.lbl_args)
        main_layout.addWidget(self.entry_args)

        self.lbl_icon = QLabel()
        self.lbl_icon.setStyleSheet("font-weight: bold;")
        icon_layout = QHBoxLayout()
        self.entry_icon = QLineEdit()
        self.btn_browse_icon = QPushButton()
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        icon_layout.addWidget(self.entry_icon)
        icon_layout.addWidget(self.btn_browse_icon)
        main_layout.addWidget(self.lbl_icon)
        main_layout.addLayout(icon_layout)

        # Python Launch Mode Radiobuttons
        self.lbl_python_mode = QLabel()
        self.lbl_python_mode.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(self.lbl_python_mode)

        radio_layout = QHBoxLayout()
        self.radio_group = QButtonGroup(central_widget)
        self.console_radio = QRadioButton()
        self.console_radio.setChecked(True)
        self.windowed_radio = QRadioButton()
        self.radio_group.addButton(self.console_radio, 0)
        self.radio_group.addButton(self.windowed_radio, 1)
        radio_layout.addWidget(self.console_radio)
        radio_layout.addWidget(self.windowed_radio)
        radio_layout.addStretch()
        main_layout.addLayout(radio_layout)

        main_layout.addSpacing(10)

        # [Sugestia 1] NOWY ERGONOMICZNY UKŁAD DOLNYCH PRZYCISKÓW AKCJI
        bottom_layout = QHBoxLayout()
        
        self.btn_exit = QPushButton()
        self.btn_exit.clicked.connect(self.close)
        bottom_layout.addWidget(self.btn_exit)

        bottom_layout.addStretch()

        self.btn_clear = QPushButton()
        self.btn_clear.clicked.connect(self.clear_form)
        bottom_layout.addWidget(self.btn_clear)

        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("PrimaryButton")
        self.btn_submit.clicked.connect(self.submit)
        bottom_layout.addWidget(self.btn_submit)

        main_layout.addLayout(bottom_layout)

        # Status Bar
        self.statusBar().showMessage("Ready")

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f3f4f6; }
            QWidget#HeaderWidget { background-color: #0f4c81; border-radius: 4px; }
            QFrame#ManagementPanel { background-color: #e5e7eb; border: 1px solid #d1d5db; border-radius: 6px; }
            QLabel { font-family: 'Segoe UI'; font-size: 11px; color: #333333; }
            QLineEdit { background-color: white; border: 1px solid #c8c8c8; border-radius: 4px; padding: 4px; font-size: 11px; }
            QPushButton { font-family: 'Segoe UI'; font-size: 11px; font-weight: bold; background-color: #e1e3e6; border: none; border-radius: 4px; padding: 6px 12px; }
            QPushButton:hover { background-color: #d9dde3; }
            QPushButton:pressed { background-color: #cfd3d8; }
            QPushButton#PrimaryButton { background-color: #0f4c81; color: white; }
            QPushButton#PrimaryButton:hover { background-color: #0b4d84; }
            QPushButton#PrimaryButton:pressed { background-color: #07315a; }
            QComboBox { background-color: white; border: 1px solid #c8c8c8; border-radius: 4px; padding: 4px; font-family: 'Segoe UI'; font-size: 11px; }
            QComboBox::drop-down { border: none; }
            QRadioButton { font-family: 'Segoe UI'; font-size: 11px; }
            QStatusBar { background-color: #e7ebf0; font-family: 'Segoe UI'; font-size: 10px; color: #4a4a4a; }
        """)

    def switch_language(self):
        global current_lang
        current_lang = 'pl' if current_lang == 'en' else 'en'
        self.statusBar().showMessage(f"Language changed to {current_lang.upper()}", 3000)
        self.update_language()

    def update_language(self):
        self.setWindowTitle(LANGUAGES[current_lang]['window_title'])
        self.btn_lang.setText("PL" if current_lang == "en" else "EN")
        self.lbl_management.setText(LANGUAGES[current_lang]['management_panel'])
        self.lbl_label.setText(f"{LANGUAGES[current_lang]['app_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.lbl_path.setText(LANGUAGES[current_lang]['app_path_label'])
        self.lbl_args.setText(LANGUAGES[current_lang]['app_args_label'])
        self.lbl_icon.setText(LANGUAGES[current_lang]['app_icon_label'])
        self.btn_browse_path.setText(LANGUAGES[current_lang]['browse'])
        self.btn_browse_icon.setText(LANGUAGES[current_lang]['browse'])
        self.lbl_python_mode.setText(LANGUAGES[current_lang]['python_launch_mode'])
        self.console_radio.setText(LANGUAGES[current_lang]['python_launch_console'])
        self.windowed_radio.setText(LANGUAGES[current_lang]['python_launch_windowed'])
        self.btn_manage.setText(LANGUAGES[current_lang]['manage_apps'])
        self.btn_submit.setText(LANGUAGES[current_lang]['submit'])
        self.btn_clear.setText(LANGUAGES[current_lang]['clear'])
        self.btn_exit.setText(LANGUAGES[current_lang]['exit'])
        self.refresh_edit_combo()

    def refresh_edit_combo(self):
        self.combo_edit.blockSignals(True)
        self.combo_edit.clear()
        self.combo_edit.addItem(LANGUAGES[current_lang]['edit_placeholder'])
        
        menus = get_installed_menus()
        self.combo_edit.addItems(menus)
        
        # Zablokowanie placeholderu (index 0) przed ponownym kliknięciem
        self.combo_edit.setItemData(0, 0, Qt.UserRole - 1)
        
        self.combo_edit.blockSignals(False)

    def load_selected_entry_to_form(self, index):
        if index <= 0:
            return
            
        selected_label = self.combo_edit.currentText()
        details = get_entry_details(selected_label)
        
        self.entry_label.setText(selected_label)
        self.entry_path.setText(details["path"])
        self.entry_args.setText(details["args"])
        self.entry_icon.setText(details["icon"])
        
        if details["windowed"]:
            self.windowed_radio.setChecked(True)
        else:
            self.console_radio.setChecked(True)
            
        self.statusBar().showMessage(f"Loaded entry: {selected_label}", 4000)

    def browse_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, LANGUAGES[current_lang]['choose_app'], "", LANGUAGES[current_lang]['supported_files']
        )
        if file_path:
            self.entry_path.setText(os.path.normpath(file_path))
            self.statusBar().showMessage(f"Selected app: {os.path.basename(file_path)}", 4000)

    def browse_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(
            self, LANGUAGES[current_lang]['choose_icon'], "", LANGUAGES[current_lang]['icon_files']
        )
        if icon_path:
            self.entry_icon.setText(os.path.normpath(icon_path))
            self.statusBar().showMessage(f"Selected icon: {os.path.basename(icon_path)}", 4000)

    def clear_form(self):
        self.entry_label.clear()
        self.entry_path.clear()
        self.entry_args.clear()
        self.entry_icon.clear()
        self.console_radio.setChecked(True)
        self.refresh_edit_combo()
        self.statusBar().showMessage("Form cleared", 3000)

    def submit(self):
        label = self.entry_label.text().strip()
        app_path = self.entry_path.text().strip()
        args = self.entry_args.text().strip()
        icon_path = self.entry_icon.text().strip()

        if not label or not app_path:
            QMessageBox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_fill'])
            return

        # [Sugestia 1 z wersji v2] Walidacja pliku aplikacji
        if not os.path.exists(app_path):
            QMessageBox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_file_not_found'])
            return

        # [Sugestia 5 z wersji v2] Automatyczna walidacja rozszerzeń plików ikony (.ico)
        if icon_path:
            if not os.path.exists(icon_path) or not icon_path.lower().endswith('.ico'):
                QMessageBox.warning(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['warning_icon_invalid'])
                return

        python_mode = 'windowed' if (app_path.lower().endswith('.py') and self.windowed_radio.isChecked()) else 'console'

        result = add_to_context_menu(label, app_path, icon_path, python_mode=python_mode, args=args)
        if result is True:
            QMessageBox.information(
                self, 
                LANGUAGES[current_lang]['success_add'], 
                f"{LANGUAGES[current_lang]['success_add']} '{label}' {LANGUAGES[current_lang]['submenu_name']}!"
            )
            self.statusBar().showMessage(f"Saved: {label}", 5000)
            
            # [Sugestia 6 z wersji v2] Automatyczne czyszczenie po pomyślnym dodaniu
            self.clear_form()
        elif result == "perm_error":
            QMessageBox.critical(self, LANGUAGES[current_lang]['error_generic'], LANGUAGES[current_lang]['error_perm'])
        else:
            QMessageBox.critical(self, LANGUAGES[current_lang]['error_generic'], f"{LANGUAGES[current_lang]['error_generic']} {result}")

    def show_about(self):
        dlg = AboutWindow(self)
        dlg.exec_()

    def open_manage_window(self):
        dlg = ManageWindow(self)
        # [Sugestia 3 z wersji v2] Odświeżanie sygnałami
        dlg.entry_changed.connect(self.refresh_edit_combo)
        dlg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AppGui()
    gui.show()
    sys.exit(app.exec_())