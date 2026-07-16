
@echo off
powershell -Command "Start-Process python -ArgumentList '\"%~dp0Add_To_Context_Menu.py\"' -Verb RunAs"
