import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def read_qr(image, qr_content):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(gray_image)
    
    if data == qr_content:
        return True
    else:
        return False

def process_pdf(pdf_bytes, qr_content):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    results = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        
        try:
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            found = read_qr(img_np, qr_content)
            if found:
                results.append(page_num + 1)
        except Exception as e:
            st.write(f"Erro ao processar a página {page_num + 1}: {e}")
            continue

    if doc.page_count not in results:
        results.append(doc.page_count)

    doc.close()
    
    return results

def divider(file_bytes, divisoes):
    pdf_reader = PdfReader(file_bytes)
    pdf_nomes_saida = []
    start_page = 0

    for end_page in divisoes: 
        pdf_writer = PdfWriter()

        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        pdf_nomes_saida.append(output)
        start_page = end_page

    return pdf_nomes_saida

qr_content = 'VINCIEyesOn'

st.title('PDF Divider with QR Code')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    st.write(f"File uploaded: {uploaded_file.name}")
    pdf_bytes = BytesIO(uploaded_file.read())
    divisoes = process_pdf(pdf_bytes, qr_content)
    pdf_bytes.seek(0)  # Reset stream position after reading
    pdfs = divider(pdf_bytes, divisoes)
    st.write("PDFs divididos e prontos para download!")
    
    for i, pdf in enumerate(pdfs):
        st.download_button(
            label=f"Download PDF {i+1}",
            data=pdf,
            file_name=f"output_{i+1}.pdf",
            mime="application/pdf"
        )
