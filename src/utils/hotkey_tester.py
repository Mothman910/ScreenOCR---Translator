#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do testowania skrótów klawiszowych.
"""

import sys
import logging
import threading
from pynput import keyboard
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QApplication, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

logger = logging.getLogger('hotkey_tester')

class KeyboardListener(QObject):
    """Klasa nasłuchująca klawisze do testowania."""
    
    key_pressed = pyqtSignal(object)
    key_released = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listener = None
        self.is_running = False
        self.current_keys = set()
        self.lock = threading.Lock()
    
    def start(self):
        """Uruchamia nasłuchiwanie klawiszy."""
        if self.is_running:
            return
        
        try:
            self.is_running = True
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            logger.debug("Rozpoczęto nasłuchiwanie klawiszy testowych")
        except Exception as e:
            logger.error(f"Błąd uruchamiania nasłuchiwania klawiszy: {e}")
            self.is_running = False
    
    def stop(self):
        """Zatrzymuje nasłuchiwanie klawiszy."""
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            with self.lock:
                self.current_keys.clear()
            
            logger.debug("Zatrzymano nasłuchiwanie klawiszy testowych")
        except Exception as e:
            logger.error(f"Błąd zatrzymywania nasłuchiwania klawiszy: {e}")
    
    def on_press(self, key):
        """Obsługa naciśnięcia klawisza."""
        try:
            with self.lock:
                self.current_keys.add(key)
                
            # Emitowanie sygnału
            self.key_pressed.emit(key)
            
        except Exception as e:
            logger.error(f"Błąd obsługi naciśnięcia klawisza: {e}")
    
    def on_release(self, key):
        """Obsługa zwolnienia klawisza."""
        try:
            with self.lock:
                self.current_keys.discard(key)
                
            # Emitowanie sygnału
            self.key_released.emit(key)
            
        except Exception as e:
            logger.error(f"Błąd obsługi zwolnienia klawisza: {e}")


class HotkeyTesterDialog(QDialog):
    """Okno dialogowe do testowania skrótów klawiszowych."""
    
    def __init__(self, hotkey_to_test, parent=None):
        super().__init__(parent)
        self.hotkey_to_test = hotkey_to_test
        self.setWindowTitle("Test skrótu klawiszowego")
        self.setMinimumSize(600, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # Stworzenie słuchacza klawiatury
        self.listener = KeyboardListener()
        self.listener.key_pressed.connect(self.on_key_pressed)
        self.listener.key_released.connect(self.on_key_released)
        
        self.setup_ui()
        
        # Automatyczne uruchomienie nasłuchiwania
        self.listener.start()
        
        # Ustawienie timera do aktualizacji statusu
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(100)  # Aktualizacja co 100ms
        
        logger.debug(f"Utworzono okno testowe dla skrótu: {hotkey_to_test}")
    
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        layout = QVBoxLayout()
        
        # Etykieta informacyjna
        info_label = QLabel(
            f"<b>Testowanie skrótu klawiszowego: {self.hotkey_to_test}</b><br>"
            "Naciśnij kombinację klawiszy, aby sprawdzić czy działa poprawnie.<br>"
            "Wszystkie naciśnięte klawisze zostaną wyświetlone poniżej."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Obszar statusu skrótu
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Skrót nie został naciśnięty")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        status_layout.addWidget(self.status_label)
        
        self.enable_debug_checkbox = QCheckBox("Pokaż szczegółowe informacje o klawiszach")
        self.enable_debug_checkbox.setChecked(True)
        status_layout.addWidget(self.enable_debug_checkbox)
        
        layout.addLayout(status_layout)
        
        # Obszar logów
        log_label = QLabel("Log naciśnięć klawiszy:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        layout.addWidget(self.log_text)
        
        # Przycisk wyczyść logi
        clear_button = QPushButton("Wyczyść logi")
        clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(clear_button)
        
        # Przyciski OK/Anuluj
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Zamknij")
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_key_pressed(self, key):
        """Obsługa zdarzenia naciśnięcia klawisza."""
        if self.enable_debug_checkbox.isChecked():
            key_description = self.get_key_description(key)
            self.log_text.append(f"Naciśnięto: {key_description}")
            self.log_text.append(f"Typ klawisza: {type(key).__name__}")
            
            # Dodatkowe informacje dla KeyCode
            if isinstance(key, keyboard.KeyCode):
                if hasattr(key, 'char') and key.char:
                    self.log_text.append(f"Znak: '{key.char}', Kod: {ord(key.char)}")
                if hasattr(key, 'vk') and key.vk:
                    self.log_text.append(f"Kod wirtualny: {key.vk}")
            
            self.log_text.append("---")
    
    def on_key_released(self, key):
        """Obsługa zdarzenia zwolnienia klawisza."""
        if self.enable_debug_checkbox.isChecked():
            key_description = self.get_key_description(key)
            self.log_text.append(f"Zwolniono: {key_description}")
    
    def update_status(self):
        """Aktualizuje status skrótu klawiszowego."""
        try:
            # Poprawiony import - z uwzględnieniem ścieżki względnej
            import sys
            import os
            
            # Dodanie katalogu nadrzędnego do sys.path aby znaleźć moduły
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            # Import z pełnej ścieżki
            from utils.hotkeys import HotkeyManager
            
            # Stworzenie tymczasowego menedżera skrótów
            class TempSettings:
                def get_hotkey(self, action, default=None):
                    return self.hotkey_to_test
            
            temp_settings = TempSettings()
            temp_settings.hotkey_to_test = self.hotkey_to_test
            
            temp_manager = HotkeyManager(temp_settings)
            temp_manager.current_keys = self.listener.current_keys
            
            is_pressed = temp_manager.is_hotkey_pressed(temp_manager.capture_hotkey)
            
            if is_pressed:
                self.status_label.setText("Skrót ZOSTAŁ NACIŚNIĘTY")
                self.status_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.status_label.setText("Skrót NIE został naciśnięty")
                self.status_label.setStyleSheet("font-weight: bold; color: red;")
            
        except Exception as e:
            logger.error(f"Błąd aktualizacji statusu: {e}")
            self.status_label.setText(f"Błąd sprawdzania: {str(e)}")
            self.status_label.setStyleSheet("font-weight: bold; color: orange;")
    
    def get_key_description(self, key):
        """Zwraca opis klawisza."""
        try:
            if isinstance(key, keyboard.Key):
                return f"Klawisz specjalny: {key.name}"
            elif isinstance(key, keyboard.KeyCode):
                if hasattr(key, 'char') and key.char:
                    return f"Klawisz: '{key.char}'"
                else:
                    return f"KeyCode: {key}"
            else:
                return f"Inny obiekt: {key}"
        except Exception as e:
            return f"Nieznany klawisz: {key} (błąd: {e})"
    
    def clear_logs(self):
        """Czyści logi."""
        self.log_text.clear()
    
    def closeEvent(self, event):
        """Obsługa zamknięcia okna."""
        self.listener.stop()
        self.update_timer.stop()
        super().closeEvent(event)


# Jeśli uruchomiono jako samodzielny skrypt
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Przykładowy skrót do testowania
    test_hotkey = "Alt+F7"
    if len(sys.argv) > 1:
        test_hotkey = sys.argv[1]
    
    dialog = HotkeyTesterDialog(test_hotkey)
    dialog.exec()