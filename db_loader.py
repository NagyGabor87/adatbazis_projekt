import os
import sqlite3
import pandas as pd


def discover_nf_tables(export_dir):
    """_NFdone fájlok felfedezése"""
    nf_files = []
    for file in os.listdir(export_dir):
        if file.endswith('_NFdone.csv'):
            nf_files.append(file)
    return nf_files


def infer_sql_type(df, column):
    """Oszlop típus automatikus felismerése"""
    if pd.api.types.is_integer_dtype(df[column]):
        return 'INTEGER'
    elif pd.api.types.is_numeric_dtype(df[column]):
        return 'REAL'
    else:
        return 'TEXT'


def create_table_from_csv(cursor, table_name, df):
    """Tábla létrehozása CSV alapján"""

    # Tábla törlése ha létezik
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Oszlopok és típusok
    columns = []
    for col in df.columns:
        sql_type = infer_sql_type(df, col)
        columns.append(f"{col} {sql_type}")

    # CREATE TABLE SQL
    create_sql = f"CREATE TABLE {table_name} (\n    "
    create_sql += ",\n    ".join(columns)
    create_sql += "\n)"

    cursor.execute(create_sql)
    print(f"  📋 Tábla létrehozva: {table_name}")


def load_data_to_table(cursor, table_name, df):
    """Adatok betöltése táblába"""
    # INSERT SQL
    placeholders = ', '.join(['?' for _ in df.columns])
    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    # Adatok betöltése
    for _, row in df.iterrows():
        cursor.execute(insert_sql, tuple(row))

    print(f"  📥 Adatok betöltve: {len(df)} sor")


def load_nf_tables_to_db(export_dir, db_path):
    """Összes _NFdone tábla betöltése adatbázisba"""
    nf_files = discover_nf_tables(export_dir)
    print(f"🔍 {len(nf_files)} NF3 tábla betöltése...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for nf_file in nf_files:
        print(f"\n🎯 {nf_file}")

        # Beolvasás
        file_path = os.path.join(export_dir, nf_file)
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')

        # Tábla neve (.csv nélkül)
        table_name = nf_file.replace('.csv', '')

        # Tábla létrehozás és adatbetöltés
        create_table_from_csv(cursor, table_name, df)
        load_data_to_table(cursor, table_name, df)

    conn.commit()
    conn.close()
    print(f"\n✅ KÉSZ! {len(nf_files)} tábla betöltve.")
