#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prosty program testowy do skrótów klawiszowych.
Ten program uruchamia proste okno testowe, które rejestruje naciśnięcia klawiszy
i wyświetla informacje o nich. Jest niezależny od głównej aplikacji.
"""

import sys
import os
import time
import threading
import logging
from pynput import keyboard
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

# Konfiguracja loggingu
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_hotkeys')

class KeyboardListener(QObject):
    """Klasa nasłuchująca klawiszy."""
    
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
            logger.debug("Rozpoczęto nasłuchiwanie klawiszy")
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
            
            logger.debug("Zatrzymano nasłuchiwanie klawiszy")
        except Exception as e:
            logger.error(f"Błąd zatrzymywania nasłuchiwania klawiszy: {e}")
    
    def on_press(self, key):
        """Obsługa naciśnięcia klawisza."""
        try:
            with self.lock:
                # Dodanie klawisza do zbioru aktualnie naciśniętych
                self.current_keys.add(key)
                
                # Wyświetlanie informacji o klawiszu
                key_info = self.get_key_info(key)
                logger.debug(f"Naciśnięto: {key_info}")
            
            # Emitowanie sygnału z informacją o klawiszu
            self.key_pressed.emit(key)
            
        except Exception as e:
            logger.error(f"Błąd obsługi naciśnięcia klawisza: {e}")
    
    def on_release(self, key):
        """Obsługa zwolnienia klawisza."""
        try:
            with self.lock:
                # Usunięcie klawisza ze zbioru aktualnie naciśniętych
                self.current_keys.discard(key)
                
                # Wyświetlanie informacji o klawiszu
                key_info = self.get_key_info(key)
                logger.debug(f"Zwolniono: {key_info}")
            
            # Emitowanie sygnału z informacją o klawiszu
            self.key_released.emit(key)
            
        except Exception as e:
            logger.error(f"Błąd obsługi zwolnienia klawisza: {e}")
    
    def get_key_info(self, key):
        """Zwraca szczegółowe informacje o klawiszu."""
        try:
            result = f"Typ: {type(key).__name__}, "
            
            # Dla klawiszy specjalnych
            if isinstance(key, keyboard.Key):
                result += f"Key: {key.name}"
            
            # Dla klawiszy znaków
            elif isinstance(key, keyboard.KeyCode):
                result += f"KeyCode: {key}"
                if hasattr(key, 'char') and key.char:
                    result += f", Znak: '{key.char}', Kod ASCII: {ord(key.char)}"
                if hasattr(key, 'vk') and key.vk:
                    result += f", VK: {key.vk}"
            
            # Dla innych typów
            else:
                result += f"Inny: {key}"
                
            return result
        except Exception as e:
            return f"Błąd opisu klawisza: {e}"

class TestMainWindow(QMainWindow):
    """Główne okno testowe aplikacji."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test skrótów klawiszowych")
        self.setGeometry(100, 100, 800, 600)
        
        # Centralny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Informacje o teście
        info_label = QLabel(
            "<h2>Test skrótów klawiszowych</h2>"
            "<p>Ten program testuje działanie skrótów klawiszowych.</p>"
            "<p>Naciskaj różne kombinacje klawiszy, aby zobaczyć ich wykrywanie:</p>"
            "<ul>"
            "<li><b>Alt+F7</b> - nowy domyślny skrót aplikacji</li>"
            "<li><b>Ctrl+Alt+T</b> - alternatywny skrót</li>"
            "<li><b>F9</b> - prosty skrót funkcyjny</li>"
            "</ul>"
        )
        layout.addWidget(info_label)
        
        # Aktualnie naciśnięte klawisze
        self.keys_label = QLabel("Naciśnięte klawisze: Brak")
        layout.addWidget(self.keys_label)
        
        # Skrót testowy
        self.test_hotkey = "Alt+F7"
        self.hotkey_status = QLabel(f"Skrót <b>{self.test_hotkey}</b>: <span style='color: red;'>NIE naciśnięty</span>")
        layout.addWidget(self.hotkey_status)
        
        # Pole z logami
        self.log_label = QLabel("Logi zdarzeń:")
        layout.addWidget(self.log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Przycisk do czyszczenia logów
        self.clear_button = QPushButton("Wyczyść logi")
        self.clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(self.clear_button)
        
        # Inicjalizacja nasłuchiwania klawiszy
        self.keyboard_listener = KeyboardListener()
        self.keyboard_listener.key_pressed.connect(self.on_key_pressed)
        self.keyboard_listener.key_released.connect(self.on_key_released)
        self.keyboard_listener.start()
        
        # Timer do aktualizacji statusu
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(100)  # Aktualizacja co 100ms
    
    def on_key_pressed(self, key):
        """Obsługa zdarzenia naciśnięcia klawisza."""
        key_info = self.keyboard_listener.get_key_info(key)
        self.log_text.append(f"Naciśnięto: {key_info}")
    
    def on_key_released(self, key):
        """Obsługa zdarzenia zwolnienia klawisza."""
        key_info = self.keyboard_listener.get_key_info(key)
        self.log_text.append(f"Zwolniono: {key_info}")
    
    def update_status(self):
        """Aktualizacja informacji o naciśniętych klawiszach."""
        with self.keyboard_listener.lock:
            keys_info = []
            for key in self.keyboard_listener.current_keys:
                if isinstance(key, keyboard.Key):
                    keys_info.append(f"{key.name}")
                elif isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char:
                    keys_info.append(f"'{key.char}'")
                else:
                    keys_info.append(f"{key}")
            
            if keys_info:
                self.keys_label.setText(f"Naciśnięte klawisze: {', '.join(keys_info)}")
            else:
                self.keys_label.setText("Naciśnięte klawisze: Brak")
            
            # Sprawdzenie czy naciśnięty jest testowy skrót
            hotkey_pressed = self.is_hotkey_pressed()
            if hotkey_pressed:
                self.hotkey_status.setText(f"Skrót <b>{self.test_hotkey}</b>: <span style='color: green;'>NACIŚNIĘTY</span>")
            else:
                self.hotkey_status.setText(f"Skrót <b>{self.test_hotkey}</b>: <span style='color: red;'>NIE naciśnięty</span>")
    
    def is_hotkey_pressed(self):
        """Sprawdza czy naciśnięty jest testowy skrót klawiszowy."""
        try:
            # Parsowanie skrótu z formatu tekstowego
            parts = self.test_hotkey.lower().split('+')
            
            # Sprawdzenie czy wszystkie części skrótu są naciśnięte
            with self.keyboard_listener.lock:
                # Sprawdzenie Alt
                if 'alt' in parts:
                    alt_pressed = any(
                        isinstance(k, keyboard.Key) and 
                        (k == keyboard.Key.alt_l or k == keyboard.Key.alt_r or k == keyboard.Key.alt) 
                        for k in self.keyboard_listener.current_keys
                    )
                    if not alt_pressed:
                        return False
                
                # Sprawdzenie Ctrl
                if 'ctrl' in parts:
                    ctrl_pressed = any(
                        isinstance(k, keyboard.Key) and 
                        (k == keyboard.Key.ctrl_l or k == keyboard.Key.ctrl_r or k == keyboard.Key.ctrl) 
                        for k in self.keyboard_listener.current_keys
                    )
                    if not ctrl_pressed:
                        return False
                
                # Sprawdzenie Shift
                if 'shift' in parts:
                    shift_pressed = any(
                        isinstance(k, keyboard.Key) and 
                        (k == keyboard.Key.shift_l or k == keyboard.Key.shift_r or k == keyboard.Key.shift) 
                        for k in self.keyboard_listener.current_keys
                    )
                    if not shift_pressed:
                        return False
                
                # Sprawdzenie klawiszy funkcyjnych
                for part in parts:
                    if part.startswith('f') and part[1:].isdigit():
                        f_key = getattr(keyboard.Key, part, None)
                        if f_key and f_key not in self.keyboard_listener.current_keys:
                            return False
                
                # Sprawdzenie zwykłych klawiszy (litery, cyfry)
                for part in parts:
                    if len(part) == 1 and part.isalnum():
                        key_pressed = any(
                            isinstance(k, keyboard.KeyCode) and 
                            hasattr(k, 'char') and k.char and k.char.lower() == part.lower()
                            for k in self.keyboard_listener.current_keys
                        )
                        if not key_pressed:
                            return False
            
            return True
        except Exception as e:
            logger.error(f"Błąd sprawdzania skrótu: {e}")
            return False
    
    def clear_logs(self):
        """Czyści pole z logami."""
        self.log_text.clear()
    
    def closeEvent(self, event):
        """Obsługa zdarzenia zamknięcia okna."""
        # Zatrzymanie nasłuchiwania klawiszy i timera
        self.update_timer.stop()
        self.keyboard_listener.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())