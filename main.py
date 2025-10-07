import os
import shutil
import sqlite3
from decoding import decode_csv_file
from browse import scan_csv_files, display_csv_files
from create2db import create_database
from cleaning import clean_file
from normalizer_prepare import normalize_file
from db_loader import load_nf_tables_to_db


def cleanup_folder(folder_path: str, folder_name: str) -> None:
    """
    Mappa tartalmának kiürítése megerősítéssel
    """
    if not os.path.exists(folder_path):
        return

    files = scan_csv_files(folder_path)
    if not files:
        return

    print(f"\n⚠️  {folder_name} mappa már tartalmaz {len(files)} fájlt:")
    for file in files:
        print(f"   📄 {file}")

    response = input(f"\n💥 Kiürítsem a {folder_name} mappát? (i/n): ").strip().lower()
    if response == 'i':
        # Összes CSV fájl törlése
        for file in files:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
        print(f"✅ {folder_name} mappa kiürítve!")
    else:
        print(f"ℹ️  {folder_name} mappa tartalma megmarad.")


def check_existing_tables(db_path: str) -> bool:
    """
    Meglévő táblák ellenőrzése és törlési engedély kérése
    """
    if not os.path.exists(db_path):
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Meglévő táblák lekérdezése
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]

        conn.close()

        if not existing_tables:
            return True

        print(f"\n⚠️  Adatbázis már tartalmaz {len(existing_tables)} táblát:")
        for table in existing_tables:
            print(f"   📊 {table}")

        response = input(f"\n💥 Törlés elutaitása esetén manuálisan kell az érintett táblákat kitörölnöd! \n Töröljem és hozzam létre újra ezeket a táblákat? (i/n): ").strip().lower()
        return response == 'i'

    except Exception as e:
        print(f"❌ Hiba az adatbázis ellenőrzése során: {e}")
        return False


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


def normalize_export_files(export_folder: str) -> int:
    """
    Export mappa NF3 normalizálása
    """
    print("\n🔧 NF3 NORMALIZÁLÁS")
    print("-" * 30)

    csv_files = scan_csv_files(export_folder)
    print(f"📁 Normalizálandó fájlok: {len(csv_files)}")

    total_tables_created = 0

    for csv_file in csv_files:
        input_path = os.path.join(export_folder, csv_file)
        tables_created = normalize_file(input_path, export_folder)
        total_tables_created += tables_created

    print(f"\n✅ NF3 KÉSZ: {total_tables_created} tábla létrehozva")
    return total_tables_created


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

    # 0. LÉPÉS: Előkészületek - mappák kiürítése
    print("\n0. 🧹 ELŐKÉSZÜLETEK")
    print("-" * 30)

    temp_folder = os.path.join(root_dir, 'temp')
    export_folder = os.path.join(root_dir, 'export')
    db_path = os.path.join(root_dir, 'db', 'data.db')

    # Temp mappa kiürítése
    cleanup_folder(temp_folder, "temp")

    # Export mappa kiürítése
    cleanup_folder(export_folder, "export")

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

    print(f"🔍 Forrás: {temp_folder}")
    print(f"🎯 Cél: export mappa")

    process_csv_files(temp_folder, 'export', 'clean')

    # 4. LÉPÉS: Export mappa NF3 normalizálása
    print("\n4. 🔧 EXPORT MAPPA NF3 NORMALIZÁLÁSA")
    print("-" * 30)

    tables_created = normalize_export_files(export_folder)

    if tables_created == 0:
        print("❌ NF3 normalizálás sikertelen, folyamat leállítva!")
        return

    # 5. LÉPÉS: Adatbázis betöltés NF3 táblákkal
    print("\n5. 🗃️  ADATBÁZIS BETÖLTÉS NF3 TÁBLÁKKAL")
    print("-" * 30)

    # Meglévő táblák ellenőrzése
    if not check_existing_tables(db_path):
        print("❌ Adatbázis betöltés megszakítva!")
        return

    load_nf_tables_to_db(export_folder, db_path)

    # 6. LÉPÉS: Végleges eredmény
    print("\n" + "=" * 60)
    print("🎉 MINDEN FOLYAMAT SIKERESEN BEFEJEZVE!")
    print("=" * 60)

    final_files = scan_csv_files(export_folder)
    nf_files = [f for f in final_files if '_NFdone' in f]
    original_files = [f for f in final_files if '_NFdone' not in f]

    if nf_files:
        print(f"\n📊 NF3 TÁBLÁK: {len(nf_files)} fájl")
        for file in nf_files:
            file_path = os.path.join(export_folder, file)
            file_size = os.path.getsize(file_path) / 1024
            print(f"   📄 {file} ({file_size:.1f} KB)")

    if original_files:
        print(f"\n📊 EREDETI FÁJLOK: {len(original_files)} fájl")
        for file in original_files:
            file_path = os.path.join(export_folder, file)
            file_size = os.path.getsize(file_path) / 1024
            print(f"   📄 {file} ({file_size:.1f} KB)")

    print(f"\n💾 Adatbázis: {db_path}")


if __name__ == "__main__":
    main()
