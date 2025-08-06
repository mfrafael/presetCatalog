"""
Stylesheet for the XMP Preset Manager application
Minimal style to maintain consistent spacing without overriding system colors
"""

STYLE_SHEET = """
QLabel[styleClass="header"] {
    font-weight: bold;
    font-size: 12px;
}

QPushButton {
    padding: 4px 12px;
}

QLineEdit {
    padding: 4px;
}

QTableWidget {
    gridline-color: #e0e0e0;
    border: none;
    border-radius: 4px;
}

QHeaderView::section {
    padding: 4px;
    background-color: transparent;
    border: none;
    border-bottom: 1px solid #e0e0e0;
}

QTableView::item {
    border: none;
    padding: 2px;
}

/* Define a cor das linhas alternadas para ser mais sutil */
QTableWidget {
    alternate-background-color: #f7f7f7;
}

QCheckBox {
    spacing: 5px;
}
"""
