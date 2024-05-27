# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['frontend.py'],
    pathex=[],
    binaries=[],
    datas=[('F:\system\simple_mosaic_editor\icon.ico', '.'), ('pillow_avif', 'pillow_avif')],
    hiddenimports=['pillow_avif', 'pillow'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Simple Mosaic Editor Trial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['F:\system\simple_mosaic_editor\icon.ico'],
)