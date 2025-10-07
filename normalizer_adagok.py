import pandas as pd
import os
from datetime import datetime


def calculate_time_difference(start_date, start_time, end_date, end_time):
    """Időkülönbség számítása percekben"""
    start_str = f"{start_date} {start_time}"
    end_str = f"{end_date} {end_time}"

    start_dt = datetime.strptime(start_str, '%Y.%m.%d %H:%M:%S')
    end_dt = datetime.strptime(end_str, '%Y.%m.%d %H:%M:%S')

    diff_minutes = (end_dt - start_dt).total_seconds() / 60
    return int(diff_minutes)  # Egész percekben


def normalize_adagok(df):
    """Adagok NF3 normalizálása 3 táblára - MINIMALIZÁLT"""
    print("  Adagok NF3 normalizálása (3 tábla - minimalizált)...")

    # 1. Tábla: Kezdet adagok
    kezdet_adagok = df[['ADAGSZÁM', 'Kezdet_DÁTUM', 'Kezdet_IDŐ']].copy()
    kezdet_adagok = kezdet_adagok.drop_duplicates(subset=['ADAGSZÁM'])

    # 2. Tábla: Vége adatok
    vege_adatok = df[['ADAGSZÁM', 'Vége_DÁTUM', 'Vége_IDŐ']].copy()

    # 3. Tábla: Idő ellenőrzés - CSAK A LÉNYEGES OSZLOPOK
    ido_ellenorzes_data = []
    hiba_count = 0

    for _, row in df.iterrows():
        # Adagidő számítása
        szamitott_adagido = calculate_time_difference(
            row['Kezdet_DÁTUM'], row['Kezdet_IDŐ'],
            row['Vége_DÁTUM'], row['Vége_IDŐ']
        )

        # CRC hiba ellenőrzés
        crc_error = abs(szamitott_adagido - row['ADAGIDŐ']) > 1

        if crc_error:
            hiba_count += 1

        ido_ellenorzes_data.append({
            'ADAGSZÁM': row['ADAGSZÁM'],
            'Örökölt_ADAGIDŐ': row['ADAGIDŐ'],
            'Számított_ADAGIDŐ': szamitott_adagido,
            'CRC_Error': crc_error
        })

    ido_ellenorzes = pd.DataFrame(ido_ellenorzes_data)

    # Hibajelzés a konzolon
    if hiba_count > 0:
        print(f"  ⚠️  FIGYELMEZTETÉS: {hiba_count} CRC hiba található!")
        print("  Hibás adagok:")
        for _, hiba in ido_ellenorzes[ido_ellenorzes['CRC_Error'] == True].iterrows():
            print(
                f"    Adag {hiba['ADAGSZÁM']}: Örökölt={hiba['Örökölt_ADAGIDŐ']} vs Számított={hiba['Számított_ADAGIDŐ']}")
    else:
        print("  ✅ Minden adagidő pontos!")

    return {
        'kezdet_adagok_NFdone': kezdet_adagok,
        'vege_adatok_NFdone': vege_adatok,
        'ido_ellenorzes_NFdone': ido_ellenorzes
    }, hiba_count


def normalize_adagok_with_prompt(df, output_dir, source_filename):
    """Adagok normalizálása felhasználói interakcióval"""
    normalized_tables, hiba_count = normalize_adagok(df)

    # Ha nincs hiba, kérdezzük meg, tartsuk-e az ellenőrző táblát
    if hiba_count == 0:
        print(f"\n💡 KÉRDÉS: Minden adagidő pontos ({len(normalized_tables['ido_ellenorzes_NFdone'])} adag)")
        response = input("   Megtartsam az ellenőrző táblát tájékoztatás céljából? (i/n): ").strip().lower()

        if response != 'i':
            # Tábla törlése
            del normalized_tables['ido_ellenorzes_NFdone']
            print("   ✅ Ellenőrző tábla törölve")
        else:
            print("   ✅ Ellenőrző tábla megmarad")

    # Fájlok mentése
    for table_name, table_data in normalized_tables.items():
        output_path = os.path.join(output_dir, f"{table_name}.csv")
        table_data.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"  💾 {table_name}.csv ({len(table_data)} sor)")

    return len(normalized_tables)


def process_adagok_file(input_file_path, output_dir):
    """Adagok fájl feldolgozása"""
    filename = os.path.basename(input_file_path)
    print(f"🎯 ADAGOK NF3: {filename}")

    # Beolvasás
    df = pd.read_csv(input_file_path, delimiter=';', encoding='utf-8-sig')

    # Normalizálás
    return normalize_adagok_with_prompt(df, output_dir, filename)
