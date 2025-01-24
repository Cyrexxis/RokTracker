# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.config

PyInstaller.config.CONF['distpath'] = "./publish"

block_cipher = None

a = Analysis(['.\\main.py'],
             pathex=['.'],
             binaries=None,
             datas=[('.\\gui_frontend\\dist', 'dist')],
             hiddenimports=['clr'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

splash = Splash('splashscreen.png',
                binaries=a.binaries,
                datas=a.datas)

exe = EXE(pyz,
          splash,
          a.scripts,
          exclude_binaries=True,
          name='RoK Tracker Suite',
          debug=False,
          strip=True,
          icon='.\\gui_frontend\\public\\favicon.ico',
          upx=True,
          console=False)

coll = COLLECT(exe,
               splash.binaries,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='RoK Tracker Suite')