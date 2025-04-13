#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł odpowiedzialny za wyświetlanie pop-upu z tłumaczeniem.
"""

import logging
import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QGuiApplication, QScreen

logger = logging.getLogger('popup')

class TranslationPopup(QWidget):
    """Widget wyświetlający tłumaczenie jako nakładka na ekranie."""
    
    closed = pyqtSignal()  # Sygnał emitowany przy zamknięciu pop-upu
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.dragging = False
        self.drag_position = QPoint()
        self.auto_hide_timer = None
        self.original_text = ""
        self.translated_text = ""
        
        self.setup_ui()
        
        logger.info("Popup tłumaczenia zainicjowany")
    
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Ustawienia okna
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Wymiary pop-upu
        width = self.settings.get('popup', 'width')
        height = self.settings.get('popup', 'height')
        self.setFixedSize(width, height)
        
        # Główny układ
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Panel główny
        self.main_panel = QFrame()
        self.main_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_panel.setAutoFillBackground(True)
        self.apply_styles()
        
        # Efekt cienia
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.main_panel.setGraphicsEffect(shadow)
        
        # Układ panelu głównego
        panel_layout = QVBoxLayout(self.main_panel)
        
        # Etykieta z oryginalnym tekstem
        self.original_label = QLabel()
        self.original_label.setWordWrap(True)
        self.original_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.original_label.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        panel_layout.addWidget(self.original_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        panel_layout.addWidget(separator)
        
        # Etykieta z tłumaczeniem
        self.translation_label = QLabel()
        self.translation_label.setWordWrap(True)
        self.translation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.translation_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        panel_layout.addWidget(self.translation_label)
        
        # Układ przycisków
        button_layout = QHBoxLayout()
        
        # Przycisk kopiowania
        self.copy_button = QPushButton("Kopiuj")
        self.copy_button.setToolTip("Kopiuj tłumaczenie do schowka")
        self.copy_button.clicked.connect(self.copy_translation)
        button_layout.addWidget(self.copy_button)
        
        # Przycisk zamknięcia
        self.close_button = QPushButton("Zamknij")
        self.close_button.setToolTip("Zamknij okno tłumaczenia")
        self.close_button.clicked.connect(self.close_popup)
        button_layout.addWidget(self.close_button)
        
        panel_layout.addLayout(button_layout)
        
        main_layout.addWidget(self.main_panel)
        self.setLayout(main_layout)
        
        # Konfiguracja auto-ukrywania
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.timeout.connect(self.close_popup)
    
    def apply_styles(self):
        """Zastosowanie stylów na podstawie ustawień."""
        # Kolor tła
        bg_color = self.settings.get('popup', 'bg_color')
        text_color = self.settings.get('popup', 'text_color')
        opacity = self.settings.get('popup', 'opacity') / 100.0
        
        # Ustawienie koloru tła z przezroczystością
        bg_qcolor = QColor(bg_color)
        bg_qcolor.setAlphaF(opacity)
        
        palette = self.main_panel.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_qcolor)
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
        self.main_panel.setPalette(palette)
        
        # Style CSS dla etykiet i przycisków
        style_sheet = f"""
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: 3px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {text_color};
                color: {bg_color};
            }}
        """
        self.setStyleSheet(style_sheet)
    
    def show_translation(self, original_text, translated_text):
        """Wyświetla tłumaczenie w pop-upie."""
        self.original_text = original_text
        self.translated_text = translated_text
        
        # Sprawdzenie, czy pokazywać oryginalny tekst
        show_original = self.settings.get('popup', 'show_original')
        if show_original:
            self.original_label.setText(f"<i>{original_text}</i>")
            self.original_label.show()
        else:
            self.original_label.hide()
        
        # Ustawienie tekstu tłumaczenia
        self.translation_label.setText(translated_text)
        
        # Pozycjonowanie pop-upu
        self.position_popup()
        
        # Wyświetlenie pop-upu
        self.show()
        self.activateWindow()
        
        # Konfiguracja automatycznego ukrywania
        if self.settings.get('popup', 'auto_hide'):
            display_time = self.settings.get('popup', 'display_time') * 1000  # ms
            self.auto_hide_timer.start(display_time)
        
        logger.info("Wyświetlono popup z tłumaczeniem")
    
    def position_popup(self):
        """Pozycjonuje pop-up zgodnie z ustawieniami."""
        position = self.settings.get('popup', 'position')
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        x, y = 0, 0
        
        if position == 'top-right':
            x = screen_geometry.width() - self.width() - 20
            y = 20
        elif position == 'top-left':
            x = 20
            y = 20
        elif position == 'bottom-right':
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20
        elif position == 'bottom-left':
            x = 20
            y = screen_geometry.height() - self.height() - 20
        elif position == 'center':
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
        
        self.move(x, y)
    
    def copy_translation(self):
        """Kopiuje tłumaczenie do schowka."""
        pyperclip.copy(self.translated_text)
        
        # Zmiana tekstu przycisku kopiowania na potwierdzenie
        self.copy_button.setText("Skopiowano!")
        QTimer.singleShot(1500, lambda: self.copy_button.setText("Kopiuj"))
        
        logger.info("Tłumaczenie skopiowane do schowka")
    
    def close_popup(self):
        """Zamyka pop-up."""
        if self.auto_hide_timer and self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()
        
        self.hide()
        self.closed.emit()
        
        logger.info("Zamknięto popup z tłumaczeniem")
    
    def mousePressEvent(self, event):
        """Obsługa naciśnięcia przycisku myszy."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.pos()
            
            # Zatrzymanie timera auto-ukrywania podczas przeciągania
            if self.auto_hide_timer and self.auto_hide_timer.isActive():
                self.auto_hide_timer.stop()
    
    def mouseMoveEvent(self, event):
        """Obsługa ruchu myszy."""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """Obsługa zwolnienia przycisku myszy."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            
            # Ponowne uruchomienie timera auto-ukrywania po przeciągnięciu
            if self.settings.get('popup', 'auto_hide'):
                display_time = self.settings.get('popup', 'display_time') * 1000  # ms
                self.auto_hide_timer.start(display_time)