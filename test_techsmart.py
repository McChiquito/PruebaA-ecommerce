import pdfplumber

ruta_pdf = r"C:\Users\alicy\OneDrive\Desktop\multiproveedor-1\catalogos\ListaDePreciosTM18.pdf"

with pdfplumber.open(ruta_pdf) as pdf:
    for i, pagina in enumerate(pdf.pages, start=1):
        print(f"\n📄 Página {i}:")
        texto = pagina.extract_text()
        if texto:
            print(texto[:1000])  # muestra los primeros 1000 caracteres
        else:
            print("⚠️ No se detectó texto en esta página.")
        break  # solo primera página
