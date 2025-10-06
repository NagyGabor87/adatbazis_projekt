import sqlite3
import os

def create_database():
    """Adatbázis és táblák létrehozása"""
    
    # Ellenőrizzük, hogy létezik-e a db mappa
    db_dir = 'db'
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Adatbázis kapcsolat létrehozása
    conn = sqlite3.connect('db/data.db')
    cursor = conn.cursor()
    
    # Adagok tábla létrehozása
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adagok (
            adag_id INTEGER PRIMARY KEY,
            kezdet_datum DATE,
            kezdet_ido TIME,
            vege_datum DATE,
            vege_ido TIME,
            adagkozi_ido INTEGER,
            adag_ido INTEGER
        )
    ''')
    
    # Hőmérséklet tábla létrehozása
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homerseklet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meres_idopont DATETIME,
            panel_1_hofok REAL,
            panel_2_hofok REAL,
            panel_3_hofok REAL,
            panel_4_hofok REAL,
            panel_5_hofok REAL,
            panel_6_hofok REAL,
            panel_8_hofok REAL,
            panel_9_hofok REAL,
            panel_10_hofok REAL,
            panel_11_hofok REAL,
            panel_12_hofok REAL,
            panel_13_hofok REAL,
            panel_14_hofok REAL,
            panel_15_hofok REAL
        )
    ''')
    
    # Commit és kapcsolat bezárása
    conn.commit()
    conn.close()
    print("Adatbázis és táblák sikeresen létrehozva!")

if __name__ == "__main__":
    create_database()
