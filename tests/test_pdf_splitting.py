import os
import shutil
from typing import Optional

import pytest

from text_extraction_service.pdf_splitting import PdfSplitter


@pytest.mark.parametrize("input_pdf_doc, "
                         "output_imgs_dir, "
                         "use_pdf_to_cairo, "
                         "img_format, "
                         "first_page, "
                         "last_page", [
                             ("doc1.pdf", "imgs/doc1", True, "png", 1, 3),
                             ("doc1.pdf", "imgs/doc1", False, "ppm", None, None),
                         ])
def test_pdf_split1(input_pdf_doc: str,
                    output_imgs_dir: str,
                    use_pdf_to_cairo: bool,
                    img_format: str,
                    first_page: Optional[int],
                    last_page: Optional[int],
                    output_filename_prefix="pag"):
    pdf_splitter_obj = PdfSplitter()
    pdf_splitter_obj.split_pdf_to_images(in_pdf_file_path=input_pdf_doc,
                                         out_images_directory_path=output_imgs_dir,
                                         dpi=200,
                                         img_exportation_format=img_format,
                                         use_pdf_to_cairo=use_pdf_to_cairo,
                                         first_page=first_page,
                                         last_page=last_page,
                                         output_filename_prefix=output_filename_prefix)
    assert os.path.isdir(output_imgs_dir)
    pages = sorted(os.listdir(output_imgs_dir))
    print(pages)
    assert len(pages) == 3
    assert pages[0].startswith(output_filename_prefix) and pages[0].endswith(f"1.{img_format}")
    assert pages[1].startswith(output_filename_prefix) and pages[1].endswith(f"2.{img_format}")
    assert pages[2].startswith(output_filename_prefix) and pages[2].endswith(f"3.{img_format}")
    shutil.rmtree(output_imgs_dir)
