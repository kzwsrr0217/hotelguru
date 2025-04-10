from flask_jwt_extended import jwt_required, get_jwt_identity  # JWT védelemhez
from app import auth
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez
from app.blueprints.invoice import bp

# Sémák és Service import
from app.blueprints.invoice.schemas import InvoiceSchema
from app.blueprints.invoice.service import InvoiceService

# Hibakezelés és jogosultság
from flask import send_file, current_app, after_this_request, render_template
from apiflask import HTTPError
from flask import send_file, current_app, after_this_request
import os
import tempfile
import logging

try:
    from weasyprint import HTML

    WEASYPRINT_INSTALLED = True
except ImportError:
    logging.warning("WeasyPrint not installed. PDF generation will be unavailable.")
    WEASYPRINT_INSTALLED = False

# @bp.post('/generate/<int:reservation_id>')
# @jwt_required() # JWT védelemhez
# @roles_required('Administrator', 'Receptionist') # Csak admin és recepciós jogosultságú felhasználók férhetnek hozzá
# @bp.output(InvoiceSchema)
# def generate_invoice(reservation_id):
#    """Számla generálása JSON-ként"""
#    success, response = InvoiceService.generate_invoice(reservation_id)
#    if success:
#        return response, 200
#    raise HTTPError(400, message=response)


@bp.get("/download/<int:invoice_id>")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required("Receptionist", "Administrator")
@bp.doc(
    summary="Download Invoice PDF",
    description="Generates and downloads the invoice as a PDF file.",
)
def download_invoice(invoice_id):
    """PDF számla letöltése"""
    # TODO: Jogosultság ellenőrzése: vendég csak sajátját?

    if not WEASYPRINT_INSTALLED:
        raise HTTPError(
            501,
            message="PDF generálás nem elérhető: A WeasyPrint könyvtár nincs telepítve.",
        )

    # 1. Adatok lekérdezése a Service-től
    # invoice_obj = InvoiceService.generate_pdf(invoice_id) # <<< Régi hívás
    invoice_obj = InvoiceService.get_invoice_details_for_pdf(invoice_id)  # <<< Új hívás

    if not invoice_obj:
        # Ha a service None-t adott vissza (nem talált számlát, vagy hiba történt a lekérdezés/számítás során)
        raise HTTPError(
            404,
            message=f"Nem található számla (ID: {invoice_id}) vagy hiba történt az adatok lekérésekor.",
        )

    # 2. HTML renderelése (most már a route kontextusában)
    try:
        # html_content = render_template("invoice/invoice_template.html", invoice=invoice_obj) # <<< Ezt használtuk utoljára
        html_content = render_template(
            "invoice_template.html", invoice=invoice_obj
        )  # <<< Visszaállítás erre
    except Exception as render_ex:
        logging.exception(
            f"Error rendering invoice template for invoice {invoice_id}: {render_ex}"
        )
        raise HTTPError(500, message="Hiba történt a számla sablon renderelésekor.")

    # 3. PDF generálás WeasyPrinttel
    pdf_path = None  # Hogy a finally blokkban tudjuk ellenőrizni
    pdf_file = None
    try:
        html = HTML(string=html_content)
        pdf_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf_path = pdf_file.name
        pdf_file.close()
        html.write_pdf(pdf_path)
        logging.info(
            f"PDF generated successfully for invoice {invoice_id} at {pdf_path}"
        )

        # 4. Fájl elküldése és törlés ütemezése
        # Az after_this_request biztosítja, hogy a fájl törlődjön, miután a kérés befejeződött
        @after_this_request
        def remove_file(response):
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logging.info(f"Temporary PDF file deleted: {pdf_path}")
                except Exception as error:
                    logging.error(f"Error removing temporary file {pdf_path}: {error}")
            return response

        # Fájl elküldése letöltésre
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"szamla_{invoice_id}.pdf",
            mimetype="application/pdf",
        )

    except Exception as pdf_ex:
        # Ha a WeasyPrint vagy a fájl írása közben hiba történik
        logging.exception(
            f"Error during PDF generation or file writing for invoice {invoice_id}: {pdf_ex}"
        )
        # Próbáljuk meg törölni az ideiglenes fájlt, ha létrejött
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception as del_ex:
                logging.error(
                    f"Could not remove temp file {pdf_path} after PDF generation error: {del_ex}"
                )
        raise HTTPError(500, message="Hiba történt a PDF fájl létrehozása közben.")
