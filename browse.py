import os


def scan_csv_files(folder_path: str) -> list:
    """
    Mappa szkennelése CSV fájlokra

    Args:
        folder_path: A szkennelendő mappa útvonala

    Returns:
        list: CSV fájlok listája (üres lista, ha nincs vagy hiba)
    """

    if not os.path.exists(folder_path):
        print(f"❌ A mappa nem található: {folder_path}")
        return []

    csv_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.csv') and os.path.isfile(os.path.join(folder_path, file)):
            csv_files.append(file)

    return csv_files


def display_csv_files(csv_files: list, folder_path: str) -> None:
    """
    CSV fájlok listájának megjelenítése
    """

    if not csv_files:
        print("ℹ️  Nincs CSV fájl a mappában.")
        return

    print(f"📁 Mappa: {folder_path}")
    print(f"✅ {len(csv_files)} CSV fájl található:")

    for i, csv_file in enumerate(csv_files, 1):
        file_path = os.path.join(folder_path, csv_file)
        file_size = os.path.getsize(file_path) / 1024  # KB-ban
        print(f"   {i}. {csv_file} ({file_size:.1f} KB)")
