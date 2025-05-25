from pathlib import Path
from typing import Union, List

from pdf2image import convert_from_path     # renders PDF pages → PIL Images
import pytesseract                          # OCR engine
from PIL.Image import Image                 # type hint only


def ocr_page_images(images: List[Image], lang: str = "eng") -> str:
    """Run Tesseract on a list of PIL images and join results."""
    return "\n".join(pytesseract.image_to_string(img, lang=lang) for img in images)


def extract_text_from_pdfs(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    suffix: str = ".txt",
    dpi: int = 300,
    lang: str = "eng",
    poppler_path: str | None = None,
) -> None:
    """
    Converts every PDF in `input_dir` to text via OCR and writes *.txt files to `output_dir`.

    Parameters
    ----------
    input_dir   : folder containing PDFs
    output_dir  : folder that will receive text files (created if missing)
    suffix      : filename extension for outputs (default ".txt")
    dpi         : render resolution; higher = better OCR, slower & larger
    lang        : Tesseract language code(s), e.g. "eng+fra"
    poppler_path: directory with Poppler binaries if not on PATH
    """
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in input_dir.glob("*.pdf"):
        try:
            # 1. Render pages to images
            images = convert_from_path(
                pdf_path, dpi=dpi, poppler_path=poppler_path
            )

            # 2. OCR
            text = ocr_page_images(images, lang=lang)

            # 3. Save
            out_path = output_dir / f"{pdf_path.stem}{suffix}"
            out_path.write_text(text, encoding="utf-8")

            print(f"✓ OCR’d '{pdf_path.name}' → '{out_path.name}'")
        except Exception as exc:
            print(f"✗ Failed on '{pdf_path.name}': {exc}")


if __name__ == "__main__":
    extract_text_from_pdfs(
        input_dir="rag/raw_texts/pdfs",
        output_dir="rag/raw_texts/texts",
        dpi=600,           # bump to 400–600 for small print
        lang="eng",        # change or use "eng+deu" for multi-lingual
        # poppler_path="/usr/local/Cellar/poppler/24.04.0/bin",  # uncomment if needed
    )