import sqlite3
import os


def create_database():
    """
    Adatbázis létrehozása, ha még nem létezik
    Returns:
        bool: Mindig True, ha sikeres
    """

    # Ellenőrizzük, hogy létezik-e a db mappa
    db_dir = 'db'
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"✅ 'db' mappa létrehozva: {db_dir}")

    # Adatbázis fájl útvonala
    db_path = 'db/data.db'

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
