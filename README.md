# XMP Preset Manager for Adobe Lightroom

## Overview

XMP Preset Manager is a tool designed to help photographers and editors efficiently organize Adobe Lightroom/Camera Raw XMP presets. It provides a simple interface to update cluster and group information in XMP files, making preset management more intuitive and structured in Lightroom.

## Key Features

- **Batch update** of cluster and group information for multiple XMP files
- **Smart Path Detection** to automatically suggest cluster/group values based on folder structure
- **Visual folder tree** for easy navigation and selection of presets
- **Recursive scanning** to process all presets in nested folders
- **Automatic XML fixing** to ensure compatibility with Adobe software

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```
   pip install PySide6
   ```
3. Run the application:
   ```
   python main.py
   ```

## How to Use

### Important: Folder Structure for Organization

The application works best with a specific folder structure to organize your presets:

```
Root Preset Folder/
├── Cluster1/              # First-level folder = Cluster name
│   ├── Group1/            # Second-level folder = Group name
│   │   ├── preset1.xmp
│   │   └── preset2.xmp
│   └── Group2/
│       ├── preset3.xmp
│       └── preset4.xmp
├── Cluster2/
│   └── Group3/
│       └── preset5.xmp
```

- **First-level folders** are used as Cluster names
- **Second-level folders** (and below) are used as Group names
- This structure is used by the Smart Path Detection feature

### Basic Usage

1. Click **Browse to Folder** and select your root preset folder
2. The application will scan for XMP files in the selected folder and its subdirectories
3. Use the folder tree to navigate and select files
4. Select the files you want to modify using the checkboxes
5. Enter new Cluster or Group names in the respective fields
6. Click **Update Clusters** or **Update Groups** to apply changes

### Smart Path Detection

This feature automatically suggests cluster and group values based on your folder structure:

1. Click **Smart Detection** to analyze file paths
2. The suggested values will be displayed in the interface
3. Select the files you want to update
4. Click **Update Clusters** or **Update Groups** to apply the suggested changes

### Selection Options

- **Select All**: Select all files in the current view
- **Select None**: Deselect all files

## Troubleshooting

### Common Issues

- **XML Format Issues**: The application automatically fixes common XML formatting issues in XMP files
- **Missing Clusters/Groups**: Make sure your folder structure follows the recommended pattern
- **Performance with Large Libraries**: For very large preset collections, be patient during initial scanning

## Structure

- **main.py**: Main application GUI
- **xmp_manager.py**: Core functionality for handling XMP files

## Notes

This application directly modifies XMP files. It is recommended to make backups before making large batch changes.

---

© Rafael Andrade - 2025 - [www.rafaelandrade.art.br](http://www.rafaelandrade.art.br)
