#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł obsługujący ustawienia aplikacji.
"""

import os
import json
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget,
    QComboBox, QCheckBox, QSpinBox, QColorDialog, QFileDialog, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

logger = logging.getLogger('settings')

class Settings:
    """Klasa zarządzająca ustawieniami aplikacji."""
    
    def __init__(self):
        """Inicjalizacja ustawień aplikacji."""
        # Określenie ścieżki do pliku ustawień
        self.settings_dir = os.path.join(
            os.path.expanduser('~'), 
            'AppData', 'Local', 'ScreenOCR & Translator'
        )
        self.settings_file = os.path.join(self.settings_dir, 'settings.json')
        
        # Domyślne ustawienia
        self.default_settings = {
            'general': {
                'language': 'pl',
                'start_with_windows': False,
                'check_updates': True
            },
            'hotkeys': {
                'capture': 'Ctrl+Shift+X',
            },
            'ocr': {
                'engine': 'tesseract',
                'language': 'eng',  # język dla OCR
                'preprocess': True,  # wstępne przetwarzanie obrazu
                'confidence_threshold': 70  # próg pewności (%)
            },
            'translation': {
                'engine': 'google',  # google, deepl
                'source_lang': 'en',
                'target_lang': 'pl',
                'auto_copy': False  # automatycznie kopiuj przetłumaczony tekst
            },
            'popup': {
                'position': 'top-right',  # pozycja popup'u
                'width': 300,  # szerokość popup'u
                'height': 200,  # wysokość popup'u
                'opacity': 80,  # przezroczystość (%)
                'auto_hide': True,  # automatycznie ukryj po czasie
                'display_time': 5,  # czas wyświetlania w sekundach
                'bg_color': '#2E2E2E',  # kolor tła
                'text_color': '#FFFFFF',  # kolor tekstu
                'show_original': True  # pokazuj oryginalny tekst
            },
            'paths': {
                'tesseract': '',  # ścieżka do Tesseract OCR
                'tessdata': ''  # ścieżka do danych językowych Tesseract
            }
        }
        
        # Wczytanie ustawień lub utworzenie domyślnych
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Wczytuje ustawienia z pliku lub tworzy domyślne."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                logger.info("Wczytano ustawienia z pliku")
                # Uzupełnianie brakujących ustawień domyślnymi
                settings = self._merge_settings(settings, self.default_settings)
                return settings
            except Exception as e:
                logger.error(f"Błąd wczytywania ustawień: {e}")
                return self.default_settings.copy()
        else:
            logger.info("Tworzenie domyślnych ustawień")
            # Utworzenie katalogu ustawień, jeśli nie istnieje
            os.makedirs(self.settings_dir, exist_ok=True)
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def _merge_settings(self, user_settings, default_settings):
        """Łączy ustawienia użytkownika z domyślnymi, uzupełniając brakujące wartości."""
        merged_settings = default_settings.copy()
        
        for category, values in user_settings.items():
            if category in merged_settings:
                if isinstance(values, dict):
                    for key, value in values.items():
                        if key in merged_settings[category]:
                            merged_settings[category][key] = value
                else:
                    merged_settings[category] = values
        
        return merged_settings
    
    def save_settings(self, settings=None):
        """Zapisuje ustawienia do pliku."""
        if settings is None:
            settings = self.settings
        
        try:
            os.makedirs(self.settings_dir, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            logger.info("Zapisano ustawienia do pliku")
            return True
        except Exception as e:
            logger.error(f"Błąd zapisywania ustawień: {e}")
            return False
    
    def get(self, category, key, default=None):
        """Pobiera wartość ustawienia."""
        try:
            return self.settings[category][key]
        except KeyError:
            if default is None and category in self.default_settings and key in self.default_settings[category]:
                return self.default_settings[category][key]
            return default
    
    def set(self, category, key, value):
        """Ustawia wartość ustawienia i zapisuje do pliku."""
        if category not in self.settings:
            self.settings[category] = {}
        
        self.settings[category][key] = value
        return self.save_settings()
    
    def get_hotkey(self, action, default=None):
        """Pobiera skrót klawiszowy dla danej akcji."""
        return self.get('hotkeys', action, default)
    
    def set_hotkey(self, action, hotkey):
        """Ustawia skrót klawiszowy dla danej akcji."""
        return self.set('hotkeys', action, hotkey)

class SettingsDialog(QDialog):
    """Dialog ustawień aplikacji."""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ustawienia")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        self.load_settings_to_ui()
        
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika dialogu ustawień."""
        layout = QVBoxLayout()
        
        # Zakładki ustawień
        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.hotkeys_tab = QWidget()
        self.ocr_tab = QWidget()
        self.translation_tab = QWidget()
        self.popup_tab = QWidget()
        self.advanced_tab = QWidget()
        
        self.setup_general_tab()
        self.setup_hotkeys_tab()
        self.setup_ocr_tab()
        self.setup_translation_tab()
        self.setup_popup_tab()
        self.setup_advanced_tab()
        
        self.tabs.addTab(self.general_tab, "Ogólne")
        self.tabs.addTab(self.hotkeys_tab, "Skróty klawiszowe")
        self.tabs.addTab(self.ocr_tab, "OCR")
        self.tabs.addTab(self.translation_tab, "Tłumaczenie")
        self.tabs.addTab(self.popup_tab, "Wyświetlanie")
        self.tabs.addTab(self.advanced_tab, "Zaawansowane")
        
        layout.addWidget(self.tabs)
        
        # Przyciski OK/Anuluj
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.save_and_close)
        
        self.cancel_button = QPushButton("Anuluj")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_general_tab(self):
        """Konfiguracja zakładki ogólnych ustawień."""
        layout = QFormLayout()
        
        # Język interfejsu
        self.language_combo = QComboBox()
        self.language_combo.addItem("Polski", "pl")
        self.language_combo.addItem("English", "en")
        layout.addRow("Język interfejsu:", self.language_combo)
        
        # Autostart z Windowsem
        self.autostart_check = QCheckBox()
        layout.addRow("Uruchamiaj z systemem:", self.autostart_check)
        
        # Sprawdzanie aktualizacji
        self.check_updates_check = QCheckBox()
        layout.addRow("Sprawdzaj aktualizacje:", self.check_updates_check)
        
        self.general_tab.setLayout(layout)
    
    def setup_hotkeys_tab(self):
        """Konfiguracja zakładki skrótów klawiszowych."""
        layout = QFormLayout()
        
        # Skrót do przechwytywania ekranu
        self.capture_hotkey_edit = QLineEdit()
        self.capture_hotkey_edit.setPlaceholderText("Kliknij i naciśnij kombinację klawiszy")
        self.capture_hotkey_edit.setReadOnly(True)
        layout.addRow("Przechwyć ekran:", self.capture_hotkey_edit)
        
        self.hotkeys_tab.setLayout(layout)
    
    def setup_ocr_tab(self):
        """Konfiguracja zakładki OCR."""
        layout = QFormLayout()
        
        # Silnik OCR
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItem("Tesseract OCR", "tesseract")
        layout.addRow("Silnik OCR:", self.ocr_engine_combo)
        
        # Język OCR
        self.ocr_language_combo = QComboBox()
        self.ocr_language_combo.addItem("Angielski", "eng")
        self.ocr_language_combo.addItem("Polski", "pol")
        layout.addRow("Język rozpoznawania:", self.ocr_language_combo)
        
        # Wstępne przetwarzanie obrazu
        self.preprocess_check = QCheckBox()
        layout.addRow("Przetwarzanie obrazu:", self.preprocess_check)
        
        # Próg pewności
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 100)
        self.threshold_spin.setSuffix("%")
        layout.addRow("Próg pewności:", self.threshold_spin)
        
        self.ocr_tab.setLayout(layout)
    
    def setup_translation_tab(self):
        """Konfiguracja zakładki tłumaczenia."""
        layout = QFormLayout()
        
        # Silnik tłumaczenia
        self.translation_engine_combo = QComboBox()
        self.translation_engine_combo.addItem("Google Translate", "google")
        self.translation_engine_combo.addItem("DeepL", "deepl")
        layout.addRow("Silnik tłumaczenia:", self.translation_engine_combo)
        
        # Język źródłowy
        self.source_language_combo = QComboBox()
        self.source_language_combo.addItem("Angielski", "en")
        layout.addRow("Język źródłowy:", self.source_language_combo)
        
        # Język docelowy
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItem("Polski", "pl")
        layout.addRow("Język docelowy:", self.target_language_combo)
        
        # Automatyczne kopiowanie
        self.auto_copy_check = QCheckBox()
        layout.addRow("Auto-kopiowanie tłumaczenia:", self.auto_copy_check)
        
        self.translation_tab.setLayout(layout)
    
    def setup_popup_tab(self):
        """Konfiguracja zakładki wyświetlania pop-up."""
        layout = QFormLayout()
        
        # Pozycja pop-up
        self.position_combo = QComboBox()
        self.position_combo.addItem("Prawy górny róg", "top-right")
        self.position_combo.addItem("Lewy górny róg", "top-left")
        self.position_combo.addItem("Prawy dolny róg", "bottom-right")
        self.position_combo.addItem("Lewy dolny róg", "bottom-left")
        self.position_combo.addItem("Środek", "center")
        layout.addRow("Pozycja pop-up:", self.position_combo)
        
        # Szerokość pop-up
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 800)
        self.width_spin.setSuffix(" px")
        layout.addRow("Szerokość:", self.width_spin)
        
        # Wysokość pop-up
        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 600)
        self.height_spin.setSuffix(" px")
        layout.addRow("Wysokość:", self.height_spin)
        
        # Przezroczystość
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(10, 100)
        self.opacity_spin.setSuffix("%")
        layout.addRow("Przezroczystość:", self.opacity_spin)
        
        # Automatyczne ukrywanie
        self.auto_hide_check = QCheckBox()
        layout.addRow("Automatyczne ukrywanie:", self.auto_hide_check)
        
        # Czas wyświetlania
        self.display_time_spin = QSpinBox()
        self.display_time_spin.setRange(1, 30)
        self.display_time_spin.setSuffix(" s")
        layout.addRow("Czas wyświetlania:", self.display_time_spin)
        
        # Kolor tła
        self.bg_color_button = QPushButton()
        self.bg_color_button.clicked.connect(self.select_bg_color)
        layout.addRow("Kolor tła:", self.bg_color_button)
        
        # Kolor tekstu
        self.text_color_button = QPushButton()
        self.text_color_button.clicked.connect(self.select_text_color)
        layout.addRow("Kolor tekstu:", self.text_color_button)
        
        # Pokazuj oryginalny tekst
        self.show_original_check = QCheckBox()
        layout.addRow("Pokazuj oryginalny tekst:", self.show_original_check)
        
        self.popup_tab.setLayout(layout)
    
    def setup_advanced_tab(self):
        """Konfiguracja zakładki zaawansowanych ustawień."""
        layout = QFormLayout()
        
        # Ścieżka do Tesseract OCR
        self.tesseract_path_edit = QLineEdit()
        self.tesseract_path_edit.setReadOnly(True)
        self.tesseract_path_button = QPushButton("Wybierz...")
        self.tesseract_path_button.clicked.connect(self.select_tesseract_path)
        
        tesseract_layout = QHBoxLayout()
        tesseract_layout.addWidget(self.tesseract_path_edit)
        tesseract_layout.addWidget(self.tesseract_path_button)
        
        layout.addRow("Ścieżka do Tesseract:", tesseract_layout)
        
        # Ścieżka do danych tessdata
        self.tessdata_path_edit = QLineEdit()
        self.tessdata_path_edit.setReadOnly(True)
        self.tessdata_path_button = QPushButton("Wybierz...")
        self.tessdata_path_button.clicked.connect(self.select_tessdata_path)
        
        tessdata_layout = QHBoxLayout()
        tessdata_layout.addWidget(self.tessdata_path_edit)
        tessdata_layout.addWidget(self.tessdata_path_button)
        
        layout.addRow("Ścieżka do tessdata:", tessdata_layout)
        
        self.advanced_tab.setLayout(layout)
    
    def load_settings_to_ui(self):
        """Wczytuje ustawienia do interfejsu użytkownika."""
        # Zakładka Ogólne
        self.set_combo_by_value(self.language_combo, self.settings.get('general', 'language'))
        self.autostart_check.setChecked(self.settings.get('general', 'start_with_windows'))
        self.check_updates_check.setChecked(self.settings.get('general', 'check_updates'))
        
        # Zakładka Skróty klawiszowe
        self.capture_hotkey_edit.setText(self.settings.get_hotkey('capture'))
        
        # Zakładka OCR
        self.set_combo_by_value(self.ocr_engine_combo, self.settings.get('ocr', 'engine'))
        self.set_combo_by_value(self.ocr_language_combo, self.settings.get('ocr', 'language'))
        self.preprocess_check.setChecked(self.settings.get('ocr', 'preprocess'))
        self.threshold_spin.setValue(self.settings.get('ocr', 'confidence_threshold'))
        
        # Zakładka Tłumaczenie
        self.set_combo_by_value(self.translation_engine_combo, self.settings.get('translation', 'engine'))
        self.set_combo_by_value(self.source_language_combo, self.settings.get('translation', 'source_lang'))
        self.set_combo_by_value(self.target_language_combo, self.settings.get('translation', 'target_lang'))
        self.auto_copy_check.setChecked(self.settings.get('translation', 'auto_copy'))
        
        # Zakładka Wyświetlanie
        self.set_combo_by_value(self.position_combo, self.settings.get('popup', 'position'))
        self.width_spin.setValue(self.settings.get('popup', 'width'))
        self.height_spin.setValue(self.settings.get('popup', 'height'))
        self.opacity_spin.setValue(self.settings.get('popup', 'opacity'))
        self.auto_hide_check.setChecked(self.settings.get('popup', 'auto_hide'))
        self.display_time_spin.setValue(self.settings.get('popup', 'display_time'))
        self.update_color_button(self.bg_color_button, self.settings.get('popup', 'bg_color'))
        self.update_color_button(self.text_color_button, self.settings.get('popup', 'text_color'))
        self.show_original_check.setChecked(self.settings.get('popup', 'show_original'))
        
        # Zakładka Zaawansowane
        self.tesseract_path_edit.setText(self.settings.get('paths', 'tesseract'))
        self.tessdata_path_edit.setText(self.settings.get('paths', 'tessdata'))
    
    def save_settings_from_ui(self):
        """Zapisuje ustawienia z interfejsu użytkownika."""
        # Zakładka Ogólne
        self.settings.set('general', 'language', self.get_combo_value(self.language_combo))
        self.settings.set('general', 'start_with_windows', self.autostart_check.isChecked())
        self.settings.set('general', 'check_updates', self.check_updates_check.isChecked())
        
        # Zakładka Skróty klawiszowe
        self.settings.set_hotkey('capture', self.capture_hotkey_edit.text())
        
        # Zakładka OCR
        self.settings.set('ocr', 'engine', self.get_combo_value(self.ocr_engine_combo))
        self.settings.set('ocr', 'language', self.get_combo_value(self.ocr_language_combo))
        self.settings.set('ocr', 'preprocess', self.preprocess_check.isChecked())
        self.settings.set('ocr', 'confidence_threshold', self.threshold_spin.value())
        
        # Zakładka Tłumaczenie
        self.settings.set('translation', 'engine', self.get_combo_value(self.translation_engine_combo))
        self.settings.set('translation', 'source_lang', self.get_combo_value(self.source_language_combo))
        self.settings.set('translation', 'target_lang', self.get_combo_value(self.target_language_combo))
        self.settings.set('translation', 'auto_copy', self.auto_copy_check.isChecked())
        
        # Zakładka Wyświetlanie
        self.settings.set('popup', 'position', self.get_combo_value(self.position_combo))
        self.settings.set('popup', 'width', self.width_spin.value())
        self.settings.set('popup', 'height', self.height_spin.value())
        self.settings.set('popup', 'opacity', self.opacity_spin.value())
        self.settings.set('popup', 'auto_hide', self.auto_hide_check.isChecked())
        self.settings.set('popup', 'display_time', self.display_time_spin.value())
        self.settings.set('popup', 'bg_color', self.bg_color_button.property('color'))
        self.settings.set('popup', 'text_color', self.text_color_button.property('color'))
        self.settings.set('popup', 'show_original', self.show_original_check.isChecked())
        
        # Zakładka Zaawansowane
        self.settings.set('paths', 'tesseract', self.tesseract_path_edit.text())
        self.settings.set('paths', 'tessdata', self.tessdata_path_edit.text())
        
        # Konfiguracja autostartu z Windows
        self.configure_autostart()
    
    def configure_autostart(self):
        """Konfiguruje autostart aplikacji z systemem Windows."""
        # Implementacja autostartu z Windows (używając rejestru Windows)
        # Będzie zaimplementowana w przyszłości
        pass
    
    def select_bg_color(self):
        """Wybór koloru tła pop-up."""
        current_color = QColor(self.settings.get('popup', 'bg_color'))
        color = QColorDialog.getColor(current_color, self, "Wybierz kolor tła")
        
        if color.isValid():
            self.update_color_button(self.bg_color_button, color.name())
    
    def select_text_color(self):
        """Wybór koloru tekstu pop-up."""
        current_color = QColor(self.settings.get('popup', 'text_color'))
        color = QColorDialog.getColor(current_color, self, "Wybierz kolor tekstu")
        
        if color.isValid():
            self.update_color_button(self.text_color_button, color.name())
    
    def select_tesseract_path(self):
        """Wybór ścieżki do Tesseract OCR."""
        path = QFileDialog.getExistingDirectory(self, "Wybierz ścieżkę do Tesseract OCR")
        if path:
            self.tesseract_path_edit.setText(path)
    
    def select_tessdata_path(self):
        """Wybór ścieżki do danych tessdata."""
        path = QFileDialog.getExistingDirectory(self, "Wybierz ścieżkę do danych tessdata")
        if path:
            self.tessdata_path_edit.setText(path)
    
    def update_color_button(self, button, color):
        """Aktualizuje przycisk koloru."""
        button.setProperty('color', color)
        button.setStyleSheet(f"background-color: {color}; min-width: 50px;")
    
    def set_combo_by_value(self, combo, value):
        """Ustawia indeks komboboxa na podstawie wartości."""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return
    
    def get_combo_value(self, combo):
        """Pobiera wartość z wybranego elementu komboboxa."""
        return combo.itemData(combo.currentIndex())
    
    def save_and_close(self):
        """Zapisuje ustawienia i zamyka dialog."""
        self.save_settings_from_ui()
        self.accept()