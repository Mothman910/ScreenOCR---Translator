#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy jednostkowe dla silnika OCR.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import cv2
import numpy as np

# Dodanie ścieżki do modułów
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Importy testowanych modułów
from ocr_engine import OCREngine

class TestOCREngine(unittest.TestCase):
    """Testy jednostkowe dla silnika OCR."""
    
    def setUp(self):
        """Przygotowanie przed każdym testem."""
        # Tworzenie mocka obiektu settings
        self.settings_mock = MagicMock()
        self.settings_mock.get.return_value = ''  # Domyślne puste ustawienia
        
        # Tworzenie instancji testowanego silnika OCR
        with patch('pytesseract.pytesseract.tesseract_cmd'):
            self.ocr_engine = OCREngine(self.settings_mock)
    
    def test_create_processing_variants(self):
        """Test tworzenia wariantów przetwarzania obrazu."""
        # Tworzenie testowego obrazu
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255  # Biały obraz
        
        # Wywołanie testowanej metody
        variants = self.ocr_engine.create_processing_variants(test_image)
        
        # Sprawdzenie wyników
        self.assertEqual(len(variants), 6, "Powinno być 6 wariantów przetwarzania obrazu")
        self.assertEqual(variants[0].shape, (100, 100), "Pierwszy wariant powinien być w skali szarości")
    
    def test_select_best_text(self):
        """Test wyboru najlepszego tekstu."""
        # Przykładowe dane wejściowe
        texts_with_confidence = [
            ("Tekst z błędami 123", 70, "variant_1"),
            ("Poprawny tekst", 90, "variant_2"),
            ("Krótki", 95, "variant_3")
        ]
        
        # Wywołanie testowanej metody
        best_text = self.ocr_engine.select_best_text(texts_with_confidence)
        
        # Sprawdzenie wyniku
        self.assertEqual(best_text, "Poprawny tekst", "Powinien zostać wybrany tekst z najlepszym stosunkiem pewności do długości")
    
    def test_empty_text_selection(self):
        """Test wyboru tekstu z pustej listy."""
        # Wywołanie testowanej metody z pustą listą
        best_text = self.ocr_engine.select_best_text([])
        
        # Sprawdzenie wyniku
        self.assertEqual(best_text, "", "Dla pustej listy powinien zostać zwrócony pusty string")

if __name__ == '__main__':
    unittest.main()