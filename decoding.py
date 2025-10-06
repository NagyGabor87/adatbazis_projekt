import os
import pandas as pd
import chardet


def decode_csv_file(input_file_path: str, output_dir: str) -> str:
    """
    CSV fájl dekódolása és mentése UTF-8-BOM formátumban

    Args:
        input_file_path: A bemeneti CSV fájl teljes útvonala
        output_dir: A kimeneti könyvtár útvonala

    Returns:
        Az exportált fájl útvonala, vagy üres string hiba esetén
    """

    # Fájl ellenőrzése
    if not os.path.exists(input_file_path):
        print(f"✗ A megadott fájl nem található: {input_file_path}")
        return ""

    # Kimeneti könyvtár ellenőrzése és létrehozása
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Kimeneti könyvtár létrehozva: {output_dir}")

    # Kimeneti fájlnév generálása
    original_filename = os.path.basename(input_file_path)
    name_without_ext = os.path.splitext(original_filename)[0]
    output_filename = f"{name_without_ext}_decoded.csv"
    output_file_path = os.path.join(output_dir, output_filename)

    print(f"Bemeneti fájl: {input_file_path}")
    print(f"Kimeneti fájl: {output_file_path}")

    # 1. Lépés: Kódolás automatikus felismerése chardet-tel
    print("\n1. Kódolás automatikus felismerése...")
    detected_encoding = detect_encoding_with_chardet(input_file_path)

    if detected_encoding:
        print(f"✓ Automatikus felismerés: {detected_encoding}")

        # Megjelenítjük az automatikusan felismert kódolás adatait
        print(f"\nAutomatikusan felismert kódolás adatai:")
        show_file_preview(input_file_path, detected_encoding)

        use_auto = input("\nSzeretnéd használni az automatikusan felismert kódolást? (i/n): ").strip().lower()
        if use_auto == 'i':
            selected_encoding = detected_encoding
        else:
            selected_encoding = select_encoding_manual(input_file_path)
    else:
        print("✗ Automatikus felismerés sikertelen, kézi választás...")
        selected_encoding = select_encoding_manual(input_file_path)

    if not selected_encoding:
        print("✗ Nem sikerült kódolást kiválasztani")
        return ""

    # 2. Lépés: Adatok beolvasása kiválasztott kódolással
    print(f"\n2. Adatok beolvasása {selected_encoding} kódolással...")
    try:
        df = pd.read_csv(input_file_path, delimiter=';', encoding=selected_encoding)
        print(f"✓ Beolvasva: {len(df)} sor, {len(df.columns)} oszlop")

        # Adatok előnézete
        print("\nAdatok előnézete:")
        print(f"Oszlopnevek: {list(df.columns)}")
        if len(df) > 0:
            print(f"Első sor: {df.iloc[0].tolist()}")

    except Exception as e:
        print(f"✗ Hiba a beolvasás során: {e}")
        return ""

    # 3. Lépés: Mentés UTF-8-SIG kódolással (Excel kompatibilis)
    try:
        df.to_csv(output_file_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"\n✓ Adatok exportálva: {output_file_path}")
        print(f"   Végeredmény: {len(df)} sor, {len(df.columns)} oszlop")
        print(f"   Kódolás: UTF-8-BOM (Excel kompatibilis)")
        return output_file_path

    except Exception as e:
        print(f"✗ Hiba az exportálás során: {e}")
        return ""


def detect_encoding_with_chardet(input_file: str) -> str:
    """Kódolás automatikus felismerése chardet könyvtárral"""
    try:
        with open(input_file, 'rb') as file:
            # Az első 10KB-ból próbálja megállapítani a kódolást
            raw_data = file.read(10000)

        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']

        print(f"   Felismert kódolás: {encoding}")
        print(f"   Megbízhatóság: {confidence:.1%}")

        # Csak akkor fogadjuk el, ha elég magas a megbízhatóság
        if confidence > 0.7:
            # Ellenőrizzük, hogy tényleg működik-e
            try:
                pd.read_csv(input_file, delimiter=';', encoding=encoding, nrows=2)
                return encoding
            except:
                print(f"   A felismert kódolás nem működik a pandas-szal")
                return ""
        else:
            print("   A megbízhatóság túl alacsony")
            return ""

    except Exception as e:
        print(f"   Hiba a chardet használata során: {e}")
        return ""


def show_file_preview(input_file: str, encoding: str) -> None:
    """Fájl előnézet megjelenítése adott kódolással"""
    try:
        df_preview = pd.read_csv(input_file, delimiter=';', encoding=encoding, nrows=3)
        print(f"Oszlopnevek: {list(df_preview.columns)}")
        if len(df_preview) > 0:
            print(f"Első sor: {df_preview.iloc[0].tolist()}")
        print("✓ Az adatok helyesen megjeleníthetők ezzel a kódolással")
    except Exception as e:
        print(f"✗ Hiba az előnézet megjelenítése során: {e}")


def select_encoding_manual(input_file: str) -> str:
    """Kódolás kézi kiválasztása a felhasználó által"""

    encodings = ['latin2', 'cp852', 'cp1250', 'utf-8']
    working_encodings = []

    print("\nKézi kódolás kiválasztása...\n")

    for encoding in encodings:
        try:
            # Csak az első néhány sor beolvasása teszteléshez
            df_test = pd.read_csv(input_file, delimiter=';', encoding=encoding, nrows=3)
            working_encodings.append(encoding)

            print(f"=== {encoding} ===")
            print(f"Fejléc: {list(df_test.columns)}")
            if len(df_test) > 0:
                print(f"1. sor: {df_test.iloc[0].tolist()}")
            print("✓ MŰKÖDIK\n")

        except Exception as e:
            print(f"=== {encoding} ===")
            print(f"✗ NEM MŰKÖDIK - {str(e)[:60]}\n")

    if not working_encodings:
        print("Egyik kódolás sem működik!")
        return ""

    # Választás
    print("Működő kódolások:")
    for i, encoding in enumerate(working_encodings, 1):
        print(f"  {i}. {encoding}")

    try:
        choice = int(input(f"\nVálassz kódolást (1-{len(working_encodings)}): "))
        return working_encodings[choice - 1]
    except:
        print("Érvénytelen választás!")
        return ""


def main() -> None:
    """Főprogram - példa használatra"""

    # Példa használat - megtartva az eredeti útvonalakat
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    input_file = os.path.join(root_dir, 'import', 'Adagok.csv')
    export_dir = os.path.join(root_dir, 'temp')

    if os.path.exists(input_file):
        result = decode_csv_file(input_file, export_dir)
        if result:
            print(f"\n🎉 Sikeres dekódolás: {result}")
        else:
            print(f"\n❌ A dekódolás sikertelen")
    else:
        print(f"✗ A példa fájl nem található: {input_file}")
        print("\nHasználat más fájlokkal:")
        print("decode_csv_file('c:/utvonal/bemeneti.csv', 'c:/utvonal/kimeneti_mappa')")


if __name__ == "__main__":
    main()
