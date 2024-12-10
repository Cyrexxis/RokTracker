import customtkinter as ctk

ctk.__path__[0].replace("\\", "/")

added_files = [(ctk.__path__[0].replace("\\", "/"), "customtkinter/")]

alliance_console_a = Analysis(
    ["alliance_scanner_console.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
alliance_console_pyz = PYZ(alliance_console_a.pure)

alliance_console_exe = EXE(
    alliance_console_pyz,
    alliance_console_a.scripts,
    [],
    exclude_binaries=True,
    name="Alliance Scanner (CLI)",
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

alliance_ui_a = Analysis(
    ["alliance_scanner_ui.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
alliance_ui_pyz = PYZ(alliance_ui_a.pure)

alliance_ui_exe = EXE(
    alliance_ui_pyz,
    alliance_ui_a.scripts,
    [],
    exclude_binaries=True,
    name="Alliance Scanner (GUI)",
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

honor_console_a = Analysis(
    ["honor_scanner_console.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
honor_console_pyz = PYZ(honor_console_a.pure)

honor_console_exe = EXE(
    honor_console_pyz,
    honor_console_a.scripts,
    [],
    exclude_binaries=True,
    name="Honor Scanner (CLI)",
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

# ------------------------------------------------------

honor_ui_a = Analysis(
    ["honor_scanner_ui.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
honor_ui_pyz = PYZ(honor_ui_a.pure)

honor_ui_exe = EXE(
    honor_ui_pyz,
    honor_ui_a.scripts,
    [],
    exclude_binaries=True,
    name="Honor Scanner (GUI)",
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

# ---------------------------------------------------

kingdom_console_a = Analysis(
    ["kingdom_scanner_console.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
kingdom_console_pyz = PYZ(kingdom_console_a.pure)

kingdom_console_exe = EXE(
    kingdom_console_pyz,
    kingdom_console_a.scripts,
    [],
    exclude_binaries=True,
    name="Kingdom Scanner (CLI)",
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

# --------------------------------------------------

kingdom_ui_a = Analysis(
    ["kingdom_scanner_ui.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
kingdom_ui_pyz = PYZ(kingdom_ui_a.pure)

kingdom_ui_exe = EXE(
    kingdom_ui_pyz,
    kingdom_ui_a.scripts,
    [],
    exclude_binaries=True,
    name="Kingdom Scanner (GUI)",
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

# -------------------------------------------------

seed_console_a = Analysis(
    ["seed_scanner_console.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
seed_console_pyz = PYZ(seed_console_a.pure)

seed_console_exe = EXE(
    seed_console_pyz,
    seed_console_a.scripts,
    [],
    exclude_binaries=True,
    name="Seed Scanner (CLI)",
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

seed_ui_a = Analysis(
    ["seed_scanner_ui.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
seed_ui_pyz = PYZ(seed_ui_a.pure)

seed_ui_exe = EXE(
    seed_ui_pyz,
    seed_ui_a.scripts,
    [],
    exclude_binaries=True,
    name="Seed Scanner (GUI)",
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
    alliance_console_exe,
    alliance_console_a.binaries,
    alliance_console_a.datas,
    alliance_ui_exe,
    alliance_ui_a.binaries,
    alliance_ui_a.datas,
    honor_console_exe,
    honor_console_a.binaries,
    honor_console_a.datas,
    honor_ui_exe,
    honor_ui_a.binaries,
    honor_ui_a.datas,
    kingdom_console_exe,
    kingdom_console_a.binaries,
    kingdom_console_a.datas,
    kingdom_ui_exe,
    kingdom_ui_a.binaries,
    kingdom_ui_a.datas,
    seed_console_exe,
    seed_console_a.binaries,
    seed_console_a.datas,
    seed_ui_exe,
    seed_ui_a.binaries,
    seed_ui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RoK Tracker",
)
