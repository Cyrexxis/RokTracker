import ttkbootstrap as ttk
from PyInstaller.utils.hooks import copy_metadata

ttk.__path__[0].replace("\\", "/")

hidden_imports = ['tesserocr.cysignals', 'ttkbootstrap']

added_metadata = []

added_ui_files = [(ttk.__path__[0].replace("\\", "/"), "ttkbootstrap/")] + added_metadata
added_cli_files = [] + added_metadata

scanner_console_a = Analysis(
    ["scanner_console.py"],
    pathex=[],
    binaries=[],
    datas=added_cli_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
scanner_console_pyz = PYZ(scanner_console_a.pure)

scanner_console_exe = EXE(
    scanner_console_pyz,
    scanner_console_a.scripts,
    [],
    exclude_binaries=True,
    name="Scanner (CLI)",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# -----------------------------------------------------

scanner_ui_a = Analysis(
    ["scanner_ui.py"],
    pathex=[],
    binaries=[],
    datas=added_ui_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
scanner_ui_pyz = PYZ(scanner_ui_a.pure)

scanner_ui_exe = EXE(
    scanner_ui_pyz,
    scanner_ui_a.scripts,
    [],
    exclude_binaries=True,
    name="Scanner (GUI)",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# -----------------------------------------------------

coll = COLLECT(
    scanner_console_exe,
    scanner_console_a.binaries,
    scanner_console_a.datas,
    scanner_ui_exe,
    scanner_ui_a.binaries,
    scanner_ui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RoK Tracker",
)
