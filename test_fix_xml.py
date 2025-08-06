import sys
import os
from xmp_manager import XMPManager

# Esse é um script de teste para verificar se a funcionalidade de correção de XML está funcionando
# Pode ser executado diretamente para testar a correção em arquivos específicos

def main():
    # Verificar se foi fornecido um caminho como argumento
    if len(sys.argv) < 2:
        print("Uso: python test_fix_xml.py <caminho_do_arquivo_ou_pasta>")
        return
    
    path = sys.argv[1]
    manager = XMPManager()
    
    if os.path.isdir(path):
        # Se for um diretório, procurar todos os arquivos XMP
        files = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.lower().endswith('.xmp'):
                    files.append(os.path.join(root, filename))
        
        if not files:
            print(f"Nenhum arquivo XMP encontrado em: {path}")
            return
            
        print(f"Encontrados {len(files)} arquivos XMP para verificação")
    else:
        # Se for um arquivo único
        if not path.lower().endswith('.xmp'):
            print(f"O arquivo não parece ser um arquivo XMP: {path}")
            return
            
        if not os.path.exists(path):
            print(f"Arquivo não encontrado: {path}")
            return
            
        files = [path]
        print(f"Verificando arquivo: {path}")
    
    # Processar os arquivos
    count = manager.fix_malformed_group_tags(files)
    print(f"\nTotal de arquivos corrigidos: {count}")
    
if __name__ == "__main__":
    main()
