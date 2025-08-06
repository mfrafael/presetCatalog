import os
import re

class XMPManager:
    """Class to handle XMP file operations for Adobe Lightroom presets"""
    
    def __init__(self):
        self.xmp_files = []
    
    def scan_xmp_files(self, folder_path, recursive=True):
        """
        Scan for XMP files in the specified folder
        
        Args:
            folder_path: Path to the folder to scan
            recursive: If True, scan subdirectories recursively
        
        Returns:
            List of dictionaries with XMP file information
        """
        result = []
        
        try:
            if recursive:
                # Walk through all subdirectories
                print(f"Starting recursive scan in {folder_path}")
                for root, dirs, files in os.walk(folder_path):
                    rel_path = os.path.relpath(root, folder_path) if root != folder_path else ""
                    if rel_path:
                        print(f"Scanning subdirectory: {rel_path}")
                    
                    xmp_files = [f for f in files if f.lower().endswith('.xmp')]
                    if xmp_files:
                        print(f"Found {len(xmp_files)} XMP files in {root}")
                    
                    for file in xmp_files:
                        file_path = os.path.join(root, file)
                        rel_file_path = os.path.relpath(file_path, folder_path)
                        
                        try:
                            cluster, group = self.extract_metadata(file_path)
                            
                            # For display purposes, include relative path if in subdirectory
                            display_name = rel_file_path if rel_path else file
                            
                            result.append({
                                'filename': file,
                                'display_name': display_name,
                                'path': file_path,
                                'rel_path': rel_file_path,
                                'cluster': cluster,
                                'group': group
                            })
                        except Exception as e:
                            print(f"Error extracting metadata from {file}: {str(e)}")
                            # Still add the file with empty metadata
                            result.append({
                                'filename': file,
                                'display_name': rel_file_path if rel_path else file,
                                'path': file_path,
                                'rel_path': rel_file_path,
                                'cluster': '(error)',
                                'group': '(error)'
                            })
            else:
                # Only scan the specified folder without recursion (original behavior)
                files = os.listdir(folder_path)
                print(f"Found {len(files)} files in directory (non-recursive)")
                
                for file in files:
                    if file.lower().endswith('.xmp'):
                        file_path = os.path.join(folder_path, file)
                        
                        try:
                            cluster, group = self.extract_metadata(file_path)
                            result.append({
                                'filename': file,
                                'display_name': file,
                                'path': file_path,
                                'rel_path': file,
                                'cluster': cluster,
                                'group': group
                            })
                        except Exception as e:
                            print(f"Error extracting metadata from {file}: {str(e)}")
                            # Still add the file with empty metadata
                            result.append({
                                'filename': file,
                                'display_name': file,
                                'path': file_path,
                                'rel_path': file,
                                'cluster': '(error)',
                                'group': '(error)'
                            })
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {str(e)}")
        
        print(f"Processed {len(result)} XMP files in total")
        self.xmp_files = result
        return result
    
    def extract_metadata(self, file_path):
        """Extract cluster and group information from an XMP file"""
        cluster = ""
        group = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
                # Extract cluster
                cluster_match = re.search(r'crs:Cluster\s*=\s*"([^"]*)"', content)
                if cluster_match:
                    cluster = cluster_match.group(1)
                
                # Extract group - try different patterns that might exist in XMP files
                group_patterns = [
                    r'<crs:Group>.*?<rdf:li xml:lang="x-default">(.*?)</rdf:li>',
                    r'<crs:Group><rdf:Alt><rdf:li.*?>(.*?)</rdf:li>',
                    r'crs:Group="([^"]*)"'
                ]
                
                for pattern in group_patterns:
                    group_match = re.search(pattern, content, re.DOTALL)
                    if group_match:
                        group = group_match.group(1)
                        break
        except UnicodeDecodeError:
            print(f"Unicode decode error in {file_path}, trying alternative encoding")
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    cluster_match = re.search(r'crs:Cluster\s*=\s*"([^"]*)"', content)
                    if cluster_match:
                        cluster = cluster_match.group(1)
            except Exception as e:
                print(f"Failed with alternative encoding: {str(e)}")
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
        
        return cluster, group
    
    def update_cluster(self, file_paths, new_cluster):
        """
        Atualiza o valor do cluster nos arquivos XMP especificados.
        Também aplica a correção nas tags de grupo para garantir que o arquivo fique consistente.
        """
        count = 0
        
        for file_path in file_paths:
            try:
                # Primeiro corrige as tags Group para garantir consistência
                self.fix_malformed_group_tags([file_path])
                
                # Lê o conteúdo do arquivo corrigido
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Atualiza o valor do cluster
                # Procura pelo padrão crs:Cluster="valor_anterior"
                cluster_pattern = r'(crs:Cluster\s*=\s*")[^"]*(")'
                updated_content, changes = re.subn(
                    cluster_pattern,
                    fr'\1{new_cluster}\2',
                    content
                )
                
                # Se não encontrou o padrão, pode ser que o arquivo não tenha o atributo Cluster
                # Nesse caso, vamos adicionar o atributo
                if changes == 0:
                    # Procura pela tag rdf:Description para adicionar o atributo
                    desc_pattern = r'(<rdf:Description[^>]*)'
                    updated_content, changes = re.subn(
                        desc_pattern,
                        fr'\1 crs:Cluster="{new_cluster}"',
                        content
                    )
                
                if changes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    count += 1
                    print(f"Cluster atualizado em {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error updating cluster in {file_path}: {str(e)}")
        
        return count
    
    def update_group(self, file_paths, new_group):
        """
        Atualiza o valor do grupo nos arquivos XMP especificados.
        Em vez de tentar reparar tags malformadas, esta implementação remove
        completamente todas as tags crs:Group existentes e insere uma nova tag
        com o formato correto.
        """
        count = 0
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                updated_content = content
                
                # Remover QUALQUER tag crs:Group existente (independente de formatação)
                # Primeiro, tentar encontrar todas as possíveis variações de tags de grupo
                group_patterns = [
                    r'<crs:Group>.*?</crs:Group>',  # Tag completa com qualquer conteúdo
                    r'<crs:Group\s*>.*?</crs:Group\s*>',  # Variação com espaços
                    r'<crs:Group>[^<]*</rdf:li></rdf:Alt></crs:Group>',  # Grupo malformado com texto solto
                    r'[^<]*</rdf:li></rdf:Alt></crs:Group>',  # Apenas fechamento sem abertura
                    r'<crs:Group>.*?<rdf:Alt>.*?<rdf:li[^>]*>.*?</rdf:li>.*?</rdf:Alt>.*?</crs:Group>',  # Grupo bem formado
                ]
                
                # Remover todas as ocorrências de cada padrão
                for pattern in group_patterns:
                    updated_content = re.sub(pattern, '', updated_content, flags=re.DOTALL)
                
                # Limpar linhas em branco ou espaços que possam ter sido deixados
                updated_content = re.sub(r'\n\s*\n', '\n', updated_content)
                
                # Criar uma nova tag Group com o formato correto
                new_group_xml = f'   <crs:Group>\n    <rdf:Alt>\n     <rdf:li xml:lang="x-default">{new_group}</rdf:li>\n    </rdf:Alt>\n   </crs:Group>\n'
                
                # Inserir a nova tag antes de </rdf:Description>
                description_end = updated_content.find('</rdf:Description>')
                if description_end != -1:
                    # Encontrar o último elemento antes do fechamento da Description
                    # para posicionar corretamente a nova tag
                    last_tag_end = updated_content.rfind('>', 0, description_end)
                    if last_tag_end != -1:
                        # Inserir a nova tag após o último elemento e antes do fechamento da Description
                        updated_content = updated_content[:last_tag_end+1] + '\n' + new_group_xml + updated_content[last_tag_end+1:]
                        changes = 1
                    else:
                        # Fallback: inserir antes do fechamento da Description
                        updated_content = updated_content[:description_end] + new_group_xml + updated_content[description_end:]
                        changes = 1
                else:
                    # Se não encontrar </rdf:Description>, não há como inserir o grupo
                    print(f"Não foi possível encontrar tag de fechamento rdf:Description em {file_path}")
                    changes = 0
                
                # Escrever o conteúdo atualizado de volta ao arquivo
                if changes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    count += 1
                    print(f"Grupo atualizado com sucesso em {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Error updating group in {file_path}: {str(e)}")
        
        return count
    
    def detect_cluster_group_from_path(self, file_path, base_path):
        """
        Auto-detecta o cluster e grupo baseado no caminho do arquivo, similar ao script.py.
        
        Args:
            file_path: Caminho completo do arquivo XMP
            base_path: Diretório base para cálculo do caminho relativo
        
        Returns:
            Tupla com (cluster, grupo)
        """
        try:
            rel_path = os.path.relpath(file_path, base_path)
            parts = rel_path.split(os.sep)
            
            # Cluster é a primeira pasta do caminho relativo
            cluster = parts[0] if len(parts) > 1 else ''
            
            # Grupo são as pastas intermediárias entre o cluster e o arquivo
            group_parts = parts[1:-1]  # Do segundo até antes do arquivo
            group = ' - '.join(group_parts)
            
            return cluster, group.strip()
        except Exception as e:
            print(f"Error detecting cluster/group from path: {str(e)}")
            return '', ''
    
    def auto_discover_metadata(self, base_folder):
        """
        Smart Detection - Descobre os metadados (cluster e grupo) para todos os arquivos XMP carregados
        baseado na estrutura de pastas.
        
        Args:
            base_folder: Pasta base para cálculo dos caminhos relativos
            
        Returns:
            Lista com as informações dos arquivos com os novos metadados sugeridos
        """
        discoveries = []
        
        for file_info in self.xmp_files:
            file_path = file_info['path']
            auto_cluster, auto_group = self.detect_cluster_group_from_path(file_path, base_folder)
            
            discoveries.append({
                'file_info': file_info,
                'path': file_path,
                'current_cluster': file_info['cluster'],
                'current_group': file_info['group'],
                'suggested_cluster': auto_cluster,
                'suggested_group': auto_group,
                'needs_cluster_update': auto_cluster != file_info['cluster'] and auto_cluster != '',
                'needs_group_update': auto_group != file_info['group'] and auto_group != ''
            })
        
        return discoveries
    
    def fix_malformed_group_tags(self, file_paths):
        """
        Corrige tags crs:Group malformadas em arquivos XMP.
        
        Abordagem: em vez de tentar detectar e corrigir vários tipos de malformação,
        extrai o valor do grupo (se existir) e depois remove completamente todas as ocorrências
        da tag crs:Group, recriando-a corretamente na posição correta na hierarquia do XML.
        
        Args:
            file_paths: Lista de caminhos dos arquivos a serem corrigidos
            
        Returns:
            Número de arquivos corrigidos
        """
        count = 0
        
        for file_path in file_paths:
            try:
                # Ler o conteúdo do arquivo
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    original_content = f.read()
                
                # Tentar extrair o nome do grupo do arquivo atual
                group_name = None
                
                # Padrões para tentar extrair o nome do grupo existente (qualquer formato)
                extraction_patterns = [
                    # Grupo bem formado
                    r'<crs:Group>.*?<rdf:Alt>.*?<rdf:li xml:lang="x-default">(.*?)</rdf:li>',
                    # Grupo com indentação variada
                    r'<crs:Group>\s*<rdf:Alt>\s*<rdf:li[^>]*>(.*?)</rdf:li>',
                    # Texto solto seguido de fechamentos de tag
                    r'([^<>]+)</rdf:li></rdf:Alt></crs:Group>',
                    # Outro formato possível
                    r'<crs:Group><rdf:Alt><rdf:li xml:lang="x-default">(.*?)</rdf:li></rdf:Alt></crs:Group>'
                ]
                
                # Procurar pelo nome do grupo usando todos os padrões
                for pattern in extraction_patterns:
                    match = re.search(pattern, original_content, re.DOTALL)
                    if match:
                        extracted_name = match.group(1).strip()
                        if extracted_name and len(extracted_name) < 100:  # Limite razoável para nome de grupo
                            group_name = extracted_name
                            print(f"Nome do grupo extraído: '{group_name}' de {os.path.basename(file_path)}")
                            break
                
                # Se não encontramos um nome de grupo, tentar extrair do caminho do arquivo
                if not group_name:
                    try:
                        # Usar o nome da pasta como grupo
                        parent_folder = os.path.basename(os.path.dirname(file_path))
                        if parent_folder and parent_folder != "Settings":
                            group_name = parent_folder
                            print(f"Nome do grupo extraído do caminho: '{group_name}' para {os.path.basename(file_path)}")
                    except:
                        pass
                
                # Se não conseguimos extrair um nome de grupo, não podemos corrigir este arquivo
                if not group_name:
                    print(f"Não foi possível extrair nome do grupo para {os.path.basename(file_path)}")
                    continue
                
                # Abordagem de reconstrução completa:
                # 1. Separar o arquivo em três partes: início da tag Description, conteúdo e fechamento
                # 2. Remover completamente qualquer tag Group existente do conteúdo
                # 3. Inserir a nova tag Group logo após as propriedades principais e antes de outras tags
                
                # Encontrar a tag Description principal
                desc_start_match = re.search(r'<rdf:Description rdf:about=""[^>]*>', original_content)
                desc_end_match = re.search(r'</rdf:Description>', original_content)
                
                if desc_start_match and desc_end_match:
                    desc_start_end = desc_start_match.end()
                    desc_end_start = desc_end_match.start()
                    
                    # Pegar o conteúdo entre o início e o fim da Description
                    description_content = original_content[desc_start_end:desc_end_start]
                    
                    # Remover todas as ocorrências de tags Group existentes
                    removal_patterns = [
                        r'<crs:Group>.*?</crs:Group>',
                        r'<crs:Group\s*>.*?</crs:Group\s*>',
                        r'[^<>]*</rdf:li></rdf:Alt></crs:Group>',
                        r'<crs:Group>.*?<rdf:Alt>.*?<rdf:li[^>]*>.*?</rdf:li>.*?</rdf:Alt>.*?</crs:Group>'
                    ]
                    
                    cleaned_content = description_content
                    for pattern in removal_patterns:
                        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL)
                    
                    # Encontrar um ponto apropriado para inserir a tag Group
                    # Normalmente após as propriedades (atributos) e antes das subtags
                    
                    # Primeiro, procurar o final dos atributos (propriedades com "=")
                    # Eles normalmente têm um formato crs:PropertyName="value"
                    prop_pattern = r'crs:[A-Za-z0-9]+=("[^"]*")'
                    all_props = list(re.finditer(prop_pattern, cleaned_content))
                    
                    # Encontrar a posição da primeira subtag (<crs:Name>, etc.)
                    subtag_match = re.search(r'<crs:', cleaned_content)
                    
                    if all_props and subtag_match:
                        # Inserir após a última propriedade e antes da primeira subtag
                        last_prop_end = all_props[-1].end()
                        first_subtag_start = subtag_match.start()
                        
                        if last_prop_end < first_subtag_start:
                            # Tem espaço entre o último atributo e a primeira subtag - ideal
                            insertion_point = last_prop_end
                        else:
                            # Inserir no início da primeira subtag
                            insertion_point = first_subtag_start
                    elif all_props:
                        # Inserir após a última propriedade
                        insertion_point = all_props[-1].end()
                    elif subtag_match:
                        # Inserir antes da primeira subtag
                        insertion_point = subtag_match.start()
                    else:
                        # Não encontrou propriedades ou subtags - inserir no início
                        insertion_point = 0
                    
                    # Criar a nova tag Group bem formatada
                    new_group_xml = f'\n   <crs:Group>\n    <rdf:Alt>\n     <rdf:li xml:lang="x-default">{group_name}</rdf:li>\n    </rdf:Alt>\n   </crs:Group>\n'
                    
                    # Reconstituir o arquivo completo
                    fixed_content = (
                        original_content[:desc_start_end] +  # Início do arquivo até o fim da abertura da tag Description
                        cleaned_content[:insertion_point] +   # Conteúdo da Description até o ponto de inserção
                        new_group_xml +                      # Nova tag Group
                        cleaned_content[insertion_point:] +  # Resto do conteúdo da Description
                        original_content[desc_end_start:]     # Fechamento da Description até o fim do arquivo
                    )
                    
                    # Limpar linhas em branco ou espaços extras que possam ter sido deixados
                    fixed_content = re.sub(r'\n\s*\n', '\n', fixed_content)
                    
                    # Escrever o conteúdo corrigido de volta ao arquivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    count += 1
                    print(f"Fixed group tag in {os.path.basename(file_path)}")
                else:
                    print(f"Não foi possível encontrar as tags rdf:Description em {os.path.basename(file_path)}")
            
            except Exception as e:
                print(f"Error fixing group tag in {file_path}: {str(e)}")
        
        return count

    def batch_process_folder(self, folder_path, cluster_name=None, group_name=None):
        """Process all XMP files in a folder to update cluster and/or group"""
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if f.lower().endswith('.xmp')]
        
        cluster_count = 0
        group_count = 0
        
        if cluster_name:
            cluster_count = self.update_cluster(files, cluster_name)
            
        if group_name:
            group_count = self.update_group(files, group_name)
            
        return {
            'total_files': len(files),
            'cluster_updated': cluster_count,
            'group_updated': group_count
        }
