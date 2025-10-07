import pandas as pd
import os


def normalize_homerseklet(df):
    """Hőmérséklet NF3 normalizálása - JAVÍTOTT (redundáns meres_id nélkül)"""
    print("  Hőmérséklet NF3 normalizálása...")

    # Hosszú formátum (tidy data)
    long_data = []

    for i in range(1, 16):
        if i == 7:  # 7-es panel nincs
            continue

        time_col = f'Panel hőfok {i} [°C] Time'
        value_col = f'Panel hőfok {i} [°C] ValueY'

        if time_col in df.columns and value_col in df.columns:
            panel_df = df[[time_col, value_col]].copy()
            panel_df.columns = ['meres_idopont', 'hofok']
            panel_df['panel_szam'] = i
            panel_df = panel_df.dropna()

            long_data.append(panel_df)

    # Összefésülés - NINCS meres_id, mert redundáns
    homerseklet_3nf = pd.concat(long_data, ignore_index=True)

    # Egyedi rekordok ellenőrzése
    duplicate_check = homerseklet_3nf.duplicated(subset=['meres_idopont', 'panel_szam']).sum()
    if duplicate_check > 0:
        print(f"  ⚠️  Figyelem: {duplicate_check} duplikált mérés található")
        # Duplikáltak eltávolítása
        homerseklet_3nf = homerseklet_3nf.drop_duplicates(subset=['meres_idopont', 'panel_szam'])
        print(f"  ✅ Duplikáltak eltávolítva: {len(homerseklet_3nf)} egyedi mérés maradt")

    return {
        'homerseklet_meresek_NFdone': homerseklet_3nf
    }


def process_homerseklet_file(input_file_path, output_dir):
    """Hőmérséklet fájl feldolgozása"""
    filename = os.path.basename(input_file_path)
    print(f"🎯 HŐMÉRSÉKLET NF3: {filename}")

    # Beolvasás
    df = pd.read_csv(input_file_path, delimiter=';', encoding='utf-8-sig')

    # Normalizálás
    normalized_tables = normalize_homerseklet(df)

    # Fájlok mentése
    for table_name, table_data in normalized_tables.items():
        output_path = os.path.join(output_dir, f"{table_name}.csv")
        table_data.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"  💾 {table_name}.csv ({len(table_data)} sor)")

        # Első néhány sor megjelenítése ellenőrzésként
        print(f"     Előnézet: {len(table_data.columns)} oszlop")
        if len(table_data) > 0:
            print(f"     Első sor: {table_data.iloc[0].tolist()}")

    return len(normalized_tables)
