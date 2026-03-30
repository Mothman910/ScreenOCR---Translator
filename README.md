# Screen OCR Translator

Desktopowa aplikacja napisana w Pythonie dla systemu Windows. Pozwala na błyskawiczne zaznaczanie obszaru na ekranie w celu rozpoznania tekstu (OCR) i przetłumaczenia go w czasie rzeczywistym. Idealne narzędzie do gier, aplikacji bez natywnego wsparcia językowego oraz zablokowanych treści tekstowych (niemożliwych do skopiowania).

## 🚀 Główne funkcje
- **Globalne skróty klawiszowe** - Szybkie wywoływanie interfejsu zaznaczania obszaru (overlay) działające nad dowolną aplikacją.
- **Zaawansowany OCR** - Wykorzystanie precyzyjnego silnika Tesseract (wspieranego przez OpenCV do preprocessingu obrazu binarnego i odszumiania) zapewnia wysoką skuteczność odczytu.
- **Błyskawiczne Tłumaczenie** - Wbudowana integracja z Google Cloud Translation / DeepL API błyskawicznie konwertuje przejęty angielski tekst na język docelowy.
- **Zgrabne UI** - Wyniki prezentowane są jako estetyczny, konfigurowalny pop-up okienkowy (PyQt6), który można swobodnie przesuwać.
- **Działanie w tle** - Aplikacja funkcjonuje prosto z zasobnika systemowego (System Tray) minimalizując użycie zasobów.

## 🛠️ Stos technologiczny
- **Język główny:** Python 3.11+
- **Interfejs Użytkownika:** PyQt6, infi.systray
- **Przetwarzanie Obrazu i OCR:** Tesseract OCR, Pytesseract, OpenCV-Python, Pillow
- **Silniki Tłumaczeń:** googletrans, DeepL
- **Narzędzia globalne:** pynput, keyboard, pyperclip
- **Pakowanie i release:** PyInstaller, Inno Setup (instalator .exe)

## ⚙️ Wymagania systemowe
- Operacyjny system Windows 11 / Windows 10 (64-bit)
- Silnik Tesseract OCR wgranym lokalnie
- Posiadanie odpowiednich uprawnień do "screenshot record"

## 💡 Jak uruchomić (dla deweloperów)
```bash
# Klonowanie repozytorium
git clone https://github.com/Mothman910/Screen_OCR_translator.git
cd Screen_OCR_translator

# Instalacja niezbędnych pakietów
pip install -r requirements.txt

# Uruchomienie aplikacji w środowisku
python src/main.py
```

## 🗂️ Architektura
Projekt pakowany jest z wykorzystaniem pyinstallera a następnie kompilowany gotowym Inno Setupem do pojedynczego okienka instalacyjnego. Szczegółowe diagramy powiązań i przebieg działania systemu dostępny jest do wglądu w pliku głównym `ARCHITEKTURA.md`.

