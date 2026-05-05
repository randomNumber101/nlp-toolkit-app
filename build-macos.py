import os
import py2app
import shutil

from distutils.core import setup

def tree(src):
    return [(root, map(lambda f: os.path.join(root, f), files))
        for (root, dirs, files) in os.walk(os.path.normpath(src))]


if os.path.exists('build'):
    shutil.rmtree('build')

if os.path.exists('dist/index.app'):
    shutil.rmtree('dist/index.app')

ENTRY_POINT = ['src/index.py']

# This correctly includes both the built frontend and storage data
DATA_FILES = tree('src/gui') + tree('storage')
OPTIONS = {
    'argv_emulation': False,
    'strip': False,
    'iconfile': 'src/assets/logo.icns',
    'packages': ['WebKit', 'Foundation', 'webview', 'pandas', 'spacy', 'torch'], # Added key packages to ensure inclusion
    'plist': {
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleName': 'NLP4Edu',
        'CFBundleDisplayName': 'NLP4Edu',
        'CFBundleIdentifier': 'com.yourdomain.nlp4edu', # It's good practice to set a unique identifier
        'CFBundleVersion': '1.3.0',
        'CFBundlePackageType': 'APPL',
    },
    'resources': DATA_FILES
}

setup(
    app=ENTRY_POINT,
    name='NLP4Edu',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)