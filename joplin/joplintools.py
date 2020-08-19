import fitz
import base64

def CreatePDFPreviev(pdffile, png, site):
    doc = fitz.open(pdffile)
    page = doc.loadPage(site - 1)
    pix = page.getPixmap()
    pix.writePNG(png)

