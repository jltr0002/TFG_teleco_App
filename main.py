"""
Main GUI application for antenna synthesis.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set larger default font for the entire application
    font = QFont()
    font.setPointSize(11)  # Increase from default size (usually 8-9) to 11
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()