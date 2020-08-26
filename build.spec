# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('resources/crawler_gui.ui', 'resources'),
                    ('title_logo_rc.py', '.'),
                    ('toolbar_logo_rc.py', '.'),
                    ('resources/eng_logo_squared.png', 'resources'),
                    ('resources/icon.ico', 'resources')
                    ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          bootloader_ignore_signals=False,
          name='PubMed Crawler',
          debug=False,
          strip=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='.\\resources\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
