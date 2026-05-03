#!/bin/bash
set -e

echo "=== Build: PresetCatalog AppImage ==="

# Ativar venv
source .venv/bin/activate

# Instalar pyinstaller se necessário
pip install pyinstaller --quiet

# Limpar builds anteriores
rm -rf build dist AppDir PresetCatalog-x86_64.AppImage

# Build com PyInstaller (onedir)
echo "Empacotando com PyInstaller..."
pyinstaller preset_catalog_linux.spec

# Converter ícone .ico -> .png
if command -v magick &>/dev/null; then
    magick "PresetCatalog.ico[0]" PresetCatalog.png
elif command -v convert &>/dev/null; then
    convert "PresetCatalog.ico[0]" PresetCatalog.png
else
    echo "Aviso: ImageMagick não encontrado, AppImage ficará sem ícone"
fi

# Criar estrutura do AppDir
echo "Criando AppDir..."
mkdir -p AppDir
cp -r dist/PresetCatalog/* AppDir/

# AppRun
cat > AppDir/AppRun << 'APPRUN'
#!/bin/bash
HERE=$(dirname "$(readlink -f "$0")")
exec "$HERE/PresetCatalog" "$@"
APPRUN
chmod +x AppDir/AppRun

# Arquivo .desktop
cat > AppDir/PresetCatalog.desktop << 'DESKTOP'
[Desktop Entry]
Name=Preset Catalog
Exec=PresetCatalog
Icon=PresetCatalog
Type=Application
Categories=Graphics;Photography;
DESKTOP

# Copiar ícone se existir
[ -f PresetCatalog.png ] && cp PresetCatalog.png AppDir/

# Baixar appimagetool se necessário
if [ ! -f appimagetool-x86_64.AppImage ]; then
    echo "Baixando appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Criar AppImage (APPIMAGE_EXTRACT_AND_RUN evita precisar de FUSE)
echo "Criando AppImage..."
APPIMAGE_EXTRACT_AND_RUN=1 ./appimagetool-x86_64.AppImage AppDir PresetCatalog-x86_64.AppImage

echo ""
echo "Concluído: PresetCatalog-x86_64.AppImage"
