import pandas as pd
import os


def clean_file(input_file_path: str, output_dir: str) -> str:
    """
    Fájltisztító - a main.py számára optimalizálva

    Args:
        input_file_path: A bemeneti fájl teljes útvonala
        output_dir: A kimeneti mappa útvonala

    Returns:
        str: A kimeneti fájl útvonala, vagy üres string hiba esetén
    """

    try:
        # Kimeneti fájl neve (_clean hozzáadásával)
        original_filename = os.path.basename(input_file_path)
        name, ext = os.path.splitext(original_filename)
        output_filename = f"{name}_clean{ext}"
        output_file_path = os.path.join(output_dir, output_filename)

        # Kimeneti mappa létrehozása ha nem létezik
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✅ Kimeneti mappa létrehozva: {output_dir}")

        # Fájl beolvasása
        df = pd.read_csv(input_file_path, delimiter=';', encoding='utf-8-sig')

        print(f"📥 Fájl beolvasva: {original_filename}")
        print(f"📊 Eredeti adatok: {len(df)} sor, {len(df.columns)} oszlop")

        # EGYSZERŰ TISZTÍTÁS
        df_clean = (df
                    .copy()
                    .drop_duplicates()  # Duplikált sorok eltávolítása
                    .dropna(how='all')  # Teljesen üres sorok
                    .fillna('')  # Hiányzó értékek helyettesítése
                    .rename(columns=lambda x: x.strip())  # Oszlopnevek tisztítása
                    )

        # Szöveges oszlopok automatikus tisztítása
        text_cols = df_clean.select_dtypes(include=['object']).columns
        df_clean[text_cols] = df_clean[text_cols].apply(lambda x: x.str.strip())

        # Mentés Excel kompatibilis formátumban
        df_clean.to_csv(output_file_path, index=False, sep=';', encoding='utf-8-sig')

        print(f"✅ Tisztított fájl: {output_file_path}")
        print(f"✅ Tisztított adatok: {len(df_clean)} sor, {len(df_clean.columns)} oszlop")

        return output_file_path

    except Exception as e:
        print(f"❌ Hiba a tisztítás során: {e}")
        return ""


def clean_file_with_fallback(input_file_path: str, output_dir: str) -> str:
    """
    Fájltisztító alternatív kódolások kipróbálásával
    """
    encodings = ['utf-8-sig', 'utf-8', 'latin2', 'cp1250', 'cp852']

    for encoding in encodings:
        try:
            print(f"🔍 Kísérlet {encoding} kódolással...")
            df = pd.read_csv(input_file_path, delimiter=';', encoding=encoding)

            # Ha sikerült beolvasni, folytatjuk a tisztítással
            original_filename = os.path.basename(input_file_path)
            name, ext = os.path.splitext(original_filename)
            output_filename = f"{name}_clean{ext}"
            output_file_path = os.path.join(output_dir, output_filename)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            df_clean = (df
                        .copy()
                        .drop_duplicates()
                        .dropna(how='all')
                        .fillna('')
                        .rename(columns=lambda x: x.strip())
                        )

            text_cols = df_clean.select_dtypes(include=['object']).columns
            df_clean[text_cols] = df_clean[text_cols].apply(lambda x: x.str.strip())

            df_clean.to_csv(output_file_path, index=False, sep=';', encoding='utf-8-sig')
            print(f"✅ Sikeres tisztítás {encoding} kódolással")
            return output_file_path

        except Exception as e:
            print(f"❌ {encoding} nem működik: {str(e)[:50]}...")
            continue

    print("❌ Egyik kódolás sem működött!")
    return ""


if __name__ == "__main__":
    # Teszt a cleaning.py fájllal
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    temp_dir = os.path.join(root_dir, 'temp')
    export_dir = os.path.join(root_dir, 'export')

    # Teszteljük az első CSV fájlt a temp mappából
    csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]

    if csv_files:
        test_file = os.path.join(temp_dir, csv_files[0])
        print(f"🧪 Tesztelés: {test_file}")
        result = clean_file(test_file, export_dir)
        if result:
            print("🎉 Teszt sikeres!")
        else:
            print("💥 Teszt sikertelen!")
    else:
        print("ℹ️  Nincs tesztelhető fájl a temp mappában")
