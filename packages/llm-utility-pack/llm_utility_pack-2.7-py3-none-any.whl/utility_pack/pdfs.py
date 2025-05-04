from utility_pack.ocr_util import is_photo, ocr_page
from enum import Enum
import fitz

def get_pdf_page_as_image(pdf_path, page_num, zoom_factor=3.5):
    # 1 - Read PDF
    pdf_document = fitz.open(pdf_path)

    # 2 - Convert page to image
    page = pdf_document.load_page(page_num)

    # Define the zoom factor for the image resolution. Higher values mean more pixels.
    mat = fitz.Matrix(zoom_factor, zoom_factor)

    # Render the page to an image (pixmap)
    pix_image = page.get_pixmap(matrix=mat)

    return pix_image

class OcrStrategy(str, Enum):
    Always = "always"
    Never = "never"
    Auto = "auto"

def pdf_to_text(filepath, strategy_ocr: OcrStrategy, zoom_factor=3.5):
    pdf_document = fitz.open(filepath)

    page_texts = []

    for page_number in range(pdf_document.page_count):
        print(f'Processando página {page_number + 1}', flush=True)

        page = pdf_document.load_page(page_number)
        page_text = page.get_text("text")

        if strategy_ocr == OcrStrategy.Never:
            pass
        elif strategy_ocr == OcrStrategy.Always:
            pix_image = get_pdf_page_as_image(filepath, page_number, zoom_factor)
            page_text = ocr_page(pix_image)
        else:
            pix_image = get_pdf_page_as_image(filepath, page_number, zoom_factor)
            if len(page_text.split(' ')) < 10 or is_photo(pix_image) or strategy_ocr == OcrStrategy.Always:
                page_text = ocr_page(pix_image)

        while '\n\n' in page_text:
            page_text = page_text.replace('\n\n', '\n')

        page_texts.append(page_text)

    return {
        "full_text": "\n".join(page_texts),
        "text_per_page": [{
            "page": idx + 1,
            "text": text
        } for idx, text in enumerate(page_texts)]
    }
