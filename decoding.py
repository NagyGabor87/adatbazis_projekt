import os
import pandas as pd
import chardet


def decode_csv_file(input_file_path: str, output_dir: str) -> str:
    """
    CSV fájl dekódolása és mentése UTF-8-BOM formátumban
    """

    if not os.path.exists(input_file_path):
        print(f"✗ A fájl nem található: {input_file_path}")
        return ""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Kimeneti fájlnév generálása
    original_filename = os.path.basename(input_file_path)
    name_without_ext = os.path.splitext(original_filename)[0]
    output_filename = f"{name_without_ext}_decoded.csv"
    output_file_path = os.path.join(output_dir, output_filename)

    print(f"📥 Bemeneti: {original_filename}")
    print(f"📤 Kimeneti: {output_filename}")

    # 1. Kódolás automatikus felismerése
    print("\n1. Kódolás automatikus felismerése...")
    detected_encoding, confidence = detect_encoding_with_chardet(input_file_path)

    if detected_encoding:
        print(f"✓ Automatikus felismerés: {detected_encoding}")
        print(f"📊 Megbízhatóság: {confidence:.1%}")

        # Megjelenítjük az automatikusan felismert kódolás adatait
        print(f"\nAutomatikusan felismert kódolás adatai:")
        show_file_preview(input_file_path, detected_encoding)

        # DÖNTÉSI PONT: 99%+ megbízhatóság esetén automatikusan elfogadjuk
        if confidence >= 0.99:
            print("🎯 99%+ megbízhatóság → automatikus elfogadás")
            selected_encoding = detected_encoding
        else:
            print(f"⚠️  Alacsony megbízhatóság ({confidence:.1%}) → kézi választás szükséges")
            response = input("\nSzeretnéd használni az automatikusan felismert kódolást? (i/n): ").strip().lower()

            if response == 'i':
                print("❌ MEGSZAKÍTVA: Alacsony megbízhatóság miatt a további feldolgozás hibás lehet!")
                print("🚪 Program leáll...")
                exit(1)
            else:
                selected_encoding = select_encoding_manual(input_file_path)
    else:
        print("✗ Automatikus felismerés sikertelen, kézi választás...")
        selected_encoding = select_encoding_manual(input_file_path)

    if not selected_encoding:
        return ""

    # 2. Adatok beolvasása kiválasztott kódolással
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

    # 3. Mentés UTF-8-SIG kódolással
    try:
        df.to_csv(output_file_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"\n✓ Adatok exportálva: {output_file_path}")
        print(f"   Végeredmény: {len(df)} sor, {len(df.columns)} oszlop")
        print(f"   Kódolás: UTF-8-BOM (Excel kompatibilis)")
        return output_file_path

    except Exception as e:
        print(f"✗ Hiba az exportálás során: {e}")
        return ""


def detect_encoding_with_chardet(input_file: str):
    """Kódolás automatikus felismerése chardet könyvtárral"""
    try:
        with open(input_file, 'rb') as file:
            raw_data = file.read(50000)

        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']

        # Kódolás normalizálása
        encoding = normalize_encoding_name(encoding)

        if confidence > 0.6:
            try:
                pd.read_csv(input_file, delimiter=';', encoding=encoding, nrows=2)
                return encoding, confidence
            except:
                return "", 0
        else:
            return "", 0

    except Exception as e:
        print(f"   Hiba: {e}")
        return "", 0


def normalize_encoding_name(encoding: str) -> str:
    """Kódolás nevek normalizálása"""
    encoding_map = {
        'ISO-8859-2': 'latin2',
        'ISO-8859-1': 'latin1',
        'Windows-1250': 'cp1250',
        'Windows-1252': 'cp1252',
        'UTF-8-SIG': 'utf-8-sig'
    }
    return encoding_map.get(encoding, encoding)


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

    print("\n🧩 Kézi kódolás kiválasztása...\n")

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
        print("❌ Egyik kódolás sem működik!")
        return ""

    # Választás
    print("Működő kódolások:")
    for i, encoding in enumerate(working_encodings, 1):
        print(f"  {i}. {encoding}")
    print(f"  {len(working_encodings) + 1}. ❌ Manuálisan oldom meg (kilépés)")

    # Input kívül a try-except blokkon
    choice_input = input(f"\nVálassz kódolást (1-{len(working_encodings) + 1}): ").strip()

    # Ellenőrizzük, hogy szám-e
    if not choice_input.isdigit():
        print("❌ Érvénytelen választás! Csak számot adj meg.")
        print("🚪 Program leáll...")
        exit(1)

    choice = int(choice_input)

    if choice == len(working_encodings) + 1:
        print("\n❌ KILÉPÉS: Felhasználó manuális megoldást választott")
        print("🚪 Program leáll...")
        exit(1)

    if 1 <= choice <= len(working_encodings):
        return working_encodings[choice - 1]
    else:
        print("❌ Érvénytelen választás!")
        print("🚪 Program leáll...")
        exit(1)
