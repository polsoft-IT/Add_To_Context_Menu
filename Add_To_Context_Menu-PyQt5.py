import os
import shutil
import struct
import sys
import winreg
import webbrowser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, 
    QListWidget, QDialog, QFileDialog, QMessageBox, QFrame, QGridLayout
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

# Słowniki językowe
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
        'supported_files': 'Supported files (*.exe *.py)',
        'python_scripts': 'Python scripts (*.py)',
        'exe_files': 'Executable files (*.exe)',
        'all_files': 'All files (*.*)',
        'choose_icon': 'Choose an icon file',
        'icon_files': 'Icon files (*.ico)',
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
        'supported_files': 'Obsługiwane pliki (*.exe *.py)',
        'python_scripts': 'Skrypty Python (*.py)',
        'exe_files': 'Pliki wykonywalne (*.exe)',
        'all_files': 'Wszystkie pliki (*.*)',
        'choose_icon': 'Wybierz plik ikony',
        'icon_files': 'Pliki ikon (*.ico)',
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
        'github_url': "polsoft-IT"
    }
}

current_lang = 'en'
MENU_ICON_SOURCE = "app_icon.ico"

# Style arkusza CSS dla PyQt (Modern Dark/Light Theme)
QSS_STYLE = """
    QMainWindow, QDialog {
        background-color: #f8f9fa;
    }
    QLabel {
        font-family: "Segoe UI";
        font-size: 12px;
        color: #333333;
    }
    QLineEdit {
        border: 1px solid #ccd1d9;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        font-family: "Segoe UI";
    }
    QLineEdit:focus {
        border: 1px solid #3b82f6;
    }
    QPushButton {
        background-color: #e4e6eb;
        color: #333333;
        border: none;
        border-radius: 4px;
        padding: 8px 14px;
        font-family: "Segoe UI";
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #d8dadf;
    }
    QPushButton:pressed {
        background-color: #ccd0d5;
    }
    QPushButton#primaryBtn {
        background-color: #0f4c81;
        color: #ffffff;
    }
    QPushButton#primaryBtn:hover {
        background-color: #0b3c66;
    }
    QPushButton#primaryBtn:pressed {
        background-color: #082d4d;
    }
    QRadioButton {
        font-family: "Segoe UI";
        font-size: 12px;
    }
    QListWidget {
        border: 1px solid #ccd1d9;
        border-radius: 4px;
        background-color: #ffffff;
        padding: 5px;
    }
    QFrame#headerFrame {
        background-color: #0f4c81;
        border-radius: 6px;
    }
    QLabel#headerTitle {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
    }
    QLabel#headerSub {
        color: #dce7f5;
        font-size: 11px;
    }
"""

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
        return "perm"
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
    except Exception as e:
        return str(e)

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


# --- OKNA DIALOGOWE ---

class ManageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(LANGUAGES[current_lang]['manage_window_title'])
        self.setFixedSize(450, 350)
        self.setModal(True)

        layout = QVBoxLayout()
        
        self.lbl_entries = QLabel()
        self.lbl_entries.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_entries)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton()
        self.btn_delete.setObjectName("primaryBtn")
        self.btn_delete.clicked.connect(self.delete_selected)
        
        self.btn_close = QPushButton()
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_texts()

    def update_texts(self):
        self.setWindowTitle(LANGUAGES[current_lang]['manage_window_title'])
        self.lbl_entries.setText(f"{LANGUAGES[current_lang]['entries_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.btn_delete.setText(LANGUAGES[current_lang]['delete_selected'])
        self.btn_close.setText(LANGUAGES[current_lang]['close'])
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        menus = get_installed_menus()
        self.list_widget.addItems(menus)

    def delete_selected(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", LANGUAGES[current_lang]['warning_select'])
            return
        
        label = selected_items[0].text()
        reply = QMessageBox.question(
            self, 
            LANGUAGES[current_lang]['about_title'], 
            f"{LANGUAGES[current_lang]['confirm_delete']} '{label}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            res = remove_from_context_menu(label)
            if res is True:
                QMessageBox.information(self, "Success", f"{LANGUAGES[current_lang]['success_delete']} '{label}'")
                self.refresh_list()
            else:
                QMessageBox.critical(self, "Error", f"{LANGUAGES[current_lang]['error_generic']} {res}")


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(LANGUAGES[current_lang]['about_title'])
        self.setFixedSize(380, 280)
        self.setModal(True)

        layout = QVBoxLayout()

        lbl_title = QLabel("Add To Context Menu")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f4c81;")
        layout.addWidget(lbl_title)

        lbl_ver = QLabel("Version 1.5 (PyQt5 Edition)")
        lbl_ver.setStyleSheet("color: #666;")
        layout.addWidget(lbl_ver)

        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)

        grid = QGridLayout()
        self.lbl_auth_title = QLabel()
        self.lbl_auth_title.setStyleSheet("font-weight: bold;")
        lbl_auth_val = QLabel(LANGUAGES[current_lang]['author_name'])
        
        self.lbl_mail_title = QLabel()
        self.lbl_mail_title.setStyleSheet("font-weight: bold;")
        lbl_mail_val = QLabel(f"<a href='mailto:{LANGUAGES[current_lang]['mail_address']}'>{LANGUAGES[current_lang]['mail_address']}</a>")
        lbl_mail_val.setOpenExternalLinks(True)

        self.lbl_git_title = QLabel()
        self.lbl_git_title.setStyleSheet("font-weight: bold;")
        lbl_git_val = QLabel(f"<a href='https://github.com/{LANGUAGES[current_lang]['github_url']}'>{LANGUAGES[current_lang]['github_url']}</a>")
        lbl_git_val.setOpenExternalLinks(True)

        grid.addWidget(self.lbl_auth_title, 0, 0)
        grid.addWidget(lbl_auth_val, 0, 1)
        grid.addWidget(self.lbl_mail_title, 1, 0)
        grid.addWidget(lbl_mail_val, 1, 1)
        grid.addWidget(self.lbl_git_title, 2, 0)
        grid.addWidget(lbl_git_val, 2, 1)
        layout.addLayout(grid)

        layout.addStretch()
        btn_close = QPushButton()
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.btn_close = btn_close
        self.setLayout(layout)
        self.update_texts()

    def update_texts(self):
        self.setWindowTitle(LANGUAGES[current_lang]['about_title'])
        self.lbl_desc.setText(LANGUAGES[current_lang]['about_desc'])
        self.lbl_auth_title.setText(LANGUAGES[current_lang]['author_label'])
        self.lbl_mail_title.setText(LANGUAGES[current_lang]['mail_label'])
        self.lbl_git_title.setText(LANGUAGES[current_lang]['github_label'])
        self.btn_close.setText(LANGUAGES[current_lang]['close'])


# --- GŁÓWNE OKNO APLIKACJI ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(560, 560)
        
        # Główny widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 1. Nagłówek (Header)
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)

        self.lbl_header_title = QLabel("Add To Context Menu")
        self.lbl_header_title.setObjectName("headerTitle")
        self.lbl_header_sub = QLabel("Add apps or scripts to the Windows desktop context menu")
        self.lbl_header_sub.setObjectName("headerSub")

        header_layout.addWidget(self.lbl_header_title)
        header_layout.addWidget(self.lbl_header_sub)
        main_layout.addWidget(header_frame)

        # Przycisk zmiany języka i o programie
        top_bar = QHBoxLayout()
        self.btn_lang = QPushButton("PL")
        self.btn_lang.setFixedWidth(60)
        self.btn_lang.clicked.connect(self.switch_language)
        
        self.btn_about = QPushButton("ℹ️")
        self.btn_about.setFixedWidth(40)
        self.btn_about.clicked.connect(self.show_about)
        
        top_bar.addStretch()
        top_bar.addWidget(self.btn_lang)
        top_bar.addWidget(self.btn_about)
        main_layout.addLayout(top_bar)

        # 2. Formularz wprowadzania danych
        # Nazwa aplikacji
        self.lbl_app = QLabel()
        self.lbl_app.setStyleSheet("font-weight: bold;")
        self.entry_label = QLineEdit()
        main_layout.addWidget(self.lbl_app)
        main_layout.addWidget(self.entry_label)

        # Ścieżka aplikacji
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

        # Ścieżka ikony
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

        # Tryb uruchamiania Python (Radio)
        self.lbl_py_mode = QLabel()
        self.lbl_py_mode.setStyleSheet("font-weight: bold;")
        self.radio_console = QRadioButton()
        self.radio_windowed = QRadioButton()
        self.radio_console.setChecked(True)
        
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_console)
        self.radio_group.addButton(self.radio_windowed)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_console)
        radio_layout.addWidget(self.radio_windowed)
        radio_layout.addStretch()

        main_layout.addWidget(self.lbl_py_mode)
        main_layout.addLayout(radio_layout)

        # 3. Zarządzanie / Przeglądaj wpisy
        self.btn_manage = QPushButton()
        self.btn_manage.setObjectName("primaryBtn")
        self.btn_manage.clicked.connect(self.open_manage)
        main_layout.addWidget(self.btn_manage)

        main_layout.addSpacing(10)

        # 4. Dolne przyciski akcji
        action_layout = QHBoxLayout()
        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("primaryBtn")
        self.btn_submit.clicked.connect(self.submit)
        
        self.btn_cancel = QPushButton()
        self.btn_cancel.clicked.connect(self.cancel)
        
        self.btn_exit = QPushButton()
        self.btn_exit.clicked.connect(self.close)

        action_layout.addWidget(self.btn_submit)
        action_layout.addWidget(self.btn_cancel)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_exit)
        main_layout.addLayout(action_layout)

        # Pasek statusu na dole
        self.statusBar().showMessage("Ready")

        self.update_texts()

    def update_texts(self):
        self.setWindowTitle(LANGUAGES[current_lang]['window_title'])
        self.btn_lang.setText("PL" if current_lang == "en" else "EN")
        self.lbl_app.setText(f"{LANGUAGES[current_lang]['app_label']} '{LANGUAGES[current_lang]['submenu_name']}':")
        self.lbl_path.setText(LANGUAGES[current_lang]['app_path_label'])
        self.lbl_icon.setText(LANGUAGES[current_lang]['app_icon_label'])
        self.btn_browse_path.setText(LANGUAGES[current_lang]['browse'])
        self.btn_browse_icon.setText(LANGUAGES[current_lang]['browse'])
        self.lbl_py_mode.setText(LANGUAGES[current_lang]['python_launch_mode'])
        self.radio_console.setText(LANGUAGES[current_lang]['python_launch_console'])
        self.radio_windowed.setText(LANGUAGES[current_lang]['python_launch_windowed'])
        self.btn_manage.setText(LANGUAGES[current_lang]['manage_apps'])
        self.btn_submit.setText(LANGUAGES[current_lang]['submit'])
        self.btn_cancel.setText(LANGUAGES[current_lang]['cancel'])
        self.btn_exit.setText(LANGUAGES[current_lang]['exit'])

    def switch_language(self):
        global current_lang
        current_lang = 'pl' if current_lang == 'en' else 'en'
        self.statusBar().showMessage(f"Language changed to {current_lang.upper()}")
        self.update_texts()

    def browse_app(self):
        file_filter = f"{LANGUAGES[current_lang]['supported_files']};;{LANGUAGES[current_lang]['python_scripts']};;{LANGUAGES[current_lang]['exe_files']};;{LANGUAGES[current_lang]['all_files']}"
        file_path, _ = QFileDialog.getOpenFileName(self, LANGUAGES[current_lang]['choose_app'], "", file_filter)
        if file_path:
            self.entry_path.setText(file_path)
            self.statusBar().showMessage(f"Selected: {os.path.basename(file_path)}")

    def browse_icon(self):
        file_filter = f"{LANGUAGES[current_lang]['icon_files']};;{LANGUAGES[current_lang]['all_files']}"
        icon_path, _ = QFileDialog.getOpenFileName(self, LANGUAGES[current_lang]['choose_icon'], "", file_filter)
        if icon_path:
            self.entry_icon.setText(icon_path)
            self.statusBar().showMessage(f"Selected icon: {os.path.basename(icon_path)}")

    def submit(self):
        label = self.entry_label.text().strip()
        app_path = self.entry_path.text().strip()
        icon_path = self.entry_icon.text().strip()

        if not label or not app_path:
            QMessageBox.warning(self, "Warning", LANGUAGES[current_lang]['warning_fill'])
            return

        python_mode = 'windowed' if self.radio_windowed.isChecked() else 'console'
        res = add_to_context_menu(label, app_path, icon_path, python_mode=python_mode)

        if res is True:
            QMessageBox.information(
                self, 
                LANGUAGES[current_lang]['success_add'], 
                f"{LANGUAGES[current_lang]['success_add']} '{label}' -> {LANGUAGES[current_lang]['submenu_name']}"
            )
            self.statusBar().showMessage(f"Added: {label}")
        elif res == "perm":
            QMessageBox.critical(self, "Error", LANGUAGES[current_lang]['error_perm'])
        else:
            QMessageBox.critical(self, "Error", f"{LANGUAGES[current_lang]['error_generic']} {res}")

    def cancel(self):
        label = self.entry_label.text().strip()
        if not label:
            QMessageBox.warning(self, "Warning", LANGUAGES[current_lang]['warning_remove_name'])
            return

        res = remove_from_context_menu(label)
        if res is True:
            QMessageBox.information(self, "Success", f"{LANGUAGES[current_lang]['success_delete']} '{label}'")
            self.statusBar().showMessage(f"Removed: {label}")
        else:
            QMessageBox.critical(self, "Error", f"{LANGUAGES[current_lang]['error_generic']} {res}")

    def open_manage(self):
        dialog = ManageDialog(self)
        dialog.exec_()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()


# --- PUNKT WEJŚCIA (MAIN) ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Unifikacja wyglądu na każdym systemie
    app.setStyleSheet(QSS_STYLE) # Wstrzyknięcie nowoczesnego stylu CSS
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())