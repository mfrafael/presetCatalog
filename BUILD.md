# Como Gerar o Executável

Este documento explica como gerar o arquivo executável (.exe) do Preset Catalog.

## Pré-requisitos

1. Python 3.7+ instalado
2. Ambiente virtual ativo (`.venv`)
3. Dependências instaladas:
   ```bash
   pip install PySide6 pyinstaller
   ```

## Método Simples - Script Batch

Execute o arquivo `build_executable.bat`:
```bash
build_executable.bat
```

Este script:
- Ativa o ambiente virtual
- Para processos em execução
- Limpa builds anteriores
- Gera o executável
- Mostra o resultado

## Método Manual

Se preferir executar manualmente:

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Limpar builds anteriores (opcional)
rmdir /s /q build dist

# Gerar executável
pyinstaller preset_catalog.spec
```

## Resultado

O executável será criado em:
```
dist/PresetCatalog.exe
```

## Distribuição

Para distribuir para outros usuários:
1. Compartilhe toda a pasta `dist`
2. O executável `PresetCatalog.exe` funcionará sem instalações adicionais
3. Inclua o arquivo `LEIA-ME.txt` para instruções

## Arquivos de Configuração

- `preset_catalog.spec`: Configuração principal do PyInstaller
- `preset_catalog_v2.spec`: Configuração alternativa (backup)

## Observações

- O executável tem aproximadamente 45MB
- Inclui todas as dependências necessárias
- Funciona em Windows 10+ sem instalações extras
- O ícone `PresetCatalog.ico` é incorporado automaticamente
