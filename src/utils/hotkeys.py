#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do obsługi globalnych skrótów klawiszowych.
"""

import logging
import keyboard  # Nowa biblioteka do obsługi skrótów klawiszowych
import threading
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger('hotkeys')

class HotkeyManager(QObject):
    """Klasa zarządzająca globalnymi skrótami klawiszowymi."""
    
    # Sygnały
    capture_hotkey_pressed = pyqtSignal()  # Emitowany gdy naciśnięto skrót przechwytywania
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_running = False
        self.hotkey_thread = None
        self.registered_hotkeys = []
        
        # Parsowanie skrótów z ustawień
        self.configure_hotkeys()
        
        logger.info("Menedżer skrótów klawiszowych zainicjowany")
    
    def configure_hotkeys(self):
        """Konfiguruje skróty klawiszowe na podstawie ustawień."""
        try:
            # Pobranie skrótu do przechwytywania
            self.capture_hotkey_str = self.settings.get_hotkey('capture', 'alt+f7')
            
            # Konwersja do formatu dla biblioteki keyboard
            self.capture_hotkey = self._convert_to_keyboard_format(self.capture_hotkey_str)
            
            logger.info(f"Skonfigurowano skrót przechwytywania: {self.capture_hotkey}")
            
        except Exception as e:
            logger.error(f"Błąd konfiguracji skrótów: {e}")
            # Ustawienie domyślnego skrótu w przypadku błędu
            self.capture_hotkey_str = 'alt+f7'
            self.capture_hotkey = self._convert_to_keyboard_format(self.capture_hotkey_str)
    
    def _convert_to_keyboard_format(self, hotkey_str):
        """Konwertuje format skrótu do formatu obsługiwanego przez bibliotekę keyboard."""
        # Standardowe przekształcenie - zamienia + na małe litery
        return hotkey_str.lower().replace(' ', '')
    
    def start(self):
        """Uruchamia nasłuchiwanie skrótów klawiszowych."""
        if self.is_running:
            return
        
        try:
            # Konfiguracja funkcji callback dla skrótu
            def capture_callback():
                logger.info("Wykryto skrót przechwytywania!")
                # Emitujemy sygnał w bezpieczny sposób (w głównym wątku Qt)
                self.capture_hotkey_pressed.emit()
            
            # Rejestracja skrótu do przechwytywania
            keyboard.add_hotkey(self.capture_hotkey, capture_callback, suppress=True)
            self.registered_hotkeys.append(self.capture_hotkey)
            
            # Rejestrujemy F9 tylko jeśli nie jest już ustawiony jako główny skrót
            if self.capture_hotkey.lower() != 'f9':
                keyboard.add_hotkey('f9', capture_callback, suppress=True)
                self.registered_hotkeys.append('f9')
                logger.info(f"Uruchomiono nasłuchiwanie skrótów klawiszowych: {self.capture_hotkey} i F9")
            else:
                logger.info(f"Uruchomiono nasłuchiwanie skrótu klawiszowego: {self.capture_hotkey}")
            
            self.is_running = True
            
        except Exception as e:
            logger.error(f"Błąd uruchamiania nasłuchiwania skrótów: {e}")
            self.is_running = False
    
    def stop(self):
        """Zatrzymuje nasłuchiwanie skrótów klawiszowych."""
        if not self.is_running:
            return
        
        try:
            # Usunięcie wszystkich zarejestrowanych skrótów
            for hotkey in self.registered_hotkeys:
                keyboard.remove_hotkey(hotkey)
            
            self.registered_hotkeys = []
            self.is_running = False
            logger.info("Zatrzymano nasłuchiwanie skrótów klawiszowych")
            
        except Exception as e:
            logger.error(f"Błąd zatrzymywania nasłuchiwania skrótów: {e}")
    
    def update_hotkeys(self):
        """Aktualizuje skróty klawiszowe po zmianie ustawień."""
        # Zatrzymaj nasłuchiwanie, jeśli jest aktywne
        if self.is_running:
            self.stop()
        
        # Zaktualizuj konfigurację
        self.configure_hotkeys()
        
        # Uruchom ponownie nasłuchiwanie
        self.start()