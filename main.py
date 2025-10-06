# code/databaseCreate.py
import sqlite3
import os


def create_database():
    # Adatbázis fájl elérési útja
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'project_database.db')

    # Biztosítjuk, hogy a db könyvtár létezik
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Kapcsolódás az adatbázishoz
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Adagok tábla létrehozása
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS adagok (
        adag_szam INTEGER PRIMARY KEY,
        kezdet_datum TEXT,
        kezdet_ido TEXT,
        vege_datum TEXT,
        vege_ido TEXT,
        adagkozi_ido INTEGER,
        adag_ido INTEGER
    )
    ''')

    # Hőmérséklet adatok tábla létrehozása
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS homersekletek (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meres_idopont TEXT,
        panel_1 REAL,
        panel_2 REAL,
        panel_3 REAL,
        panel_4 REAL,
        panel_5 REAL,
        panel_6 REAL,
        panel_8 REAL,
        panel_9 REAL,
        panel_10 REAL,
        panel_11 REAL,
        panel_12 REAL,
        panel_13 REAL,
        panel_14 REAL,
        panel_15 REAL
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Adatbázis sikeresen létrehozva: {db_path}")


if __name__ == "__main__":
    create_database()
