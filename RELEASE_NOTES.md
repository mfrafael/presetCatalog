# Preset Catalog v1.0 - Release Notes

## 📦 Download
Baixe o arquivo `PresetCatalog-v1.0.zip`, extraia e execute `PresetCatalog.exe`

## ✨ Funcionalidades

### Organização de Presets
- **Batch update** de informações de cluster e grupo em arquivos XMP
- **Smart Path Detection** para sugestão automática baseada na estrutura de pastas
- **Interface visual** com árvore de pastas para navegação fácil
- **Escaneamento recursivo** para processar todos os presets em subpastas

### Interface
- Interface gráfica intuitiva com PySide6
- Seleção múltipla de arquivos
- Navegação por árvore de pastas
- Feedback visual do progresso

### Compatibilidade
- **Windows 10+** (testado)
- **Não requer instalação** - executável portátil
- **Adobe Lightroom/Camera Raw** - compatível com presets XMP

## 📋 Como Usar

1. **Extraia o ZIP** em qualquer pasta
2. **Execute** `PresetCatalog.exe`
3. **Clique** em "Browse to Folder" e selecione sua pasta de presets
4. **Navegue** pela árvore de pastas e selecione arquivos
5. **Digite** novos nomes de Cluster/Grupo
6. **Clique** em "Update Clusters" ou "Update Groups"

## 📁 Estrutura Recomendada de Pastas

```
Pasta de Presets/
├── Cluster1/           (Nome do Cluster)
│   ├── Grupo1/         (Nome do Grupo)
│   │   ├── preset1.xmp
│   │   └── preset2.xmp
│   └── Grupo2/
│       └── preset3.xmp
```

## 🔧 Funcionalidades Técnicas

- **Correção automática** de formatação XML
- **Backup de segurança** antes das modificações
- **Detecção inteligente** de caminhos baseada na estrutura de pastas
- **Interface responsiva** com processamento em background

## 📝 Arquivos Incluídos

- `PresetCatalog.exe` - Aplicativo principal
- `LEIA-ME.txt` - Instruções detalhadas em português

## 🐛 Problemas Conhecidos

Nenhum problema conhecido nesta versão.

## 💡 Suporte

Para suporte ou dúvidas:
- **Website**: [www.rafaelandrade.art.br](http://www.rafaelandrade.art.br)
- **GitHub**: [Issues](https://github.com/mfrafael/presetCatalog/issues)

---

**Desenvolvido por Rafael Andrade** © 2025
