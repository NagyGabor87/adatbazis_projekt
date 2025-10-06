import os
from decoding import decode_csv_file
from browse import scan_csv_files, display_csv_files


def process_csv_files(folder_path: str) -> None:
    """
    CSV fájlok feldolgozása
    """

    # 1. Mappa szkennelése
    csv_files = scan_csv_files(folder_path)
    file_count = len(csv_files)

    if file_count == 0:
        return

    # 2. Fájlok megjelenítése
    display_csv_files(csv_files, folder_path)

    # 3. Kimeneti mappa beállítása
    output_dir = os.path.join(os.path.dirname(folder_path), 'temp')

    # 4. Feldolgozás indítása
    print(f"\n🔄 {file_count} CSV fájl feldolgozása...")

    successful_files = []

    for csv_file in csv_files:
        input_file_path = os.path.join(folder_path, csv_file)

        print(f"\n{'─' * 40}")
        print(f"📄 {csv_file}")
        print(f"{'─' * 40}")

        result = decode_csv_file(input_file_path, output_dir)

        if result:
            successful_files.append(csv_file)
            print(f"✅ SIKERES")
        else:
            print(f"❌ SIKERTELEN")

    # 5. Eredmény jelentés
    print(f"\n{'=' * 50}")
    print(f"🎉 KÉSZ: {len(successful_files)}/{file_count} fájl")
    print(f"{'=' * 50}")


def main():
    """
    Főprogram - CSV fájlok automatikus feldolgozása
    """

    print("=" * 50)
    print("🚀 CSV FÁJLOK FELDOLGOZÁSA")
    print("=" * 50)

    # Projekt útvonalak
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    # Mappa megadása
    folder_name = 'import'
    folder_path = os.path.join(root_dir, folder_name)

    print(f"\n📁 Feldolgozandó mappa: {folder_path}")

    # Feldolgozás indítása
    process_csv_files(folder_path)


if __name__ == "__main__":
    main()
