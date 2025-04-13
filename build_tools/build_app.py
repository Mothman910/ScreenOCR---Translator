"""
Skrypt do budowania aplikacji ScreenOCR & Translator jako plik .exe
za pomocą PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Ścieżki projektowe
PROJECT_ROOT = Path.cwd().parent
SRC_DIR = PROJECT_ROOT / 'src'
BUILD_DIR = PROJECT_ROOT / 'build'
DIST_DIR = PROJECT_ROOT / 'dist'
RESOURCES_DIR = PROJECT_ROOT / 'resources'
ICON_PATH = PROJECT_ROOT / 'icon.ico'

def run_command(command):
    """Uruchamia komendę i wyświetla jej wyjście"""
    print(f"Uruchamianie: {command}")
    process = subprocess.Popen(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        shell=True, 
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    if process.returncode != 0:
        print(f"Komenda zakończyła się kodem {process.returncode}")
        return False
    return True

def cleanup_build_dirs():
    """Czyści katalogi budowania"""
    print("Czyszczenie katalogów budowania...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"Usunięto {directory}")

def build_executable():
    """Buduje aplikację jako pojedynczy plik .exe"""
    print("\n=== Budowanie aplikacji ScreenOCR & Translator ===\n")
    
    # Sprawdzenie, czy znajdujemy się w katalogu build_tools
    if not (Path.cwd().name == 'build_tools' and (Path.cwd().parent / 'src').exists()):
        print("Błąd: Ten skrypt powinien być uruchamiany z katalogu build_tools!")
        return False
    
    # Czyszczenie
    cleanup_build_dirs()
    
    # Sprawdzenie czy mamy wszystkie wymagane zasoby
    tesseract_dir = PROJECT_ROOT / 'external' / 'Tesseract-OCR'
    if not tesseract_dir.exists() or not (tesseract_dir / 'tesseract.exe').exists():
        print(f"OSTRZEŻENIE: Nie znaleziono Tesseract OCR w {tesseract_dir}")
        print("Aplikacja może działać nieprawidłowo bez Tesseract OCR.")
    
    if not ICON_PATH.exists():
        print(f"OSTRZEŻENIE: Nie znaleziono pliku ikony {ICON_PATH}")
    
    # Budowanie za pomocą PyInstaller
    pyinstaller_command = [
        'pyinstaller',
        '--onefile',  # Pojedynczy plik .exe
        '--windowed',  # Aplikacja okienkowa (bez konsoli)
        f'--icon={ICON_PATH}' if ICON_PATH.exists() else '',
        '--name=ScreenOCR_Translator',
        '--clean',
        '--noconfirm',
        '--add-data', f"{RESOURCES_DIR};resources",
        # Dodanie Tesseract OCR do pliku wykonalnego
        '--add-data', f"{tesseract_dir};external/Tesseract-OCR" if tesseract_dir.exists() else "",
        # Dodatkowe opcje DLL
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=pynput',
        '--hidden-import=pytesseract',
        str(SRC_DIR / 'main.py')
    ]
    
    # Filtrowanie pustych argumentów
    pyinstaller_command = [arg for arg in pyinstaller_command if arg]
    
    success = run_command(' '.join(pyinstaller_command))
    if not success:
        print("Błąd podczas budowania aplikacji!")
        return False
    
    print("\nAplikacja została zbudowana pomyślnie!")
    exe_path = DIST_DIR / 'ScreenOCR_Translator.exe'
    print(f"Plik wykonywalny znajduje się w: {exe_path}")
    
    return True

def create_installer():
    """Tworzy instalator za pomocą Inno Setup"""
    print("\n=== Tworzenie instalatora ===\n")
    
    # Sprawdzenie, czy Inno Setup jest zainstalowany
    inno_compiler_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not Path(inno_compiler_path).exists():
        print("Błąd: Nie znaleziono Inno Setup! Zainstaluj Inno Setup 6 i spróbuj ponownie.")
        return False
    
    # Uruchomienie kompilatora Inno Setup
    inno_command = f'"{inno_compiler_path}" installer.iss'
    
    success = run_command(inno_command)
    if not success:
        print("Błąd podczas tworzenia instalatora!")
        return False
    
    installer_path = DIST_DIR / 'Setup_ScreenOCR_Translator.exe'
    print(f"\nInstalator został utworzony pomyślnie!")
    print(f"Plik instalatora znajduje się w: {installer_path}")
    
    return True

if __name__ == "__main__":
    if build_executable():
        create_installer()