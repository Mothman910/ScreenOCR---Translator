# ScreenOCR & Translator

Narzędzie do rozpoznawania i tłumaczenia tekstu z ekranu w grach i innych aplikacjach.

## Opis

ScreenOCR & Translator to aplikacja umożliwiająca szybkie przechwytywanie tekstu z ekranu, jego rozpoznanie przez mechanizm OCR i tłumaczenie na wybrany język. Jest szczególnie przydatna dla graczy chcących tłumaczyć dialogi w grach, które nie posiadają oficjalnego tłumaczenia na język polski.

## Funkcje

- Przechwytywanie wybranego obszaru ekranu za pomocą skrótów klawiszowych
- Rozpoznawanie tekstu z wykorzystaniem silnika Tesseract OCR
- Tłumaczenie tekstu za pomocą różnych silników (Google Translate, DeepL)
- Wyświetlanie przetłumaczonego tekstu w okienku popup
- Konfigurowalny interfejs i ustawienia
- Działanie w tle z ikoną w zasobniku systemowym

## Wymagania

- Python 3.8 lub nowszy
- Biblioteki wymienione w pliku `requirements.txt`
- Tesseract OCR (dostępny w folderze `external/Tesseract-OCR/`)

## Instalacja

1. Sklonuj repozytorium:

   ```
   git clone https://github.com/username/ScreenOCR-Translator.git
   cd ScreenOCR-Translator
   ```

2. Zainstaluj wymagane biblioteki:

   ```
   pip install -r requirements.txt
   ```

3. Uruchom aplikację:
   ```
   python src/main.py
   ```

## Budowanie aplikacji

Aby zbudować samodzielną aplikację:

1. Zainstaluj PyInstaller:

   ```
   pip install pyinstaller
   ```

2. Uruchom skrypt budowania:
   ```
   cd build_scripts
   pyinstaller ScreenOCR_Translator.spec
   ```

## Struktura projektu

- `src/` - Kod źródłowy aplikacji
- `resources/` - Ikony, tłumaczenia i style
- `external/` - Zewnętrzne zależności (Tesseract OCR)
- `tests/` - Testy jednostkowe
- `docs/` - Dokumentacja
- `logs/` - Pliki logów
- `build_scripts/` - Skrypty do budowania aplikacji

## Licencja

Ten projekt jest rozpowszechniany na licencji MIT. Zobacz plik `LICENSE` po szczegóły.

## Autor

Adam Fijałkowski
