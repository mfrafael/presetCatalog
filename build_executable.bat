@echo off
echo Criando executavel do Preset Catalog...
echo.

REM Ativar o ambiente virtual
call .venv\Scripts\activate

REM Parar qualquer instancia em execucao
taskkill /f /im PresetCatalog.exe >nul 2>&1

REM Aguardar um pouco para garantir que o processo foi finalizado
timeout /t 2 >nul

REM Limpar builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Criar o executavel usando o arquivo .spec
pyinstaller preset_catalog.spec

echo.
if exist dist\PresetCatalog.exe (
    echo Executavel criado com sucesso em: dist\PresetCatalog.exe
    echo.
    echo Voce pode enviar a pasta 'dist' completa para seus amigos.
    echo O arquivo PresetCatalog.exe estara dentro dela.
) else (
    echo Erro ao criar o executavel!
)

echo.
pause
