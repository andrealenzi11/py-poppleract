# py-poppleract
Python library and Web service based on **Poppler Pdftotext** utility and **Tesseract OCR** 
for extracting text from PDF documents.

Often, many pdf documents are of mixed type and contain:
- machine-readable pages from which text can be extracted with pdf rendering libraries;
- **not** machine-readable pages (images) from which text can only be extracted with OCR engines.

With this tool (**Poppleract**), you can extract text from mixed documents efficiently and easily .

## How to extract text from an input pdf through the web service

### Run the Poppleract services
Expose on the desired port (ex. 50000) the Poppleract services:
```console
docker run -it --rm -p 50000:8080 andrealenzi/poppleract-services:0.0.4
```

See the APIs documentation:
```url
http://0.0.0.0:50000/docs

http://0.0.0.0:50000/redoc
```

### Call the Text Extraction Service
Perform a **CURL** to extract text from the specified input pdf doc:
```console
curl -X 'POST' \
  'http://0.0.0.0:50000/extract_text?minimum_chars_number=20&raw=false&physical=false&dpi=200&lang=eng&oem=3&psm=3&thresholding_method=0&preserve_interword_spaces=1' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'input_file=@doc1.pdf;type=application/pdf'
```

Or perform a request with **Python**:
```python3
import requests

headers = {
    'accept': 'application/json'
}
params = {
    'minimum_chars_number': '20',
    'raw': 'false',
    'physical': 'false',
    'dpi': '200',
    'lang': 'eng',
    'oem': '3',
    'psm': '3',
    'tessdata_dir': None,
    'thresholding_method': '0',
    'preserve_interword_spaces': '1',
}
files = {
    'input_file': ('doc1.pdf', open('doc1.pdf', 'rb'), 'application/pdf')
}
response = requests.post(url='http://0.0.0.0:50000/extract_text',
                         params=params,
                         headers=headers,
                         files=files)
print(response.json())
```

Response body:
```json
{
  "file_name": "doc1.pdf", 
  "file_size_mb": 0.1771, 
  "num_extracted_chars": 762, 
  "extracted_text": "INTERNAL\n\nTEST DOC 1\nThis is a pdf document for test.\n\nThis page is machine-readable.\nThe second page of this document is NOT machine-readable, but it represents an image with text.\nThe third page of this document is again machine-readable.\n\nQwertyuiop\nAsdfghjkl\nZxcvbnm\n\nQWERTYUIOP\nASDFGHJKL\nZXCVBNM\n\n\x0c\n\n<END_PAGE>\n\nINTERNAL\n\nThis is a lot of 12 point text to test the\nocr code and see if it works on all types\nof file format.\n\nThe quick brown dog jumped over the\nlazy fox. The quick brown dog jumped\nover the lazy fox. The quick brown dog\njumped over the lazy fox. The quick\nbrown dog jumped over the lazy fox.\n\n\n<END_PAGE>\n\nINTERNAL\n\nThird and final page of this test document.\n\nQwertyuiop\nAsdfghjkl\nZxcvbnm\n\nQWERTYUIOP\nASDFGHJKL\nZXCVBNM\n\n<end of document>\n\n\x0c"
}
```

## How to use programmatically *PoppleractPdfExtractor*

```python3
"""
Hybrid Approach for extract text from mixed PDFs: 
Pdftotext on machine-readable pages + Tesseract OCR on images pages
"""
from text_extraction_service.text_extraction import PoppleractPdfExtractor

hybrid_extr_obj = PoppleractPdfExtractor(
    cache_folder="imgs/",  # Folder with doc images representing pages 
    preserve_cache=False  # Boolean flag for preserve the folder with doc images or not
)

hybrid_extr_obj.extract_text(
    in_pdf_file_path="doc1.pdf",  # Input pdf document path
    out_txt_file_path="doc1.txt",  # Output txt file path
    minimum_chars_number=20,  # For each page, we apply OCR only if we extract less than this threshold value 
    raw=False,  # Pdftotext parameter to keep strings in content stream order or not
    physical=False,  # Pdftotext parameter to maintain original physical layout or not
    dpi=200,  # Dots per Inch (DPI) used by Pdftocairo and Tesseract
    lang="eng+ita",  # Tesseract langs
    oem=3,  # Tesseract OCR Engine Mode 
    psm=3,  # Tesseract Page Segmentation Mode 
    tessdata_dir="/usr/local/share/tessdata/",  # Folder with Tesseract languages files
    thresholding_method=0,  # Tesseract parameter to perform automatic image thresholding
    preserve_interword_spaces=1  # Tesseract option to preserve spaces
)
```


## How to use programmatically *PdfSplitter*

```python3
"""
Splitting of an input pdf documents in the relative png pages
"""
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
    output_filename_prefix="page"
)
```
