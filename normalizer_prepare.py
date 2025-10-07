import os
import pandas as pd
from normalizer_adagok import process_adagok_file
from normalizer_homerseklet import process_homerseklet_file


def normalize_file(input_file_path, output_dir):
    """Fájl NF3 normalizálása - fő koordináló függvény"""
    filename = os.path.basename(input_file_path)

    # Fájltípus alapú útválasztás
    if 'Adagok' in filename:
        return process_adagok_file(input_file_path, output_dir)
    elif any(x in filename for x in ['Hutopanelek', 'homerseklet', 'panel']):
        return process_homerseklet_file(input_file_path, output_dir)
    else:
        # Alapértelmezett - nincs normalizálás, csak _NFdone hozzáadás
        print(f"🎯 ALAPÉRTELMEZETT NF3: {filename}")

        df = pd.read_csv(input_file_path, delimiter=';', encoding='utf-8-sig')
        name_only = filename.replace('.csv', '')
        normalized_tables = {f"{name_only}_NFdone": df}

        for table_name, table_data in normalized_tables.items():
            output_path = os.path.join(output_dir, f"{table_name}.csv")
            table_data.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
            print(f"  💾 {table_name}.csv ({len(table_data)} sor)")

        return len(normalized_tables)


def get_normalizer_info():
    """Normalizálók információja"""
    return {
        'adagok': '3 tábla: kezdet_adagok, vege_adatok, ido_ellenorzes',
        'homerseklet': '1 tábla: homerseklet_meresek (tidy data)',
        'default': '1 tábla: eredeti fájl _NFdone kiegészítéssel'
    }
