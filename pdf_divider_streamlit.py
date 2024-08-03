import streamlit as st
import fitz  # PyMuPDF
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import os
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def read_qr(image, qr_content):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (7, 7), 0)
    
    qr_codes = decode(blurred_image)
    found_pages = []

    if qr_codes:
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')
            if qr_data == qr_content:
                found_pages.append(True)
            else:
                found_pages.append(False)
    
    return found_pages

def process_pdf(pdf_bytes, qr_content):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    results = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        
        try:
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            found_pages = read_qr(img_np, qr_content)
        except Exception as e:
            st.write(f"Erro ao processar a página {page_num + 1}: {e}")
            continue
        
        if any(found_pages):
            results.append(page_num + 1)

    if doc.page_count not in results:
        results.append(doc.page_count)

    doc.close()
    
    return results

def divider(file_bytes, divisoes, output_folder):
    pdf_reader = PdfReader(file_bytes)
    pdf_nomes_saida = [] 
    start_page = 0

    for end_page in divisoes: 
        pdf_writer = PdfWriter()

        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        base_name = "output"
        nome_arquivo_saida = os.path.join(output_folder, f"{base_name}_{start_page+1}.pdf")
        pdf_nomes_saida.append(nome_arquivo_saida) 
        with open(nome_arquivo_saida, 'wb') as arquivo_saida:
            pdf_writer.write(arquivo_saida)

        start_page = end_page

    return pdf_nomes_saida

qr_content = 'VINCIEyesOn'

st.title('PDF Divider with QR Code')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
output_folder = st.text_input("Output Folder", "")

if uploaded_file:
    st.write(f"File uploaded: {uploaded_file.name}")

if output_folder:
    st.write(f"Output folder: {output_folder}")

if uploaded_file and output_folder:
    pdf_bytes = BytesIO(uploaded_file.read())
    divisoes = process_pdf(pdf_bytes, qr_content)
    pdf_bytes.seek(0)  # Reset stream position after reading
    pdfs = divider(pdf_bytes, divisoes, output_folder)
    st.write("PDFs divididos e salvos com sucesso!")
    for pdf in pdfs:
        st.write(pdf)