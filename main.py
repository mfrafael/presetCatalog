import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                              QFileDialog, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QCheckBox, QGridLayout, QFrame,
                              QProgressDialog, QTreeWidget, QTreeWidgetItem,
                              QSplitter, QTabWidget, QAbstractItemView)
from PySide6.QtCore import Qt, QSettings, QCoreApplication
from PySide6.QtGui import QIcon
from xmp_manager import XMPManager
from styles import STYLE_SHEET

class PresetCatalogApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Preset Catalog, by Rafael Andrade")
        self.resize(800, 600)
        
        # Definir o ícone da aplicação
        icon_path = os.path.join(os.path.dirname(__file__), "PresetCatalog.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Configuração para salvar preferências
        self.settings = QSettings("RafaelAndrade", "PresetCatalog")
        
        self.xmp_manager = XMPManager()
        
        # Tentar obter a última pasta usada ou usar a pasta padrão do Camera Raw
        self.current_folder = self.settings.value("last_folder", "")
        if not self.current_folder or not os.path.exists(self.current_folder):
            default_preset_folder = self.get_default_preset_folder()
            if os.path.exists(default_preset_folder):
                self.current_folder = default_preset_folder
                
        # Estado para Smart Path Detection
        self.suggested_clusters = {}  # Mapeamento de arquivo para cluster sugerido
        self.suggested_groups = {}  # Mapeamento de arquivo para grupo sugerido
        self.smart_detection_active = False
        
        self.initUI()
        
        # Carrega a última pasta usada, se existir
        self.load_last_folder()
        
    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Process events more frequently to avoid UI freezes
        QApplication.instance().processEvents()
        
        main_layout = QVBoxLayout(main_widget)
        
        # Header with copyright
        header_layout = QHBoxLayout()
        copyright_label = QLabel("<b>© <a href='http://www.rafaelandrade.art.br'>www.rafaelandrade.art.br</a></b>")
        copyright_label.setStyleSheet("color: gray; font-size: 12px;")
        copyright_label.setOpenExternalLinks(True)  # Enable clickable links
        
        backup_button = QPushButton("Create Backup")
        backup_button.setToolTip("Create a ZIP backup of your preset files")
        backup_button.clicked.connect(self.create_backup)
        
        about_button = QPushButton("About")
        about_button.clicked.connect(self.show_about)
        
        header_layout.addWidget(copyright_label)
        header_layout.addStretch()
        header_layout.addWidget(backup_button)
        header_layout.addWidget(about_button)
        main_layout.addLayout(header_layout)
        
        # Top area - Folder selection
        folder_layout = QVBoxLayout()
        
        folder_header = QLabel("Selected Folder")
        folder_header.setStyleSheet("font-weight: bold;")
        folder_layout.addWidget(folder_header)
        
        folder_selection = QHBoxLayout()
        self.folder_label = QLineEdit()
        self.folder_label.setReadOnly(True)
        self.folder_label.setMinimumHeight(28)  # Aumenta um pouco a altura do campo
        self.folder_label.setStyleSheet("padding-left: 5px;")  # Adiciona um pouco de padding para o texto não ficar grudado na borda
        browse_button = QPushButton("Browse to Folder...")
        browse_button.clicked.connect(self.browse_folder)
        
        folder_selection.addWidget(self.folder_label, 1)  # Dá mais espaço ao campo de texto (proporção 1)
        folder_selection.addWidget(browse_button, 0)  # O botão mantém seu tamanho natural (proporção 0)
        folder_layout.addLayout(folder_selection)
        
        # Description
        description = QLabel("This will edit all XMP files in this folder and its subdirectories. Tick/untick items to be updated below.")
        folder_layout.addWidget(description)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        select_all_button = QPushButton("Select All")
        select_none_button = QPushButton("Select None")
        auto_discover_button = QPushButton("Smart Detection")
        auto_discover_button.setToolTip("Detect cluster and group values from file paths")
        
        select_all_button.clicked.connect(self.select_all_items)
        select_none_button.clicked.connect(self.deselect_all_items)
        auto_discover_button.clicked.connect(self.smart_path_detection)
        
        selection_layout.addWidget(select_all_button)
        selection_layout.addWidget(select_none_button)
        selection_layout.addStretch()
        selection_layout.addWidget(auto_discover_button)
        folder_layout.addLayout(selection_layout)
        
        main_layout.addLayout(folder_layout)
        
        # Tree view for folder structure
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        # Add explanatory label
        tree_label = QLabel("Select folders or files to batch update.")
        tree_label.setStyleSheet("color: gray;")
        tree_layout.addWidget(tree_label)
        
        # Create folder tree with checkboxes
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["Folders & Files", "Cluster", "Group"])
        self.folder_tree.setColumnWidth(0, 400)  # Wider first column
        self.folder_tree.setColumnWidth(1, 150)
        self.folder_tree.setColumnWidth(2, 150)
        self.folder_tree.setAlternatingRowColors(False)
        
        tree_layout.addWidget(self.folder_tree)
        
        main_layout.addWidget(tree_widget)
        
        # Esconder a tabela, mas mantê-la para compatibilidade com o código existente
        self.file_table = QTableWidget(0, 4)
        self.file_table.setVisible(False)
        
        # Bottom controls
        bottom_layout = QVBoxLayout()
        
        # Cluster update
        cluster_layout = QVBoxLayout()
        cluster_label = QLabel("Enter New Cluster Name:")
        self.cluster_input = QLineEdit()
        update_cluster_button = QPushButton("Update Clusters")
        update_cluster_button.clicked.connect(self.update_clusters)

        cluster_note = QLabel("<center>This will update the <i>selected</i> cluster for all selected XMP files.</center>")
        cluster_note.setStyleSheet("color: gray;")
        
        cluster_layout.addWidget(cluster_label)
        cluster_layout.addWidget(self.cluster_input)
        cluster_layout.addWidget(update_cluster_button)
        cluster_layout.addWidget(cluster_note)
        
        # Group update
        group_layout = QVBoxLayout()
        group_label = QLabel("Enter New Group Name:")
        self.group_input = QLineEdit()
        update_group_button = QPushButton("Update Groups")
        update_group_button.clicked.connect(self.update_groups)

        group_note = QLabel("<center>This will update the <i>selected</i> group for all selected XMP files.</center>")
        group_note.setStyleSheet("color: gray;")
        
        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_input)
        group_layout.addWidget(update_group_button)
        group_layout.addWidget(group_note)
        
        # Add everything to bottom layout
        bottom_grid = QGridLayout()
        bottom_grid.addLayout(cluster_layout, 0, 0)
        bottom_grid.addLayout(group_layout, 0, 1)
        
        bottom_layout.addLayout(bottom_grid)
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        self.statusBar().showMessage("Preset Catalog ready - www.rafaelandrade.art.br")
    
    def load_last_folder(self):
        """Carrega a última pasta usada, se existir e for válida"""
        if self.current_folder and os.path.exists(self.current_folder):
            self.folder_label.setText(self.current_folder)
            try:
                self.load_xmp_files(self.current_folder)
                self.statusBar().showMessage(f"Loaded last used folder: {self.current_folder}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading last folder: {str(e)}")
                print(f"Error loading last folder: {str(e)}")
    
    def browse_folder(self):
        # Iniciar o diálogo na última pasta usada ou na pasta padrão do Camera Raw
        if self.current_folder and os.path.exists(self.current_folder):
            initial_dir = self.current_folder
        else:
            initial_dir = self.get_default_preset_folder()
            if not os.path.exists(initial_dir):
                initial_dir = ""
                
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", initial_dir)
        
        if folder:
            self.current_folder = folder
            # Salvar a pasta nas configurações
            self.settings.setValue("last_folder", folder)
            self.folder_label.setText(folder)  # Mostra o caminho completo no campo principal
            try:
                self.load_xmp_files(folder)
                self.statusBar().showMessage(f"Loaded folder: {folder}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading files: {str(e)}")
                print(f"Error loading files: {str(e)}")
    
    def load_xmp_files(self, folder):
        # Resetar qualquer estado de detecção inteligente
        self.suggested_clusters.clear()
        self.suggested_groups.clear()
        self.smart_detection_active = False
        self.cluster_input.setEnabled(True)
        self.group_input.setEnabled(True)
        
        # Always use recursive scanning (as requested)
        recursive = True
        
        # Update status bar with loading message
        self.statusBar().showMessage(f"Loading files from {folder} (including subdirectories)...")
        QApplication.processEvents()  # Make sure UI updates
        
        # Scan for XMP files
        files = self.xmp_manager.scan_xmp_files(folder, recursive=True)
        self.file_table.setRowCount(0)  # Clear table first
        self.file_table.setRowCount(len(files))
        
        print(f"Loading {len(files)} XMP files from {folder}")
        
        self.file_table.setSortingEnabled(False)  # Disable sorting while loading
        
        for i, file_info in enumerate(files):
            try:
                # Checkbox for selection
                checkbox = QCheckBox()
                checkbox_cell = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_cell)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.file_table.setCellWidget(i, 0, checkbox_cell)
                
                # Cluster
                cluster = file_info.get('cluster', '')
                self.file_table.setItem(i, 1, QTableWidgetItem(cluster))
                
                # Group
                group = file_info.get('group', '')
                self.file_table.setItem(i, 2, QTableWidgetItem(group))
                
                # File name with relative path if in subdirectory
                display_name = file_info.get('display_name', file_info['filename'])
                self.file_table.setItem(i, 3, QTableWidgetItem(display_name))
                
                # Update UI every 50 items to keep responsive
                if i % 50 == 0:
                    QApplication.processEvents()
            except Exception as e:
                print(f"Error loading file at index {i}: {str(e)}")
        
        self.file_table.setSortingEnabled(True)  # Re-enable sorting
        
        # Construir a visualização em árvore
        self.build_folder_tree(folder, files)
        
        self.statusBar().showMessage(f"Loaded {len(files)} XMP files", 3000)
    
    def select_all_items(self):
        """Seleciona todos os itens na árvore"""
        # Desconecta temporariamente o sinal para evitar múltiplas atualizações
        self.folder_tree.itemChanged.disconnect(self.on_tree_item_changed)
        
        # Marca recursivamente todos os itens
        self._set_check_state_recursive(self.folder_tree.invisibleRootItem(), Qt.Checked)
        
        # Reconecta o sinal
        self.folder_tree.itemChanged.connect(self.on_tree_item_changed)
        
        self.statusBar().showMessage("Selected all items", 3000)
    
    def deselect_all_items(self):
        """Desmarca todos os itens na árvore"""
        # Desconecta temporariamente o sinal para evitar múltiplas atualizações
        self.folder_tree.itemChanged.disconnect(self.on_tree_item_changed)
        
        # Desmarca recursivamente todos os itens
        self._set_check_state_recursive(self.folder_tree.invisibleRootItem(), Qt.Unchecked)
        
        # Reconecta o sinal
        self.folder_tree.itemChanged.connect(self.on_tree_item_changed)
        
        self.statusBar().showMessage("Deselected all items", 3000)
    
    def get_selected_files(self):
        """Retorna arquivos selecionados a partir dos checkboxes na árvore"""
        # Agora usamos diretamente os checkboxes da árvore
        return self.get_checked_files()
    
    def update_clusters(self):
        new_cluster = self.cluster_input.text().strip()
        if not new_cluster:
            self.statusBar().showMessage("Please enter a cluster name", 3000)
            return
        
        selected_files = self.get_selected_files()
        if not selected_files:
            self.statusBar().showMessage("No files selected", 3000)
            return
        
        # Show progress in status bar
        self.statusBar().showMessage(f"Updating {len(selected_files)} files with cluster '{new_cluster}'...")
        QApplication.processEvents()
        
        count = self.xmp_manager.update_cluster(selected_files, new_cluster)
        self.statusBar().showMessage(f"Updated {count} files with cluster '{new_cluster}'", 5000)
        self.load_xmp_files(self.current_folder)  # Refresh
    
    def update_groups(self):
        new_group = self.group_input.text().strip()
        if not new_group:
            self.statusBar().showMessage("Please enter a group name", 3000)
            return
        
        selected_files = self.get_selected_files()
        if not selected_files:
            self.statusBar().showMessage("No files selected", 3000)
            return
        
        # Show progress in status bar
        self.statusBar().showMessage(f"Updating {len(selected_files)} files with group '{new_group}'...")
        QApplication.processEvents()
        
        count = self.xmp_manager.update_group(selected_files, new_group)
        self.statusBar().showMessage(f"Updated {count} files with group '{new_group}'", 5000)
        self.load_xmp_files(self.current_folder)  # Refresh
        
    def show_about(self):
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About Preset Catalog")
        msg.setText("Preset Catalog, by Rafael Andrade")
        # Use HTML formatting for better control over line breaks
        msg.setInformativeText("""<p>A tool to organize Adobe Lightroom/Camera Raw XMP presets.</p>
                              <p>This application allows you to easily manage your presets by updating 
                              cluster and group information in XMP files.</p>
                              <p>Folder structure is important for organization:<br>
                              - First-level folders are used as Clusters<br>
                              - Second-level folders are used as Groups</p>
                              <p>&nbsp;</p>
                              <p><b>Created by Rafael Andrade - <a href='http://www.rafaelandrade.art.br'>www.rafaelandrade.art.br</a><b></p>""")
        msg.setTextFormat(Qt.RichText)  # Enable HTML formatting
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    def create_backup(self):
        """Creates a ZIP backup of all XMP files in the current folder while preserving folder structure"""
        import zipfile
        import datetime
        import os
        from PySide6.QtWidgets import QFileDialog, QProgressDialog, QMessageBox
        
        # Check if we have a current folder selected
        if not self.current_folder or not os.path.exists(self.current_folder):
            QMessageBox.warning(self, "Backup Error", "Please select a folder with presets first.")
            return
        
        # Get the list of files to back up (all XMP files in the current folder)
        if not hasattr(self.xmp_manager, 'xmp_files') or not self.xmp_manager.xmp_files:
            QMessageBox.warning(self, "Backup Error", "No XMP files found to back up.")
            return
            
        # Generate default backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"PresetCatalog_Backup_{timestamp}.zip"
        
        # Ask user where to save the backup
        backup_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Backup As", 
            os.path.join(os.path.expanduser("~"), "Documents", default_filename),
            "ZIP Archives (*.zip)"
        )
        
        if not backup_path:
            return  # User cancelled
            
        # Add .zip extension if not provided
        if not backup_path.lower().endswith('.zip'):
            backup_path += '.zip'
        
        try:
            # Create progress dialog
            total_files = len(self.xmp_manager.xmp_files)
            progress = QProgressDialog("Creating backup archive...", "Cancel", 0, total_files, self)
            progress.setWindowTitle("Creating Backup")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Create ZIP file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                base_folder = os.path.basename(self.current_folder)
                
                # Add all XMP files to the ZIP
                for i, file_info in enumerate(self.xmp_manager.xmp_files):
                    if progress.wasCanceled():
                        # Delete partial ZIP file
                        zipf.close()
                        os.remove(backup_path)
                        self.statusBar().showMessage("Backup operation canceled", 3000)
                        return
                        
                    file_path = file_info['path']
                    filename = os.path.basename(file_path)
                    
                    # Update progress
                    progress.setValue(i)
                    progress.setLabelText(f"Adding {i+1} of {total_files}: {filename}")
                    QApplication.processEvents()
                    
                    # Calculate relative path for maintaining folder structure
                    rel_path = os.path.relpath(file_path, os.path.dirname(self.current_folder))
                    
                    # Add file to ZIP
                    zipf.write(file_path, rel_path)
            
            # Complete
            progress.setValue(total_files)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Backup Complete", 
                f"Successfully backed up {total_files} XMP files to:\n{backup_path}"
            )
            
            self.statusBar().showMessage(f"Backup created successfully: {backup_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Error creating backup: {str(e)}")
            self.statusBar().showMessage(f"Backup failed: {str(e)}", 5000)
            print(f"Error creating backup: {str(e)}")
    
    def smart_path_detection(self):
        """Executa a detecção inteligente de cluster e grupo baseada no caminho do arquivo"""
        if not self.current_folder:
            self.statusBar().showMessage("Please select a folder first", 3000)
            return
            
        # Verificar se temos arquivos para analisar
        if not self.xmp_manager.xmp_files:
            self.statusBar().showMessage("No XMP files found to analyze", 3000)
            return
            
        total_files = len(self.xmp_manager.xmp_files)
            
        # Criar barra de progresso
        progress = QProgressDialog("Analyzing file paths for smart detection...", "Abort", 0, total_files, self)
        progress.setWindowTitle("Smart Detection")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # Mostrar imediatamente
        progress.setValue(0)
        
        # Executar a auto-descoberta
        self.statusBar().showMessage("Analyzing file paths for smart detection...")
        QApplication.processEvents()  # Atualizar UI
        
        try:
            # Preparar para descoberta manual com progresso
            discoveries = []
            self.suggested_clusters.clear()
            self.suggested_groups.clear()
            self.smart_detection_active = True
            
            # Processar cada arquivo com atualização de progresso
            for i, file_info in enumerate(self.xmp_manager.xmp_files):
                if progress.wasCanceled():
                    self.statusBar().showMessage("Smart detection canceled", 3000)
                    return
                    
                file_path = file_info['path']
                
                # Atualizar barra de progresso
                progress.setValue(i)
                filename = os.path.basename(file_path)
                progress.setLabelText(f"Processing {i+1} of {total_files}: {filename}")
                QCoreApplication.processEvents()
                
                # Detectar cluster e grupo para este arquivo
                auto_cluster, auto_group = self.xmp_manager.detect_cluster_group_from_path(file_path, self.current_folder)
                
                # Preparar item de descoberta
                item = {
                    'file_info': file_info,
                    'path': file_path,
                    'current_cluster': file_info['cluster'],
                    'current_group': file_info['group'],
                    'suggested_cluster': auto_cluster,
                    'suggested_group': auto_group,
                    'needs_cluster_update': auto_cluster != file_info['cluster'] and auto_cluster != '',
                    'needs_group_update': auto_group != file_info['group'] and auto_group != ''
                }
                
                discoveries.append(item)
            
            # Marcar como completo
            progress.setValue(total_files)
            
            # Processar resultados
            files_with_suggestions = 0
            cluster_changes = 0
            group_changes = 0
            
            for item in discoveries:
                file_path = item['path']
                
                if item['needs_cluster_update']:
                    self.suggested_clusters[file_path] = item['suggested_cluster']
                    cluster_changes += 1
                    
                if item['needs_group_update']:
                    self.suggested_groups[file_path] = item['suggested_group']
                    group_changes += 1
                    
                if item['needs_cluster_update'] or item['needs_group_update']:
                    files_with_suggestions += 1
            
            # Criar nova barra de progresso para atualização da tabela
            progress = QProgressDialog("Updating table with suggestions...", "Abort", 0, self.file_table.rowCount(), self)
            progress.setWindowTitle("Smart Detection - Updating UI")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Atualizar a tabela para mostrar sugestões
            self.file_table.setSortingEnabled(False)  # Desabilitar ordenação durante a atualização
            
            # Atualizar os valores de display na tabela
            for row in range(self.file_table.rowCount()):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(row)
                QCoreApplication.processEvents()
                
                # Obter o caminho do arquivo para esta linha
                file_path = None
                item = self.file_table.item(row, 3)  # coluna do nome do arquivo
                if item:
                    display_name = item.text()
                    # Encontrar o caminho completo do arquivo
                    for file_info in self.xmp_manager.xmp_files:
                        if file_info.get('display_name') == display_name:
                            file_path = file_info['path']
                            break
                
                if file_path:
                    # Verificar se há sugestões para este arquivo
                    cluster_cell = self.file_table.item(row, 1)
                    if file_path in self.suggested_clusters and cluster_cell:
                        current = cluster_cell.text()
                        suggested = self.suggested_clusters[file_path]
                        cluster_cell.setText(f"{current} → {suggested}")
                        # Destacar visualmente as células com sugestões
                        cluster_cell.setBackground(Qt.yellow)
                    
                    group_cell = self.file_table.item(row, 2)
                    if file_path in self.suggested_groups and group_cell:
                        current = group_cell.text()
                        suggested = self.suggested_groups[file_path]
                        group_cell.setText(f"{current} → {suggested}")
                        # Destacar visualmente as células com sugestões
                        group_cell.setBackground(Qt.yellow)
            
            # Marcar como completo
            progress.setValue(self.file_table.rowCount())
            
            self.file_table.setSortingEnabled(True)  # Reabilitar ordenação
            
            # Atualizar a visualização em árvore
            self.build_folder_tree(self.current_folder, self.xmp_manager.xmp_files)
            
            # Atualizar os campos de entrada para indicar múltiplos valores
            if cluster_changes > 0:
                self.cluster_input.setText("<multiple values>")
                self.cluster_input.setEnabled(False)  # Desabilitar edição manual quando há sugestões
            
            if group_changes > 0:
                self.group_input.setText("<multiple values>")
                self.group_input.setEnabled(False)  # Desabilitar edição manual quando há sugestões
                
            # Mostrar resultado na status bar
            self.statusBar().showMessage(
                f"Smart Detection found suggestions for {files_with_suggestions} files "
                f"({cluster_changes} cluster changes, {group_changes} group changes)", 
                5000
            )
            
        except Exception as e:
            self.statusBar().showMessage(f"Error during Smart Detection: {str(e)}", 5000)
            print(f"Error during Smart Detection: {str(e)}")
    
    def reset_smart_detection(self):
        """Limpa o estado de detecção inteligente"""
        if self.smart_detection_active:
            self.suggested_clusters.clear()
            self.suggested_groups.clear()
            self.smart_detection_active = False
            self.cluster_input.setEnabled(True)
            self.group_input.setEnabled(True)
            self.cluster_input.clear()
            self.group_input.clear()
            
            # Recarregar a tabela para remover as sugestões visuais
            if self.current_folder:
                self.load_xmp_files(self.current_folder)
    
    def update_clusters(self):
        new_cluster = self.cluster_input.text().strip()
        
        # Verificar se temos detecção inteligente ativa
        if self.smart_detection_active and new_cluster == "<multiple values>":
            # Usar os valores sugeridos
            selected_files = self.get_selected_files()
            if not selected_files:
                self.statusBar().showMessage("No files selected", 3000)
                return
                
            # Filtrar apenas os arquivos que têm sugestões de cluster
            files_to_update = []
            clusters_to_apply = []
            
            for file_path in selected_files:
                if file_path in self.suggested_clusters:
                    files_to_update.append(file_path)
                    clusters_to_apply.append(self.suggested_clusters[file_path])
            
            if not files_to_update:
                self.statusBar().showMessage("No smart path suggestions for selected files", 3000)
                return
            
            # Criar barra de progresso
            progress = QProgressDialog("Updating files with Smart Detection clusters...", "Abort", 0, len(files_to_update), self)
            progress.setWindowTitle("Updating Clusters")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)  # Mostrar imediatamente
            progress.setValue(0)
                
            # Atualizar cada arquivo com seu cluster sugerido
            total_updated = 0
            for i, file_path in enumerate(files_to_update):
                if progress.wasCanceled():
                    self.statusBar().showMessage("Update operation canceled", 3000)
                    break
                    
                # Atualizar barra de progresso
                progress.setValue(i)
                filename = os.path.basename(file_path)
                progress.setLabelText(f"Updating {i+1} of {len(files_to_update)}: {filename}")
                QCoreApplication.processEvents()
                
                cluster_to_apply = clusters_to_apply[i]
                count = self.xmp_manager.update_cluster([file_path], cluster_to_apply)
                # Fix XML tags automatically (new functionality)
                self.xmp_manager.fix_malformed_group_tags([file_path])
                total_updated += count
            
            # Atualizar a barra de progresso para indicar que está carregando os arquivos
            progress.setLabelText("Reloading files after update, please wait...")
            progress.setValue(len(files_to_update))
            QCoreApplication.processEvents()
            
            # Atualizar a barra de status
            self.statusBar().showMessage(f"Reloading files after updating {total_updated} files with Smart Detection clusters...")
            
            # Recarregar arquivos e limpar estado de detecção
            self.reset_smart_detection()
            self.load_xmp_files(self.current_folder)
            
            # Fechar a barra de progresso somente depois que tudo estiver carregado
            progress.close()
            
            # Atualizar a barra de status final
            self.statusBar().showMessage(f"Updated {total_updated} files with Smart Detection clusters", 5000)
            return
        
        # Comportamento normal quando não estamos usando detecção inteligente
        if not new_cluster:
            self.statusBar().showMessage("Please enter a cluster name", 3000)
            return
        
        selected_files = self.get_selected_files()
        if not selected_files:
            self.statusBar().showMessage("No files selected", 3000)
            return
        
        # Criar barra de progresso
        progress = QProgressDialog(f"Updating files with cluster '{new_cluster}'...", "Abort", 0, len(selected_files), self)
        progress.setWindowTitle("Updating Clusters")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # Mostrar imediatamente
        progress.setValue(0)
        
        # Show progress in status bar
        self.statusBar().showMessage(f"Updating {len(selected_files)} files with cluster '{new_cluster}'...")
        
        # Fazer a atualização em lote, mas monitorando o progresso
        count = 0
        batch_size = min(20, len(selected_files))  # Processar em lotes menores para atualizar o progresso
        for i in range(0, len(selected_files), batch_size):
            if progress.wasCanceled():
                self.statusBar().showMessage("Update operation canceled", 3000)
                break
                
            # Atualizar a barra de progresso
            progress.setValue(i)
            if i + batch_size < len(selected_files):
                progress.setLabelText(f"Processing files {i+1}-{i+batch_size} of {len(selected_files)}")
            else:
                progress.setLabelText(f"Processing files {i+1}-{len(selected_files)} of {len(selected_files)}")
            QCoreApplication.processEvents()
            
            # Processar este lote
            batch_files = selected_files[i:i+batch_size]
            count += self.xmp_manager.update_cluster(batch_files, new_cluster)
            
            # Fix XML tags automatically after each batch (new functionality)
            progress.setLabelText(f"Fixing XML tags in batch {i+1}-{min(i+batch_size, len(selected_files))}...")
            QCoreApplication.processEvents()
            self.xmp_manager.fix_malformed_group_tags(batch_files)
        
        # Atualizar a barra de progresso para indicar que está carregando os arquivos
        progress.setLabelText("Reloading files after update, please wait...")
        progress.setValue(len(selected_files))
        QCoreApplication.processEvents()
        
        # Recarregar os arquivos (operação mais demorada)
        self.statusBar().showMessage(f"Reloading files after updating {count} files with cluster '{new_cluster}'...")
        self.load_xmp_files(self.current_folder)  # Refresh
        
        # Fechar a barra de progresso somente depois que tudo estiver carregado
        progress.close()
        
        # Atualizar a barra de status
        self.statusBar().showMessage(f"Updated {count} files with cluster '{new_cluster}'", 5000)
    
    def update_groups(self):
        new_group = self.group_input.text().strip()
        
        # Verificar se temos detecção inteligente ativa
        if self.smart_detection_active and new_group == "<multiple values>":
            # Usar os valores sugeridos
            selected_files = self.get_selected_files()
            if not selected_files:
                self.statusBar().showMessage("No files selected", 3000)
                return
                
            # Filtrar apenas os arquivos que têm sugestões de grupo
            files_to_update = []
            groups_to_apply = []
            
            for file_path in selected_files:
                if file_path in self.suggested_groups:
                    files_to_update.append(file_path)
                    groups_to_apply.append(self.suggested_groups[file_path])
            
            if not files_to_update:
                self.statusBar().showMessage("No smart path suggestions for selected files", 3000)
                return
            
            # Criar barra de progresso
            progress = QProgressDialog("Updating files with Smart Detection groups...", "Abort", 0, len(files_to_update), self)
            progress.setWindowTitle("Updating Groups")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)  # Mostrar imediatamente
            progress.setValue(0)
                
            # Atualizar cada arquivo com seu grupo sugerido
            total_updated = 0
            for i, file_path in enumerate(files_to_update):
                if progress.wasCanceled():
                    self.statusBar().showMessage("Update operation canceled", 3000)
                    break
                
                # Atualizar barra de progresso
                progress.setValue(i)
                filename = os.path.basename(file_path)
                progress.setLabelText(f"Updating {i+1} of {len(files_to_update)}: {filename}")
                QCoreApplication.processEvents()
                
                group_to_apply = groups_to_apply[i]
                count = self.xmp_manager.update_group([file_path], group_to_apply)
                # Fix XML tags automatically (new functionality)
                self.xmp_manager.fix_malformed_group_tags([file_path])
                total_updated += count
            
            # Atualizar a barra de progresso para indicar que está carregando os arquivos
            progress.setLabelText("Reloading files after update, please wait...")
            progress.setValue(len(files_to_update))
            QCoreApplication.processEvents()
            
            # Atualizar a barra de status
            self.statusBar().showMessage(f"Reloading files after updating {total_updated} files with Smart Detection groups...")
            
            # Recarregar arquivos e limpar estado de detecção
            self.reset_smart_detection()
            self.load_xmp_files(self.current_folder)
            
            # Fechar a barra de progresso somente depois que tudo estiver carregado
            progress.close()
            
            # Atualizar a barra de status final
            self.statusBar().showMessage(f"Updated {total_updated} files with Smart Detection groups", 5000)
            return
        
        # Comportamento normal quando não estamos usando detecção inteligente
        if not new_group:
            self.statusBar().showMessage("Please enter a group name", 3000)
            return
        
        selected_files = self.get_selected_files()
        if not selected_files:
            self.statusBar().showMessage("No files selected", 3000)
            return
        
        # Criar barra de progresso
        progress = QProgressDialog(f"Updating files with group '{new_group}'...", "Abort", 0, len(selected_files), self)
        progress.setWindowTitle("Updating Groups")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # Mostrar imediatamente
        progress.setValue(0)
        
        # Show progress in status bar
        self.statusBar().showMessage(f"Updating {len(selected_files)} files with group '{new_group}'...")
        
        # Fazer a atualização em lote, mas monitorando o progresso
        count = 0
        batch_size = min(20, len(selected_files))  # Processar em lotes menores para atualizar o progresso
        for i in range(0, len(selected_files), batch_size):
            if progress.wasCanceled():
                self.statusBar().showMessage("Update operation canceled", 3000)
                break
                
            # Atualizar a barra de progresso
            progress.setValue(i)
            if i + batch_size < len(selected_files):
                progress.setLabelText(f"Processing files {i+1}-{i+batch_size} of {len(selected_files)}")
            else:
                progress.setLabelText(f"Processing files {i+1}-{len(selected_files)} of {len(selected_files)}")
            QCoreApplication.processEvents()
            
            # Processar este lote
            batch_files = selected_files[i:i+batch_size]
            count += self.xmp_manager.update_group(batch_files, new_group)
            
            # Fix XML tags automatically after each batch (new functionality)
            progress.setLabelText(f"Fixing XML tags in batch {i+1}-{min(i+batch_size, len(selected_files))}...")
            QCoreApplication.processEvents()
            self.xmp_manager.fix_malformed_group_tags(batch_files)
            
        # Atualizar a barra de progresso para indicar que está carregando os arquivos
        progress.setLabelText("Reloading files after update, please wait...")
        progress.setValue(len(selected_files))
        QCoreApplication.processEvents()
        
        # Recarregar os arquivos (operação mais demorada)
        self.statusBar().showMessage(f"Reloading files after updating {count} files with group '{new_group}'...")
        self.load_xmp_files(self.current_folder)  # Refresh
        
        # Fechar a barra de progresso somente depois que tudo estiver carregado
        progress.close()
        
        # Atualizar a barra de status
        self.statusBar().showMessage(f"Updated {count} files with group '{new_group}'", 5000)
    

    def on_tree_selection_changed(self):
        """Atualiza a seleção dos checkboxes na tabela com base na seleção da árvore"""
        selected_items = self.folder_tree.selectedItems()
        if not selected_items:
            return
            
        # Desmarcar todos os itens primeiro
        self.deselect_all_items()
        
        # Conjunto de arquivos a serem selecionados
        files_to_select = set()
        
        # Processa os itens selecionados
        for item in selected_items:
            # Se é um arquivo, adiciona diretamente
            if hasattr(item, 'file_path'):
                files_to_select.add(item.file_path)
            # Se é uma pasta, adiciona todos os arquivos sob ela
            else:
                self._collect_files_from_tree_item(item, files_to_select)
        
        # Agora marca os checkboxes dos arquivos encontrados
        self._select_files_in_table(files_to_select)
        
        # Atualiza a contagem na barra de status
        self.statusBar().showMessage(f"Selected {len(files_to_select)} files", 3000)
    
    def _collect_files_from_tree_item(self, item, files_set):
        """Coleta recursivamente todos os caminhos de arquivos de um item da árvore e seus filhos"""
        # Verifica se este item é um arquivo
        if hasattr(item, 'file_path'):
            files_set.add(item.file_path)
        
        # Recursivamente processa todos os filhos
        for i in range(item.childCount()):
            child = item.child(i)
            self._collect_files_from_tree_item(child, files_set)
    
    def _select_files_in_table(self, file_paths):
        """Seleciona arquivos na tabela baseado em seus caminhos"""
        # Mapeia caminhos de arquivo para índices na tabela
        file_path_to_row = {}
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 3)  # Coluna do nome do arquivo
            if item:
                display_name = item.text()
                # Encontra o caminho completo
                for file_info in self.xmp_manager.xmp_files:
                    if file_info.get('display_name') == display_name:
                        file_path_to_row[file_info['path']] = row
                        break
        
        # Agora seleciona os checkboxes para os arquivos identificados
        for file_path in file_paths:
            if file_path in file_path_to_row:
                row = file_path_to_row[file_path]
                checkbox_cell = self.file_table.cellWidget(row, 0)
                if checkbox_cell:
                    checkbox = checkbox_cell.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(True)
    
    def build_folder_tree(self, folder, files):
        """Constrói uma árvore de pastas e arquivos para visualização com checkboxes"""
        self.folder_tree.clear()
        
        if not folder or not files:
            return
            
        # Cria o nó raiz
        root_item = QTreeWidgetItem(self.folder_tree, [os.path.basename(folder), "", ""])
        root_item.setExpanded(True)
        root_item.setFlags(root_item.flags() | Qt.ItemIsUserCheckable)
        root_item.setCheckState(0, Qt.Unchecked)
        
        # Mapeia caminhos de pasta para itens de árvore
        self.folder_items = {folder: root_item}
        self.file_items = {}  # Mapeia caminhos de arquivo para itens de árvore
        
        # Agrupa arquivos por pastas
        folder_files = {}
        
        # Processa todos os arquivos
        for file_info in files:
            file_path = file_info['path']
            parent_dir = os.path.dirname(file_path)
            
            # Adiciona a pasta pai à estrutura, se ainda não existir
            if parent_dir not in self.folder_items:
                # Cria cadeia de pastas pai, se necessário
                self._create_parent_folders(parent_dir, folder, self.folder_items)
            
            # Adiciona arquivo à sua pasta pai
            if parent_dir not in folder_files:
                folder_files[parent_dir] = []
            folder_files[parent_dir].append(file_info)
        
        # Adiciona arquivos às pastas correspondentes
        for folder_path, files_list in folder_files.items():
            folder_item = self.folder_items[folder_path]
            
            for file_info in files_list:
                file_name = file_info['filename']
                file_path = file_info['path']
                cluster = file_info.get('cluster', '')
                group = file_info.get('group', '')
                
                # Verificar se existem sugestões de Smart Detection para este arquivo
                if self.smart_detection_active:
                    if file_path in self.suggested_clusters:
                        cluster = f"{cluster} → {self.suggested_clusters[file_path]}"
                    if file_path in self.suggested_groups:
                        group = f"{group} → {self.suggested_groups[file_path]}"
                
                file_item = QTreeWidgetItem(folder_item, [file_name, cluster, group])
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
                file_item.setCheckState(0, Qt.Unchecked)
                file_item.file_path = file_path  # Armazena o caminho do arquivo
                
                # Guarda referência ao item da árvore
                self.file_items[file_path] = file_item
        
        # Habilita a seleção de itens
        self.folder_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Conecta o sinal de alteração de item
        self.folder_tree.itemChanged.connect(self.on_tree_item_changed)
        
        # Ordena a árvore
        self.folder_tree.sortItems(0, Qt.AscendingOrder)
    
    def _create_parent_folders(self, folder_path, base_folder, folder_items):
        """Cria hierarquia de pastas na árvore"""
        if folder_path == base_folder or folder_path in folder_items:
            return folder_items[folder_path]
        
        # Obtém a pasta pai
        parent_dir = os.path.dirname(folder_path)
        
        # Se a pasta pai ainda não existe, cria recursivamente
        if parent_dir not in folder_items:
            parent_item = self._create_parent_folders(parent_dir, base_folder, folder_items)
        else:
            parent_item = folder_items[parent_dir]
        
        # Cria o item para esta pasta
        folder_name = os.path.basename(folder_path)
        folder_item = QTreeWidgetItem(parent_item, [folder_name, "", ""])
        folder_item.setFlags(folder_item.flags() | Qt.ItemIsUserCheckable)
        folder_item.setCheckState(0, Qt.Unchecked)
        folder_items[folder_path] = folder_item
        
        return folder_item
        
    def on_tree_item_changed(self, item, column):
        """Lida com a alteração de estado de checkbox em itens da árvore"""
        if column == 0 and item.flags() & Qt.ItemIsUserCheckable:
            # Obter o estado atual do checkbox
            check_state = item.checkState(0)
            
            # Desconectar o sinal antes de fazer alterações para evitar recursão
            self.folder_tree.itemChanged.disconnect(self.on_tree_item_changed)
            
            # Lógica diferente para pastas e arquivos
            if not hasattr(item, 'file_path'):
                # Se for uma pasta, propaga o estado para os filhos diretos
                for i in range(item.childCount()):
                    child = item.child(i)
                    child.setCheckState(0, check_state)
            
            # Reconectar o sinal após as alterações
            self.folder_tree.itemChanged.connect(self.on_tree_item_changed)
            
            # Atualiza os pais baseado no estado dos filhos
            self.update_parent_check_state(item.parent())
    

    def _set_check_state_recursive(self, item, check_state):
        """Define o estado de checkbox para um item e todos os seus filhos recursivamente"""
        # Primeiro, marca todos os itens de nível inferior
        for i in range(item.childCount()):
            child = item.child(i)
            if child.flags() & Qt.ItemIsUserCheckable:
                child.setCheckState(0, check_state)
            self._set_check_state_recursive(child, check_state)
    
    def update_parent_check_state(self, parent):
        """Atualiza o estado de checkbox do pai baseado nos filhos"""
        if not parent:
            return
            
        child_count = parent.childCount()
        if child_count == 0:
            return
            
        checked_count = 0
        unchecked_count = 0
        partially_checked_count = 0
        
        for i in range(child_count):
            child = parent.child(i)
            state = child.checkState(0)
            if state == Qt.Checked:
                checked_count += 1
            elif state == Qt.Unchecked:
                unchecked_count += 1
            elif state == Qt.PartiallyChecked:
                partially_checked_count += 1
        
        # Desconecta temporariamente o sinal para evitar recursão
        self.folder_tree.itemChanged.disconnect(self.on_tree_item_changed)
        
        # Define o estado do pai
        if checked_count == child_count:
            parent.setCheckState(0, Qt.Checked)
        elif unchecked_count == child_count:
            parent.setCheckState(0, Qt.Unchecked)
        else:
            parent.setCheckState(0, Qt.PartiallyChecked)
        
        # Reconecta o sinal
        self.folder_tree.itemChanged.connect(self.on_tree_item_changed)
            
        # Propaga para cima na árvore
        self.update_parent_check_state(parent.parent())
    
    def get_checked_files(self):
        """Retorna uma lista de caminhos de arquivo para todos os itens marcados na árvore"""
        checked_files = []
        self._collect_checked_files(self.folder_tree.invisibleRootItem(), checked_files)
        return checked_files
    
    def _collect_checked_files(self, item, file_list):
        """Coleta recursivamente os arquivos marcados"""
        # Para cada item filho
        for i in range(item.childCount()):
            child = item.child(i)
            
            # Se o filho é um arquivo e está marcado
            if hasattr(child, 'file_path') and child.checkState(0) == Qt.Checked:
                file_list.append(child.file_path)
            
            # Se o filho é uma pasta e está completamente marcado (não parcialmente)
            # colete todos os arquivos desta pasta diretamente
            elif not hasattr(child, 'file_path') and child.checkState(0) == Qt.Checked:
                self._collect_all_files_in_folder(child, file_list)
            # Caso contrário, continue a verificação recursiva normal
            elif child.childCount() > 0:
                self._collect_checked_files(child, file_list)
                
        # Certifique-se de que os arquivos que têm caminhos armazenados diretamente são incluídos
        # Isso é importante para compatibilidade com Smart Detection
        if hasattr(item, 'file_path') and item.checkState(0) == Qt.Checked:
            file_list.append(item.file_path)
    
    def _collect_all_files_in_folder(self, folder_item, file_list):
        """Coleta todos os arquivos em uma pasta, independente do estado do checkbox"""
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            
            # Se é um arquivo, adiciona à lista
            if hasattr(child, 'file_path'):
                file_list.append(child.file_path)
            # Se é uma pasta, coleta recursivamente
            else:
                self._collect_all_files_in_folder(child, file_list)
    
    def get_default_preset_folder(self):
        """
        Retorna o diretório padrão dos presets do Adobe Camera Raw baseado no sistema operacional
        e no perfil do usuário atual.
        """
        user_home = os.path.expanduser("~")
        
        # Caminho padrão para Windows
        if os.name == 'nt':  # Windows
            return os.path.join(user_home, "AppData", "Roaming", "Adobe", "CameraRaw", "Settings")
        # Caminho padrão para macOS
        elif os.name == 'posix' and sys.platform == 'darwin':  # macOS
            return os.path.join(user_home, "Library", "Application Support", "Adobe", "CameraRaw", "Settings")
        # Caminho padrão para Linux
        elif os.name == 'posix':  # Linux
            return os.path.join(user_home, ".config", "Adobe", "CameraRaw", "Settings")
        # Caso não seja reconhecido, retorna uma pasta vazia
        return ""
        
    def closeEvent(self, event):
        """Executado quando o aplicativo é fechado"""
        # Salvar configurações antes de fechar
        if self.current_folder:
            self.settings.setValue("last_folder", self.current_folder)
        event.accept()  # Permite que o evento de fechamento continue

def debug_file_access(directory):
    """Debug function to check folder access"""
    if not os.path.exists(directory):
        print(f"Directory doesn't exist: {directory}")
        return False
        
    print(f"Directory exists: {directory}")
    try:
        files = os.listdir(directory)
        print(f"Successfully listed {len(files)} files")
        xmp_files = [f for f in files if f.lower().endswith('.xmp')]
        print(f"Found {len(xmp_files)} XMP files")
        return True
    except Exception as e:
        print(f"Error accessing directory: {str(e)}")
        return False

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = PresetCatalogApp()
    window.show()
    
    # Debug default location
    debug_dir = window.get_default_preset_folder()
    if os.path.exists(debug_dir):
        print(f"Default directory accessible: {debug_dir}")
        debug_file_access(debug_dir)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
