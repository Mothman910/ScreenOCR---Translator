#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do obsługi globalnych skrótów klawiszowych.
"""

import logging
import threading
from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger('hotkeys')

class HotkeyManager(QObject):
    """Klasa zarządzająca globalnymi skrótami klawiszowymi."""
    
    # Sygnały
    capture_hotkey_pressed = pyqtSignal()  # Emitowany gdy naciśnięto skrót przechwytywania
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.listener = None
        self.current_keys = set()
        self.is_running = False
        self.lock = threading.Lock()
        
        # Parsowanie skrótów z ustawień
        self.configure_hotkeys()
        
        logger.info("Menedżer skrótów klawiszowych zainicjowany")
    
    def configure_hotkeys(self):
        """Konfiguruje skróty klawiszowe na podstawie ustawień."""
        try:
            # Pobranie skrótu do przechwytywania
            self.capture_hotkey_str = self.settings.get_hotkey('capture', 'Ctrl+Shift+X')
            
            # Parsowanie skrótu do formatu pynput
            self.capture_hotkey = self.parse_hotkey(self.capture_hotkey_str)
            
            logger.info(f"Skonfigurowano skrót przechwytywania: {self.capture_hotkey_str}")
            
        except Exception as e:
            logger.error(f"Błąd konfiguracji skrótów: {e}")
            # Ustawienie domyślnego skrótu w przypadku błędu
            self.capture_hotkey_str = 'Ctrl+Shift+X'
            self.capture_hotkey = self.parse_hotkey(self.capture_hotkey_str)
    
    def parse_hotkey(self, hotkey_str):
        """Parsuje string skrótu do listy klawiszy pynput."""
        key_map = {
            'ctrl': keyboard.Key.ctrl,
            'shift': keyboard.Key.shift,
            'alt': keyboard.Key.alt,
            'cmd': keyboard.Key.cmd,
            'win': keyboard.Key.cmd,
            'esc': keyboard.Key.esc,
            'space': keyboard.Key.space,
            'tab': keyboard.Key.tab,
            'enter': keyboard.Key.enter
        }
        
        keys = []
        for part in hotkey_str.lower().split('+'):
            part = part.strip()
            if part in key_map:
                keys.append(key_map[part])
            elif len(part) == 1:
                keys.append(part)
            else:
                # Obsługa klawiszy funkcyjnych (F1-F12)
                if part.startswith('f') and part[1:].isdigit():
                    f_num = int(part[1:])
                    if 1 <= f_num <= 12:
                        keys.append(getattr(keyboard.Key, part))
                else:
                    logger.warning(f"Nieznany klawisz w skrócie: {part}")
        
        return keys
    
    def start(self):
        """Uruchamia nasłuchiwanie skrótów klawiszowych."""
        if self.is_running:
            return
        
        try:
            self.is_running = True
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            logger.info("Uruchomiono nasłuchiwanie skrótów klawiszowych")
        except Exception as e:
            logger.error(f"Błąd uruchamiania nasłuchiwania skrótów: {e}")
            self.is_running = False
    
    def stop(self):
        """Zatrzymuje nasłuchiwanie skrótów klawiszowych."""
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            with self.lock:
                self.current_keys.clear()
            
            logger.info("Zatrzymano nasłuchiwanie skrótów klawiszowych")
        except Exception as e:
            logger.error(f"Błąd zatrzymywania nasłuchiwania skrótów: {e}")
    
    def on_press(self, key):
        """Obsługa naciśnięcia klawisza."""
        try:
            # Konwersja klawisza do formatu porównywalnego
            if hasattr(key, 'char') and key.char:
                key_to_add = key.char.lower()
            else:
                key_to_add = key
            
            # Dodanie klawisza do zbioru aktualnie naciśniętych
            with self.lock:
                self.current_keys.add(key_to_add)
                
                # Sprawdzanie, czy naciśnięty został skrót przechwytywania
                if self.is_hotkey_pressed(self.capture_hotkey):
                    logger.info("Wykryto skrót przechwytywania")
                    self.capture_hotkey_pressed.emit()
        except Exception as e:
            logger.error(f"Błąd obsługi naciśnięcia klawisza: {e}")
    
    def on_release(self, key):
        """Obsługa zwolnienia klawisza."""
        try:
            # Konwersja klawisza do formatu porównywalnego
            if hasattr(key, 'char') and key.char:
                key_to_remove = key.char.lower()
            else:
                key_to_remove = key
            
            # Usunięcie klawisza ze zbioru aktualnie naciśniętych
            with self.lock:
                self.current_keys.discard(key_to_remove)
        except Exception as e:
            logger.error(f"Błąd obsługi zwolnienia klawisza: {e}")
    
    def is_hotkey_pressed(self, hotkey):
        """Sprawdza, czy naciśnięty został dany skrót klawiszowy."""
        # Sprawdzenie czy wszystkie klawisze ze skrótu są naciśnięte
        return all(k in self.current_keys for k in hotkey)
    
    def update_hotkeys(self):
        """Aktualizuje skróty klawiszowe po zmianie ustawień."""
        self.configure_hotkeys()
        
        # Restart nasłuchiwania, jeśli już działa
        if self.is_running and self.listener:
            self.stop()
            self.start()