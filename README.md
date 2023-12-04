# py-poppleract
Python library and Web service based on Poppler Pdftotext utility and Tesseract OCR  for extracting text from PDF documents

## Build and Run Dockerfile
```console
cd text-extraction-service/containers
docker build -t text-extraction-service:0.0.3 -f base.Dockerfile .
docker run -it --rm text-extraction-service:0.0.3 /bin/bash
```

## How to use programmatically text extractors

```python3
from text_extraction_service.text_extraction import (
    PdfToTextExtractor,
    TesseractPdfExtractor,
    PoppleractPdfExtractor
)

# === Poppler Pdftotext for machine-readable pdf === #
pdftotext_extr_obj = PdfToTextExtractor()
pdftotext_extr_obj.extract_text(
    in_pdf_file_path="doc1.pdf",
    out_txt_file_path="doc1a.txt",
    raw=False,
    physical=True
)

# === Tesseract OCR for NOT machine-readable pdf === #
tesseract_extr_obj = TesseractPdfExtractor(
    cache_folder="imgs/",
    preserve_cache=True
)
tesseract_extr_obj.extract_text(
    in_pdf_file_path="doc1.pdf",
    out_txt_file_path="doc1b.txt",
    dpi=200,
    lang="eng+ita",
    oem=3,
    psm=3,
    tessdata_dir="/usr/local/share/tessdata/",
    thresholding_method=0,
    preserve_interword_spaces=1
)

# === Hybrid Approach for mixed pdf: Pdftotext + Tesseract === #
hybrid_extr_obj = PoppleractPdfExtractor(
    cache_folder="imgs/",
    preserve_cache=True
)
hybrid_extr_obj.extract_text(
    in_pdf_file_path="doc1.pdf",
    out_txt_file_path="doc1c.txt",
    minimum_chars_number=20,
    raw=False,
    physical=False,
    dpi=200,
    lang="eng+ita",
    oem=3,
    psm=3,
    tessdata_dir="/usr/local/share/tessdata/",
    thresholding_method=0,
    preserve_interword_spaces=1
)
```


## How to use programmatically pdf splitter

```python3
from text_extraction_service.pdf_splitting import PdfSplitter

pdf_splitter_obj = PdfSplitter()
pdf_splitter_obj.split_pdf_to_images(
    in_pdf_file_path="doc1.pdf",
    out_images_directory_path="imgs/",
    dpi=200,
    img_exportation_format="png",
    use_pdf_to_cairo=True,
    first_page=1,
    last_page=3,
    output_file="page"
)
```
