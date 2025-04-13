#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do przetwarzania obrazów przed rozpoznawaniem tekstu.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger('image_processing')

class ImageProcessor:
    """Klasa odpowiedzialna za przetwarzanie obrazów przed OCR."""
    
    def __init__(self, settings):
        self.settings = settings
        logger.info("Procesor obrazów zainicjowany")
    
    def preprocess(self, image):
        """Przetwarza obraz w celu optymalizacji dla OCR."""
        try:
            # Konwersja do skali szarości, jeśli obraz jest kolorowy
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Usunięcie szumu
            denoised = self._denoise(gray)
            
            # Binaryzacja obrazu
            binary = self._binarize(denoised)
            
            # Usunięcie zniekształceń i ewentualne skalowanie
            processed = self._deskew(binary)
            
            return processed
            
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania obrazu: {e}")
            return image
    
    def _denoise(self, image):
        """Usuwa szum z obrazu."""
        try:
            # Zastosowanie algorytmu redukcji szumu Non-Local Means Denoising
            denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
            return denoised
        except Exception as e:
            logger.error(f"Błąd podczas usuwania szumu: {e}")
            return image
    
    def _binarize(self, image):
        """Binaryzuje obraz dla lepszego rozpoznawania tekstu."""
        try:
            # Binaryzacja adaptacyjna
            # Dostosowuje próg na podstawie lokalnego obszaru wokół każdego piksela
            binary = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Alternatywnie, można użyć metody Otsu dla globalnej binaryzacji
            # _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
        except Exception as e:
            logger.error(f"Błąd podczas binaryzacji: {e}")
            return image
    
    def _deskew(self, image):
        """Koryguje pochylenie tekstu."""
        try:
            # Wykrycie linii tekstu za pomocą transformacji Hough'a
            lines = cv2.HoughLinesP(
                255 - image, 1, np.pi / 180, 100, 
                minLineLength=100, maxLineGap=50
            )
            
            if lines is None or len(lines) == 0:
                # Jeśli nie wykryto linii, zwróć oryginalny obraz
                return image
            
            # Obliczenie kąta pochylenia
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 != x1:  # Unikaj dzielenia przez zero
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    # Uwzględnij tylko kąty bliskie poziomym liniom
                    if abs(angle) < 30:
                        angles.append(angle)
            
            if not angles:
                return image
            
            # Średni kąt pochylenia
            median_angle = np.median(angles)
            
            # Korekcja pochylenia
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h), 
                flags=cv2.INTER_CUBIC, 
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return rotated
            
        except Exception as e:
            logger.error(f"Błąd podczas korekcji pochylenia: {e}")
            return image
    
    def enhance_game_screenshot(self, image):
        """Specjalne przetwarzanie dla zrzutów ekranu z gier."""
        try:
            # Konwersja do skali szarości
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Zwiększenie kontrastu
            # Zastosowanie CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Wyostrzenie obrazu
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # Usunięcie szumu
            denoised = cv2.fastNlMeansDenoising(sharpened, None, 10, 7, 21)
            
            # Zastosowanie adaptacyjnej binaryzacji z inną konfiguracją dla tekstur gier
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 15, 5
            )
            
            # Operacje morfologiczne do usunięcia małych artefaktów i wzmocnienia tekstu
            kernel = np.ones((1, 1), np.uint8)
            morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return morph
            
        except Exception as e:
            logger.error(f"Błąd podczas wzmacniania zrzutu z gry: {e}")
            return image
    
    def resize_for_better_ocr(self, image, scale_factor=1.5):
        """Zmienia rozmiar obrazu dla lepszego rozpoznawania tekstu."""
        try:
            # Zwiększenie rozmiaru obrazu dla lepszego OCR małego tekstu
            resized = cv2.resize(
                image, None, 
                fx=scale_factor, fy=scale_factor, 
                interpolation=cv2.INTER_CUBIC
            )
            return resized
            
        except Exception as e:
            logger.error(f"Błąd podczas zmiany rozmiaru: {e}")
            return image