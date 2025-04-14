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

# Dodanie ścieżki do modułów
sys.path.append(BASE_DIR)

# Importy wewnętrzne
from tray_icon import SystemTrayIcon
from settings import Settings
from utils.hotkeys import HotkeyManager  # Dodanie importu menedżera skrótów

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
    
    # Inicjalizacja i uruchomienie menedżera skrótów klawiszowych
    hotkey_manager = HotkeyManager(settings)
    
    # Nowa implementacja - podłączenie bezpośrednio do sygnału screenshot_requested
    def on_hotkey_detected():
        logger.info("HOTKEY DETECTED: Wykryto skrót klawiszowy!")
        tray_icon.screenshot_requested.emit()  # Bezpośrednie emitowanie sygnału
    
    # Podłączenie funkcji nasłuchującej do sygnału z menedżera skrótów
    hotkey_manager.capture_hotkey_pressed.connect(on_hotkey_detected)
    
    # Ustawienie wysokiego poziomu debug dla modułu hotkeys
    hotkey_logger = logging.getLogger('hotkeys')
    hotkey_logger.setLevel(logging.DEBUG)
    
    # Dodanie handlera do wyświetlania logów w konsoli
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    hotkey_logger.addHandler(console_handler)
    
    # Uruchomienie nasłuchiwania skrótów
    hotkey_manager.start()
    
    logger.info("Aplikacja uruchomiona pomyślnie")
    logger.info(f"Nasłuchiwanie skrótu przechwytywania: {settings.get_hotkey('capture')}")
    
    # Zachowanie referencji do menedżera skrótów (ważne!)
    app.hotkey_manager = hotkey_manager
    
    # Uruchomienie pętli aplikacji
    sys.exit(app.exec())

if __name__ == "__main__":
    main()