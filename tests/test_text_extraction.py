import os

import pytest

from poppleract.text_extraction import (
    PdfToTextExtractor,
    TesseractPdfExtractor,
    PoppleractPdfExtractor,
    DocExtractorType
)


def check_file_content(fp: str, min_num_chars: int = 10):
    assert os.path.isfile(fp)
    with open(file=fp, mode="r", encoding="utf-8") as fr:
        content = fr.read()
        assert len(content) > min_num_chars


def check_cache_deletion(cache_dir_path: str, in_doc: str, preserve_flag: bool):
    if preserve_flag:
        assert len(os.listdir(cache_dir_path)) == 2
        doc_images_path = os.path.join(cache_dir_path, in_doc.rstrip('.pdf'))
        assert len(os.listdir(doc_images_path)) == 3
        assert all([img_p.endswith(".png") for img_p in os.listdir(doc_images_path)])
    else:
        assert len(os.listdir(cache_dir_path)) == 1


@pytest.mark.parametrize("input_pdf_doc, "
                         "output_txt_doc, "
                         "raw, "
                         "physical", [
                             ("doc1.pdf", "doc1_pdftotext1.txt", False, False),
                             ("doc1.pdf", "doc1_pdftotext2.txt", True, False),
                             ("doc1.pdf", "doc1_pdftotext3.txt", False, True),
                         ])
def test_pdftotext_extractor(input_pdf_doc: str,
                             output_txt_doc: str,
                             raw: bool,
                             physical: bool):
    pdftotext_extr_obj = PdfToTextExtractor()
    assert pdftotext_extr_obj.doc_extractor_type == DocExtractorType.MR
    pdftotext_extr_obj.extract_text(in_pdf_file_path=input_pdf_doc,
                                    out_txt_file_path=output_txt_doc,
                                    raw=raw,
                                    physical=physical)
    check_file_content(fp=output_txt_doc, min_num_chars=10)
    os.remove(output_txt_doc)


@pytest.mark.parametrize("input_pdf_doc, "
                         "output_txt_doc, "
                         "preserve_cache", [
                             ("doc1.pdf", "doc1_ocr1.txt", True),
                             ("doc1.pdf", "doc1_ocr2.txt", False),
                         ])
def test_ocr_extractor(input_pdf_doc: str,
                       output_txt_doc: str,
                       preserve_cache: bool):
    tesseract_extr_obj = TesseractPdfExtractor(cache_folder="imgs",
                                               preserve_cache=preserve_cache)
    assert tesseract_extr_obj.doc_extractor_type == DocExtractorType.OCR
    tesseract_extr_obj.extract_text(in_pdf_file_path=input_pdf_doc,
                                    out_txt_file_path=output_txt_doc,
                                    lang="eng+ita",
                                    oem=3,
                                    psm=3,
                                    dpi=200)
    check_file_content(fp=output_txt_doc, min_num_chars=10)
    check_cache_deletion(cache_dir_path="imgs", in_doc=input_pdf_doc, preserve_flag=preserve_cache)
    os.remove(output_txt_doc)


@pytest.mark.parametrize("input_pdf_doc, "
                         "output_txt_doc, "
                         "preserve_cache, "
                         "physical, "
                         "dpi", [
                             ("doc1.pdf", "doc1_hybrid1.txt", True, True, 120),
                             ("doc1.pdf", "doc1_hybrid2.txt", False, False, 180),
                         ])
def test_hybrid_extractor(input_pdf_doc: str,
                          output_txt_doc: str,
                          preserve_cache: bool,
                          physical: bool,
                          dpi: int):
    hybrid_extr_obj = PoppleractPdfExtractor(cache_folder="imgs",
                                             preserve_cache=preserve_cache)
    assert hybrid_extr_obj.doc_extractor_type == DocExtractorType.HYBRID
    hybrid_extr_obj.extract_text(in_pdf_file_path=input_pdf_doc,
                                 out_txt_file_path=output_txt_doc,
                                 minimum_chars_number=30,
                                 physical=physical,
                                 dpi=dpi,
                                 lang="eng")
    check_file_content(fp=output_txt_doc,
                       min_num_chars=10)
    check_cache_deletion(cache_dir_path="imgs",
                         in_doc=input_pdf_doc,
                         preserve_flag=preserve_cache)
    os.remove(output_txt_doc)
