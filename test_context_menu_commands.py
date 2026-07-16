import importlib.util
import pathlib
import unittest
from unittest.mock import patch

MODULE_PATH = pathlib.Path(__file__).with_name("Add_To_Context_Menu.py")
spec = importlib.util.spec_from_file_location("add_to_context_menu", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CommandBuilderTests(unittest.TestCase):
    def test_python_script_uses_python_launcher_when_frozen(self):
        with patch("shutil.which", side_effect=lambda name: "C:/Python311/py.exe" if name == "py" else None), patch(
            "os.path.exists", side_effect=lambda path: path == "C:/Python311/py.exe"
        ):
            command = module.build_command_string(
                r"C:\Apps\demo.py",
                current_executable=r"C:\Apps\Add_To_Context_Menu.exe",
                is_frozen=True,
            )
        self.assertEqual(command, '"C:/Python311/py.exe" "C:\\Apps\\demo.py"')

    def test_exe_target_uses_direct_path(self):
        command = module.build_command_string(r"C:\Apps\demo.exe")
        self.assertEqual(command, '"C:\\Apps\\demo.exe"')

    def test_python_script_can_run_without_console(self):
        with patch("shutil.which", side_effect=lambda name: "C:/Python311/pythonw.exe" if name == "pythonw" else None), patch(
            "os.path.exists", side_effect=lambda path: path == "C:/Python311/pythonw.exe"
        ):
            command = module.build_command_string(
                r"C:\Apps\demo.py",
                current_executable=r"C:\Apps\Add_To_Context_Menu.exe",
                is_frozen=True,
                python_mode="windowed",
            )
        self.assertEqual(command, '"C:/Python311/pythonw.exe" "C:\\Apps\\demo.py"')


if __name__ == "__main__":
    unittest.main()
