#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ScreenOCR & Translator - Narzędzie do rozpoznawania i tłumaczenia tekstu z ekranu w grach.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Ustawienie ścieżek
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
RESOURCES_DIR = os.path.join(PARENT_DIR, 'resources')
ICON_PATH = os.path.join(PARENT_DIR, 'icon.ico')

# Importy wewnętrzne
from tray_icon import SystemTrayIcon
from settings import Settings

# Konfiguracja loggingu
logging.basicConfig(
    filename=os.path.join(PARENT_DIR, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main')

def main():
    """Główna funkcja aplikacji"""
    logger.info("Uruchamianie aplikacji ScreenOCR & Translator")
    
    # Inicjalizacja aplikacji
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Aplikacja działa nawet gdy nie ma aktywnych okien
    app.setWindowIcon(QIcon(ICON_PATH))
    
    # Wczytanie ustawień
    settings = Settings()
    
    # Utworzenie ikony w zasobniku systemowym
    tray_icon = SystemTrayIcon(QIcon(ICON_PATH), app, settings)
    tray_icon.show()
    
    logger.info("Aplikacja uruchomiona pomyślnie")
    
    # Uruchomienie pętli aplikacji
    sys.exit(app.exec())

if __name__ == "__main__":
    main()