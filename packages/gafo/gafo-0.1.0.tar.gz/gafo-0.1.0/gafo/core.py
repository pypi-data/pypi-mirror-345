import zlib

def create_gafo_file(input_path: str, output_path: str):
    """
    يقرأ ملف، يضغطه باستخدام ZLIB، ثم يضيف الهيدر 'GAFO FILE' ويكتب النتيجة في ملف جديد.
    """
    header = b"GAFO FILE"

    try:
        with open(input_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"الملف {input_path} غير موجود")

    compressed = zlib.compress(data)

    with open(output_path, "wb") as f:
        f.write(header)
        f.write(compressed)

    print(f"[✓] تم إنشاء ملف GAFO بنجاح: {output_path}")
