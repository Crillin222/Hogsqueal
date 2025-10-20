# Hobgoblin.spec
from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Tree
import certifi

# Coleta tudo do PySide6 (plugins, DLLs)
pyside6_datas, pyside6_binaries, pyside6_hidden = collect_all('PySide6')

datas = []
binaries = []
hiddenimports = []

datas += pyside6_datas
binaries += pyside6_binaries
hiddenimports += pyside6_hidden

# Inclui recursos
resources_tree = Tree('resources', prefix='resources')

# Inclui bundle de certificados (HTTPS)
datas += [(certifi.where(), 'certifi')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Hobgoblin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # True se quiser console para debug
    icon='hobgoblin.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    resources_tree,  # <- adiciona a pasta resources inteira
    strip=False,
    upx=False,
    name='Hobgoblin'
)

