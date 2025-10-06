import os
from decoding import decode_csv_file
from browse import scan_csv_files, display_csv_files
from create2db import create_database
from cleaning import clean_file  # A JAVÍTOTT clean_file függvényt importáljuk


def process_csv_files(folder_path: str, output_folder_name: str, process_type: str = 'decode') -> None:
    """
    CSV fájlok feldolgozása
    """

    # 1. Mappa szkennelése
    csv_files = scan_csv_files(folder_path)
    file_count = len(csv_files)

    if file_count == 0:
        print(f"ℹ️  Nincs CSV fájl a mappában: {folder_path}")
        return

    # 2. Fájlok megjelenítése
    display_csv_files(csv_files, folder_path)

    # 3. Kimeneti mappa beállítása
    output_dir = os.path.join(os.path.dirname(folder_path), output_folder_name)

    # 4. Feldolgozás indítása
    process_name = "DEKÓDOLÁS" if process_type == 'decode' else "TISZTÍTÁS"
    print(f"\n🔄 {file_count} CSV fájl {process_name.lower()}a...")

    successful_files = []

    for csv_file in csv_files:
        input_file_path = os.path.join(folder_path, csv_file)

        print(f"\n{'─' * 40}")
        print(f"📄 {csv_file}")
        print(f"{'─' * 40}")

        if process_type == 'decode':
            result = decode_csv_file(input_file_path, output_dir)
        else:  # clean
            result = clean_file(input_file_path, output_dir)

        if result:
            successful_files.append(csv_file)
            print(f"✅ SIKERES")
        else:
            print(f"❌ SIKERTELEN")

    # 5. Eredmény jelentés
    print(f"\n{'=' * 50}")
    print(f"🎉 {process_name} KÉSZ: {len(successful_files)}/{file_count} fájl")
    print(f"{'=' * 50}")


def main():
    """
    Főprogram - Teljes adatfeldolgozási folyamat
    """

    print("=" * 60)
    print("🚀 TELJES ADATFELDOLGOZÁSI FOLYAMAT")
    print("=" * 60)

    # Projekt útvonalak
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    # 1. LÉPÉS: Adatbázis létrehozás
    print("\n1. 📊 ADATBÁZIS LÉTREHOZÁS")
    print("-" * 30)

    db_success = create_database()

    if not db_success:
        print("❌ Adatbázis létrehozása sikertelen, folyamat leállítva!")
        return

    print("✅ Adatbázis sikeresen létrehozva!")

    # 2. LÉPÉS: Import mappa dekódolása → temp mappa
    print("\n2. 📁 IMPORT MAPPA DEKÓDOLÁSA")
    print("-" * 30)

    import_folder = os.path.join(root_dir, 'import')
    print(f"🔍 Forrás: {import_folder}")
    print(f"🎯 Cél: temp mappa")

    process_csv_files(import_folder, 'temp', 'decode')

    # 3. LÉPÉS: Temp mappa tisztítása → export mappa
    print("\n3. 🧹 TEMP MAPPA TISZTÍTÁSA")
    print("-" * 30)

    temp_folder = os.path.join(root_dir, 'temp')
    print(f"🔍 Forrás: {temp_folder}")
    print(f"🎯 Cél: export mappa")

    process_csv_files(temp_folder, 'export', 'clean')

    # 4. LÉPÉS: Végleges eredmény
    print("\n" + "=" * 60)
    print("🎉 MINDEN FOLYAMAT SIKERESEN BEFEJEZVE!")
    print("=" * 60)

    export_folder = os.path.join(root_dir, 'export')
    final_files = scan_csv_files(export_folder)

    if final_files:
        print(f"\n📊 VÉGEREDMÉNY: {len(final_files)} fájl az export mappában:")
        for file in final_files:
            file_path = os.path.join(export_folder, file)
            file_size = os.path.getsize(file_path) / 1024
            print(f"   📄 {file} ({file_size:.1f} KB)")
    else:
        print("\n📊 VÉGEREDMÉNY: Nincs fájl az export mappában")


if __name__ == "__main__":
    main()
