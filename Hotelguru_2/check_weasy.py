from weasyprint import HTML
import os
import traceback  # Traceback importhoz

print("--- WeasyPrint Test Script ---")
print("Attempting to import WeasyPrint...")
try:
    # Itt már megtörtént az importálás, ha nem dobott hibát a script elején
    print("WeasyPrint imported successfully.")

    # Egyszerű HTML tartalom
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Test</title></head>
    <body>
        <h1>Helló WeasyPrint!</h1>
        <p>Ez egy teszt. Árvíztűrő tükörfúrógép.</p>
    </body>
    </html>
    """
    print("Attempting to create HTML object...")
    html = HTML(string=html_content)
    pdf_filename = "test_output.pdf"
    print(f"Attempting to write PDF to {pdf_filename}...")
    html.write_pdf(pdf_filename)  # <<< Itt vagy az előző sorban szokott hiba lenni
    print(f"SUCCESS: Successfully wrote {pdf_filename}")

    # Ideiglenes fájl törlése
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
        print(f"Cleaned up {pdf_filename}")

except ImportError as imp_err:
    print(f"IMPORT ERROR: Failed to import WeasyPrint or its dependency: {imp_err}")
    traceback.print_exc()  # Teljes traceback kiírása

except Exception as e:
    print(f"ERROR: An error occurred during PDF generation: {e}")
    traceback.print_exc()  # Teljes traceback kiírása

print("--- Test script finished. ---")
