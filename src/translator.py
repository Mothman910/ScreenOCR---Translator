#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do tłumaczenia tekstu.
"""

import os
import logging
import requests
import json
import time
import hashlib
from typing import Dict, Tuple, Optional

logger = logging.getLogger('translator')

class TranslationCache:
    """Klasa do przechowywania cache'u tłumaczeń."""
    
    def __init__(self, max_size: int = 100):
        """Inicjalizacja cache'u tłumaczeń.
        
        Args:
            max_size: Maksymalna liczba przechowywanych tłumaczeń
        """
        self.cache: Dict[str, Tuple[str, float]] = {}  # hash -> (tłumaczenie, timestamp)
        self.max_size = max_size
    
    def get_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generuje klucz cache'a dla danego tekstu i języków.
        
        Args:
            text: Tekst do tłumaczenia
            source_lang: Język źródłowy
            target_lang: Język docelowy
            
        Returns:
            Klucz hash dla cache'a
        """
        # Tworzenie unikalnego klucza na podstawie tekstu i języków
        cache_data = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Pobiera tłumaczenie z cache'u jeśli istnieje.
        
        Args:
            text: Tekst do tłumaczenia
            source_lang: Język źródłowy
            target_lang: Język docelowy
            
        Returns:
            Przetłumaczony tekst lub None jeśli nie ma w cache'u
        """
        key = self.get_key(text, source_lang, target_lang)
        if key in self.cache:
            translation, _ = self.cache[key]
            logger.info(f"Znaleziono tłumaczenie w cache'u: {text[:20]}...")
            return translation
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str) -> None:
        """Zapisuje tłumaczenie do cache'u.
        
        Args:
            text: Oryginalny tekst
            source_lang: Język źródłowy
            target_lang: Język docelowy
            translation: Przetłumaczony tekst
        """
        # Jeśli cache jest pełny, usuń najstarszy wpis
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            
        key = self.get_key(text, source_lang, target_lang)
        self.cache[key] = (translation, time.time())
        logger.debug(f"Dodano tłumaczenie do cache'u: {text[:20]}...")

class Translator:
    """Klasa odpowiedzialna za tłumaczenie tekstu."""
    
    def __init__(self, settings):
        """Inicjalizacja tłumacza."""
        self.settings = settings
        self.cache = TranslationCache(
            max_size=int(self.settings.get('translation', 'cache_size', '100'))
        )
        logger.info("Translator zainicjowany")
    
    def translate(self, text):
        """Tłumaczy tekst z języka źródłowego na docelowy."""
        if not text:
            return ""
            
        try:
            engine = self.settings.get('translation', 'engine')
            source_lang = self.settings.get('translation', 'source_lang')
            target_lang = self.settings.get('translation', 'target_lang')
            
            # Sprawdzenie czy tłumaczenie jest w cache'u
            cached_translation = self.cache.get(text, source_lang, target_lang)
            if cached_translation:
                return cached_translation
            
            logger.info(f"Tłumaczenie tekstu silnikiem {engine} z {source_lang} na {target_lang}")
            
            # Wykonanie tłumaczenia
            translation = self._translate_with_engine(engine, text, source_lang, target_lang)
            
            # Zapisanie tłumaczenia do cache'u (jeśli nie jest to komunikat o błędzie)
            if not translation.startswith("[Błąd tłumaczenia]"):
                self.cache.set(text, source_lang, target_lang, translation)
                
            return translation
                
        except Exception as e:
            logger.error(f"Błąd podczas tłumaczenia: {e}")
            return self._fallback_translation(text)
    
    def _translate_with_engine(self, engine, text, source_lang, target_lang):
        """Wybiera odpowiedni silnik tłumaczenia.
        
        Args:
            engine: Nazwa silnika tłumaczenia
            text: Tekst do tłumaczenia
            source_lang: Język źródłowy
            target_lang: Język docelowy
            
        Returns:
            Przetłumaczony tekst
        """
        if engine == 'google':
            return self._translate_with_google(text, source_lang, target_lang)
        elif engine == 'deepl':
            return self._translate_with_deepl(text, source_lang, target_lang)
        else:
            logger.error(f"Nieznany silnik tłumaczenia: {engine}")
            return self._fallback_translation(text)
    
    def _make_api_request(self, method, url, **kwargs):
        """Wykonuje zapytanie do API z obsługą błędów.
        
        Args:
            method: Metoda HTTP ('get' lub 'post')
            url: URL API
            **kwargs: Parametry zapytania
            
        Returns:
            Odpowiedź API lub None w przypadku błędu
        """
        try:
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, **kwargs)
            else:
                logger.error(f"Nieznana metoda HTTP: {method}")
                return None
                
            if response.status_code == 200:
                return response
            else:
                logger.error(f"Błąd API: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Błąd podczas wykonywania zapytania: {e}")
            return None
    
    def _translate_with_google(self, text, source_lang, target_lang):
        """Tłumaczy tekst za pomocą Google Translate API."""
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        response = self._make_api_request('get', url, params=params)
        if response:
            try:
                result = response.json()
                translated_text = ''.join([sentence[0] for sentence in result[0] if sentence[0]])
                return translated_text
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania odpowiedzi Google: {e}")
        
        return self._fallback_translation(text)
    
    def _translate_with_deepl(self, text, source_lang, target_lang):
        """Tłumaczy tekst za pomocą DeepL API."""
        # DeepL wymaga klucza API, który powinien być podany w ustawieniach
        api_key = self.settings.get('translation', 'deepl_api_key', '')
        if not api_key:
            logger.warning("Brak klucza API DeepL. Przełączanie na Google Translate.")
            return self._translate_with_google(text, source_lang, target_lang)
        
        url = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Authorization": f"DeepL-Auth-Key {api_key}"
        }
        data = {
            "text": [text],
            "source_lang": source_lang.upper(),
            "target_lang": target_lang.upper()
        }
        
        response = self._make_api_request('post', url, headers=headers, data=data)
        if response:
            try:
                result = response.json()
                return result['translations'][0]['text']
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania odpowiedzi DeepL: {e}")
                # Próba użycia Google jako fallback
                return self._translate_with_google(text, source_lang, target_lang)
        
        # Jeśli DeepL zawiedzie, spróbuj z Google
        return self._translate_with_google(text, source_lang, target_lang)
    
    def _fallback_translation(self, text):
        """Tłumaczenie awaryjne gdy API zawiedzie."""
        # W przypadku błędu zwracamy oryginalny tekst z informacją o błędzie
        return f"[Błąd tłumaczenia] {text}"