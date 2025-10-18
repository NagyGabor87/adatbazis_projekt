import sqlite3
import os


def create_database(db_path=None):
    """
    Adatbázis létrehozása a megadott útvonalon, vagy root/db/data.db alapértelmezettként

    Args:
        db_path: Opcionális - adatbázis útvonala. Ha None, akkor root/db/data.db lesz

    Returns:
        bool: Mindig True, ha sikeres
    """
    # Alapértelmezett útvonal beállítása
    if db_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        db_path = os.path.join(root_dir, 'db', 'data.db')

    # Ellenőrizzük, hogy létezik-e a db mappa
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"✅ 'db' mappa létrehozva: {db_dir}")

    # Ellenőrizzük, hogy létezik-e az adatbázis fájl
    if os.path.exists(db_path):
        print(f"✅ Adatbázis már létezik: {db_path}")
        return True

    # Adatbázis kapcsolat létrehozása (ez létrehozza a fájlt)
    conn = sqlite3.connect(db_path)
    conn.close()

    print(f"✅ Új adatbázis létrehozva: {db_path}")
    return True


if __name__ == "__main__":
    create_database()
