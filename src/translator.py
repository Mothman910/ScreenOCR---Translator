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

logger = logging.getLogger('translator')

class Translator:
    """Klasa odpowiedzialna za tłumaczenie tekstu."""
    
    def __init__(self, settings):
        """Inicjalizacja tłumacza."""
        self.settings = settings
        logger.info("Translator zainicjowany")
    
    def translate(self, text):
        """Tłumaczy tekst z języka źródłowego na docelowy."""
        if not text:
            return ""
            
        try:
            engine = self.settings.get('translation', 'engine')
            source_lang = self.settings.get('translation', 'source_lang')
            target_lang = self.settings.get('translation', 'target_lang')
            
            logger.info(f"Tłumaczenie tekstu silnikiem {engine} z {source_lang} na {target_lang}")
            
            if engine == 'google':
                return self._translate_with_google(text, source_lang, target_lang)
            elif engine == 'deepl':
                return self._translate_with_deepl(text, source_lang, target_lang)
            else:
                logger.error(f"Nieznany silnik tłumaczenia: {engine}")
                return self._fallback_translation(text)
                
        except Exception as e:
            logger.error(f"Błąd podczas tłumaczenia: {e}")
            return self._fallback_translation(text)
    
    def _translate_with_google(self, text, source_lang, target_lang):
        """Tłumaczy tekst za pomocą Google Translate API."""
        try:
            # Ze względu na ograniczenia API, używamy nieoficjalnego API
            # Docelowo można zastąpić to oficjalnym API Google Translate
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": source_lang,
                "tl": target_lang,
                "dt": "t",
                "q": text
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                # Parsowanie odpowiedzi
                result = response.json()
                translated_text = ''.join([sentence[0] for sentence in result[0] if sentence[0]])
                return translated_text
            else:
                logger.error(f"Błąd API Google Translate: {response.status_code}")
                return self._fallback_translation(text)
                
        except Exception as e:
            logger.error(f"Błąd podczas tłumaczenia Google: {e}")
            return self._fallback_translation(text)
    
    def _translate_with_deepl(self, text, source_lang, target_lang):
        """Tłumaczy tekst za pomocą DeepL API."""
        try:
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
            
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                result = response.json()
                return result['translations'][0]['text']
            else:
                logger.error(f"Błąd API DeepL: {response.status_code}")
                return self._translate_with_google(text, source_lang, target_lang)
                
        except Exception as e:
            logger.error(f"Błąd podczas tłumaczenia DeepL: {e}")
            return self._translate_with_google(text, source_lang, target_lang)
    
    def _fallback_translation(self, text):
        """Tłumaczenie awaryjne gdy API zawiedzie."""
        # W przypadku błędu zwracamy oryginalny tekst z informacją o błędzie
        return f"[Błąd tłumaczenia] {text}"