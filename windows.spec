# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.config

PyInstaller.config.CONF['distpath'] = "./publish"

block_cipher = None

a = Analysis(['.\\main.py'],
             pathex=['.'],
             binaries=None,
             datas=[('.\\dist', 'dist')],
             hiddenimports=['clr'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='RoK Tracker Suite',
          debug=False,
          strip=True,
          icon='.\\public\\favicon.ico',
          upx=True,
          console=False)
