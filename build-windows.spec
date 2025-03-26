# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Include the 'gui' and 'storage' directories
added_files = [
    ('.\\src\\gui', 'gui'),
    ('.\\storage', 'storage'),
]

hidden_imports = [
    'clr',
    'sklearn.tree._partitioner',
    'scipy.special._cdflib',
]

a = Analysis(
    ['.\\src\\index.py'],
    pathex=['.\\src'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NLP Toolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    icon='.\\src\\assets\\logo.ico',
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect everything into a directory (one-dir mode)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NLP Toolkit',
)