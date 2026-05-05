# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Include the 'gui' and 'storage' directories using Linux/macOS path separators
added_files = [
    ('src/gui', 'gui'),
    ('storage', 'storage'),
]

# Hidden imports needed by dependencies, without the Windows-specific 'clr'
hidden_imports = [
    'sklearn.tree._partitioner',
    'scipy.special._cdflib',
]

a = Analysis(
    ['src/index.py'],
    pathex=['src'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NLP4Edu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/assets/logo.ico', # PyInstaller can often use .ico on Linux for the window icon
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
    name='NLP4Edu_linux',
)