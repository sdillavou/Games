# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['/Users/Sam/Documents/GitHub/Games/Boxy'],
             binaries=[],
             datas=[('slide.wav', '.'), ('boom.wav', '.'), ('protection.wav', '.'), ('tnt_sound2.wav', '.'), ('blip.wav', '.'), ('ouch.wav', '.'), ('footstep.wav', '.'), ('power_down.wav', '.'), ('thud.wav', '.'), ('box_break0.wav', '.'), ('box_break1.wav', '.'), ('box_break2.wav', '.'), ('box_break3.wav', '.'), ('box_break4.wav', '.'), ('box_break5.wav', '.'), ('box_break6.wav', '.'), ('freesansbold.ttf', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['pygame'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += Tree("/Users/Sam/anaconda3/lib/python3.7/site-packages/pygame/", prefix= "pygame")
a.datas += Tree("/Users/Sam/anaconda3/lib/python3.7/xml/", prefix= "xml")

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
            
             

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='run',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='run')
