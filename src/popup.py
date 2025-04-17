#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł odpowiedzialny za wyświetlanie pop-upu z tłumaczeniem.
"""

import logging
import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, 
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
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
        self.resize_mode = False
        
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
        self.setMinimumSize(300, 200)
        self.resize(width, height)
        
        # Główny układ
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
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
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(5)
        
        # Obszar przewijania dla oryginalnego tekstu
        self.original_scroll = QScrollArea()
        self.original_scroll.setWidgetResizable(True)
        self.original_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.original_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.original_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Kontener dla oryginalnego tekstu
        self.original_container = QWidget()
        self.original_container_layout = QVBoxLayout(self.original_container)
        self.original_container_layout.setContentsMargins(5, 5, 15, 5)  # Dodany dodatkowy prawy margines dla paska przewijania
        
        # Etykieta z oryginalnym tekstem
        self.original_label = QLabel()
        self.original_label.setWordWrap(True)
        self.original_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.original_label.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        self.original_container_layout.addWidget(self.original_label)
        
        self.original_scroll.setWidget(self.original_container)
        panel_layout.addWidget(self.original_scroll)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        panel_layout.addWidget(separator)
        
        # Obszar przewijania dla tłumaczenia
        self.translation_scroll = QScrollArea()
        self.translation_scroll.setWidgetResizable(True)
        self.translation_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.translation_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.translation_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Kontener dla tłumaczenia
        self.translation_container = QWidget()
        self.translation_container_layout = QVBoxLayout(self.translation_container)
        self.translation_container_layout.setContentsMargins(5, 5, 15, 5)  # Dodany dodatkowy prawy margines dla paska przewijania
        
        # Etykieta z tłumaczeniem
        self.translation_label = QLabel()
        self.translation_label.setWordWrap(True)
        self.translation_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.translation_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.translation_container_layout.addWidget(self.translation_label)
        
        self.translation_scroll.setWidget(self.translation_container)
        panel_layout.addWidget(self.translation_scroll, 1)  # Dajemy większy współczynnik rozciągania
        
        # Panel przycisków w oddzielnym widgecie, aby zawsze był widoczny
        self.button_panel = QWidget()
        button_layout = QHBoxLayout(self.button_panel)
        button_layout.setContentsMargins(0, 5, 0, 0)
        
        # Przycisk kopiowania
        self.copy_button = QPushButton("Kopiuj")
        self.copy_button.setToolTip("Kopiuj tłumaczenie do schowka")
        self.copy_button.clicked.connect(self.copy_translation)
        self.copy_button.setMinimumHeight(30)
        button_layout.addWidget(self.copy_button)
        
        # Przycisk zamknięcia
        self.close_button = QPushButton("Zamknij")
        self.close_button.setToolTip("Zamknij okno tłumaczenia")
        self.close_button.clicked.connect(self.close_popup)
        self.close_button.setMinimumHeight(30)
        button_layout.addWidget(self.close_button)
        
        panel_layout.addWidget(self.button_panel)
        
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
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.1);
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba({text_color}, 0.5);
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: rgba(0, 0, 0, 0.1);
                height: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba({text_color}, 0.5);
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        self.setStyleSheet(style_sheet)
    
    def show_translation(self, original_text, translated_text):
        """Wyświetla tłumaczenie w pop-upie."""
        self.original_text = original_text
        self.translated_text = translated_text
        
        # Sprawdzenie, czy pokazywać oryginalny tekst
        show_original = self.settings.get('popup', 'show_original')
        if show_original and original_text.strip():
            self.original_label.setText(f"<i>{original_text}</i>")
            self.original_scroll.setMaximumHeight(int(self.height() * 0.3))
            self.original_scroll.show()
        else:
            self.original_scroll.hide()
            separator = self.main_panel.findChild(QFrame)
            if separator:
                separator.hide()
        
        # Ustawienie tekstu tłumaczenia
        self.translation_label.setText(translated_text)
        
        # Dostosowanie rozmiaru głównego kontenera
        self.translation_container.adjustSize()
        self.original_container.adjustSize()
        
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
    
    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru okna."""
        super().resizeEvent(event)
        
        # Zapisanie nowych wymiarów w ustawieniach
        self.settings.set('popup', 'width', self.width())
        self.settings.set('popup', 'height', self.height())
        
        # Dostosowanie obszarów przewijania
        if self.settings.get('popup', 'show_original'):
            self.original_scroll.setMaximumHeight(int(self.height() * 0.3))
    
    def mousePressEvent(self, event):
        """Obsługa naciśnięcia przycisku myszy."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Sprawdzenie, czy kliknięcie nastąpiło w przycisk
            if self.close_button.geometry().contains(event.position().toPoint() - self.button_panel.pos()) or \
               self.copy_button.geometry().contains(event.position().toPoint() - self.button_panel.pos()):
                # Przekazanie zdarzenia do przetworzenia przez normalny mechanizm
                return
            
            self.dragging = True
            self.drag_position = event.pos()
            
            # Zatrzymanie timera auto-ukrywania podczas przeciągania
            if self.auto_hide_timer and self.auto_hide_timer.isActive():
                self.auto_hide_timer.stop()
    
    def mouseMoveEvent(self, event):
        """Obsługa ruchu myszy."""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Tylko przeciąganie, bez zmiany rozmiaru
            self.move(self.pos() + event.pos() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """Obsługa zwolnienia przycisku myszy."""
        if event.button() == Qt.MouseButton.LeftButton:
            was_dragging = self.dragging
            self.dragging = False
            
            # Ponowne uruchomienie timera auto-ukrywania po przeciągnięciu
            if was_dragging and self.settings.get('popup', 'auto_hide'):
                display_time = self.settings.get('popup', 'display_time') * 1000  # ms
                self.auto_hide_timer.start(display_time)
    
    def mouseDoubleClickEvent(self, event):
        """Obsługa podwójnego kliknięcia myszy."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Implementacja możliwości maksymalizacji/przywracania poprzedniego rozmiaru
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()