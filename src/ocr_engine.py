#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do rozpoznawania tekstu z obrazów.
"""

import os
import cv2
import numpy as np
import pytesseract
import logging
from pathlib import Path

logger = logging.getLogger('ocr_engine')

class OCREngine:
    """Silnik OCR wykorzystujący Tesseract do rozpoznawania tekstu z obrazów."""
    
    def __init__(self, settings):
        """Inicjalizacja silnika OCR."""
        self.settings = settings
        
        # Konfiguracja Tesseract
        self.configure_tesseract()
        
        logger.info("Silnik OCR zainicjowany")
    
    def configure_tesseract(self):
        """Konfiguruje Tesseract OCR."""
        # Sprawdzenie, czy ustawiona jest ścieżka do Tesseract
        tesseract_path = self.settings.get('paths', 'tesseract')
        
        # Jeśli ścieżka jest pusta lub nieprawidłowa, spróbuj znaleźć Tesseract w projekcie
        if not tesseract_path or not os.path.exists(tesseract_path):
            # Ścieżka względna do Tesseract w folderze projektu
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tesseract_project_path = os.path.join(project_root, 'external', 'Tesseract-OCR', 'tesseract.exe')
            
            if os.path.exists(tesseract_project_path):
                tesseract_path = tesseract_project_path
                # Zapisz wykrytą ścieżkę w ustawieniach
                self.settings.set('paths', 'tesseract', tesseract_path)
                logger.info(f"Znaleziono Tesseract w folderze projektu: {tesseract_path}")
        
        # Konfiguracja ścieżki do Tesseract
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"Ustawiono Tesseract OCR: {tesseract_path}")
        else:
            logger.warning("Nie znaleziono Tesseract OCR. OCR może nie działać prawidłowo.")
        
        # Sprawdzenie, czy ustawiona jest ścieżka do danych tessdata
        tessdata_path = self.settings.get('paths', 'tessdata')
        
        # Jeśli ścieżka jest pusta lub nieprawidłowa, spróbuj znaleźć tessdata w projekcie
        if not tessdata_path or not os.path.exists(tessdata_path):
            # Ścieżka względna do tessdata w folderze projektu
            tessdata_project_path = os.path.join(project_root, 'external', 'Tesseract-OCR', 'tessdata')
            
            if os.path.exists(tessdata_project_path):
                tessdata_path = tessdata_project_path
                # Zapisz wykrytą ścieżkę w ustawieniach
                self.settings.set('paths', 'tessdata', tessdata_path)
                logger.info(f"Znaleziono tessdata w folderze projektu: {tessdata_path}")
        
        # Konfiguracja ścieżki do tessdata
        if tessdata_path and os.path.exists(tessdata_path):
            os.environ['TESSDATA_PREFIX'] = tessdata_path
            logger.info(f"Ustawiono TESSDATA_PREFIX: {tessdata_path}")
    
    def process_image(self, image_path):
        """Przetwarza obraz i rozpoznaje tekst."""
        try:
            logger.info(f"Przetwarzanie obrazu: {image_path}")
            
            # Wczytanie obrazu
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Nie można wczytać obrazu: {image_path}")
            
            # Przetwarzanie obrazu przed OCR, jeśli jest włączone
            if self.settings.get('ocr', 'preprocess'):
                image = self.preprocess_image(image)
            
            # Rozpoznawanie tekstu
            ocr_language = self.settings.get('ocr', 'language')
            config = f'--psm 6 --oem 3 -l {ocr_language}'
            
            text = pytesseract.image_to_string(image, config=config)
            text = self.postprocess_text(text)
            
            logger.info("Rozpoznawanie tekstu zakończone")
            return text
            
        except Exception as e:
            logger.error(f"Błąd podczas rozpoznawania tekstu: {e}")
            return ""
    
    def preprocess_image(self, image):
        """Przetwarza obraz przed OCR dla zwiększenia dokładności."""
        try:
            # Konwersja do skali szarości
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Usuwanie szumu
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Binaryzacja adaptacyjna
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Opcjonalne powiększenie obrazu dla lepszego rozpoznawania małego tekstu
            resized = cv2.resize(binary, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            
            return resized
            
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania obrazu: {e}")
            return image  # Zwrócenie oryginalnego obrazu w przypadku błędu
    
    def postprocess_text(self, text):
        """Przetwarza rozpoznany tekst."""
        if not text:
            return ""
        
        # Usuwanie nadmiarowych białych znaków
        text = ' '.join(text.split())
        
        # Usuwanie ewentualnych niepotrzebnych znaków
        text = text.strip()
        
        return text