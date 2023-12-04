import os
import shutil
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence, Union, List

import pdftotext
from pytesseract import image_to_string

from text_extraction_service.pdf_splitting import PdfSplitter


class DocExtractorType(Enum):
    MR = "MachineReadable"
    OCR = "OpticalCharacterRecognition"
    HYBRID = "Hybrid"


class BasePdfExtractor(ABC):
    """
    Abstract PDF text extractor Base Class
    """

    def __init__(self,
                 pages_sep_token: str = "<END_PAGE>",
                 encoding: str = "utf-8"):
        """
        Parameters
        ----------
        pages_sep_token : str (optional)
            token used to separate pages, default to '<END_PAGE>'
        encoding : str (optional)
            text encoding, default to <utf-8>
        """
        self.pages_sep_token = pages_sep_token
        self.encoding = encoding
        self.doc_extractor_type: Optional[DocExtractorType] = None

    @abstractmethod
    def extract_text(self,
                     in_pdf_file_path: Union[str, Path],
                     out_txt_file_path: Union[str, Path],
                     **kwargs):
        """ Abstract method to implement """
        pass

    @staticmethod
    def _check_paths(in_pdf_file_path: Union[str, Path],
                     out_txt_file_path: Union[str, Path]):
        """ Check input path for pdf file and output path for txt file """
        assert os.path.isfile(in_pdf_file_path)
        assert in_pdf_file_path != out_txt_file_path
        directory_path = os.path.split(out_txt_file_path)[0]
        if directory_path == "":
            directory_path = os.getcwd()
        assert os.path.isdir(directory_path)

    def _merge_pages_contents(self, pages_contents: Sequence[str]) -> str:
        """ join the extracted pages contents """
        return f"\n\n{self.pages_sep_token}\n\n".join(pages_contents)

    def _store(self, content: str, out_txt_file_path: Union[str, Path]):
        """ Write content to the specified output txt file """
        with open(file=out_txt_file_path, mode="w", encoding=self.encoding) as fw:
            fw.write(content)


class MrPdfExtractor(BasePdfExtractor, ABC):
    """
    Abstract PDF text extractor Class for manage Machine Readable documents
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_extractor_type = DocExtractorType.MR


class NotMrPdfExtractor(BasePdfExtractor, ABC):
    """
    Abstract PDF text extractor Class for manage NOT Machine Readable documents
    """

    def __init__(self,
                 preserve_cache: bool = True,
                 cache_folder: Union[str, Path] = os.getcwd(),
                 **kwargs):
        """
        Parameters
        ----------
        preserve_cache : bool
            Boolean flag indicating whether to keep the cache folder with images or delete it at the end,
            default to True
        cache_folder : Union[str, Path]
            Cache folder path,
            default to current working directory
        """
        super().__init__(**kwargs)
        self.preserve_cache = preserve_cache
        self.cache_folder = cache_folder
        self.pdf_splitter_obj = PdfSplitter()
        self.doc_extractor_type = None
        if not os.path.isdir(self.cache_folder):
            raise NotADirectoryError("The specified 'cache_folder' must be an existing directory!")

    @staticmethod
    def _remove_extensions(file_name: Union[str, Path]) -> str:
        """ Remove for the given file name all the file extensions """
        file_name = Path(file_name)
        if file_name.suffixes:
            return file_name.name.split(file_name.suffixes[0])[0]
        else:
            return file_name.name

    def _create_images_folder(self, in_pdf_file_path: Union[str, Path]) -> str:
        """ Create images folder and return the associated path """
        file_name = os.path.split(in_pdf_file_path)[1]
        images_folder_name = self._remove_extensions(file_name=file_name)
        images_folder_path = os.path.join(self.cache_folder, images_folder_name)
        if not os.path.isdir(images_folder_path):
            os.mkdir(path=images_folder_path)
        return images_folder_path

    def _remove_cache_folder(self, images_folder_path: Union[str, Path]):
        """ Remove cache folder if field 'preserve_cache' is set to False """
        if not self.preserve_cache:
            shutil.rmtree(images_folder_path)


class OcrPdfExtractor(NotMrPdfExtractor, ABC):
    """
    Abstract PDF text extractor Class based on Optical Character Recognition Techniques
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_extractor_type = DocExtractorType.OCR


class HybridPdfExtractor(NotMrPdfExtractor, ABC):
    """
    Abstract PDF text extractor Class based on a hybrid approach:
    Machine Readable pdfs extraction and Optical Character Recognition Techniques
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.doc_extractor_type = DocExtractorType.HYBRID


class PdfToTextExtractor(MrPdfExtractor):
    """
    Class that represents a text extractor based on Poppler pdftotext library for Machine Readable PDFs.
    It's a wrapper of Python library `pdftotext <https://github.com/jalan/pdftotext>`.
    It's based on OS library `Poppler <https://poppler.freedesktop.org/>`.
    """

    def extract_text(self,
                     in_pdf_file_path: Union[str, Path],
                     out_txt_file_path: Union[str, Path],
                     raw: bool = False,
                     physical: bool = False):
        """
        Text Extraction from the input pdf document and writing to the output txt file

        Parameters
        ----------
        in_pdf_file_path : Union[str, Path]
            input path of the pdf document
        out_txt_file_path : Union[str, Path]
            output path of the txt file
        raw : bool (optional)
            boolean flag to keep strings in content stream order or not, default to False
        physical : bool (optional)
            boolean flag to maintain original physical layout or not, default to False
        """
        self._check_paths(in_pdf_file_path=in_pdf_file_path,
                          out_txt_file_path=out_txt_file_path)
        with open(file=in_pdf_file_path, mode="rb") as fr:
            pdf_pages = pdftotext.PDF(pdf_file=fr,
                                      raw=raw,
                                      physical=physical)
        result_str = self._merge_pages_contents(pages_contents=list(pdf_pages))
        self._store(content=result_str, out_txt_file_path=out_txt_file_path)
        del pdf_pages, result_str


class TesseractPdfExtractor(OcrPdfExtractor):
    """
     Class that represents a text extractor based on OCR system Tesseract for NOT Machine Readable PDFs.
     It's a wrapper of Python library `Pytesseract <https://github.com/madmaze/pytesseract>`.
     It's based on OCR system `Tesseract <https://github.com/tesseract-ocr/tesseract>`.
    """

    @staticmethod
    def _apply_ocr(images_folder_path: Union[str, Path],
                   lang: str,
                   tesseract_config: str) -> List[str]:
        all_texts = []
        for img_filename in sorted(os.listdir(images_folder_path)):
            img_path = os.path.join(images_folder_path, img_filename)
            assert os.path.isfile(img_path)
            extracted_text = image_to_string(image=img_path,
                                             lang=lang,
                                             config=tesseract_config)
            all_texts.append(extracted_text)
        return all_texts

    def extract_text(self,
                     in_pdf_file_path: Union[str, Path],
                     out_txt_file_path: Union[str, Path],
                     dpi: int = 200,
                     lang: str = "eng",
                     oem: int = 3,
                     psm: int = 3,
                     tessdata_dir: Optional[str] = None,
                     thresholding_method: int = 0,
                     preserve_interword_spaces: int = 1):
        """
        Text Extraction from the input pdf document and writing to the output txt file

        Parameters
        ----------
        in_pdf_file_path : Union[str, Path]
            input path of the pdf document
        out_txt_file_path : Union[str, Path]
            output path of the txt file
        dpi : int (optional)
            DPI for images, default to 200
        lang : str (optional)
            Tesseract OCR language, default to 'eng'
        oem : int (optional)
            Tesseract OCR Engine Modes, default to 3
        psm : int (optional)
            Tesseract Page Segmentation Modes, default to 3
        tessdata_dir : Optional[str] (optional)
            location of tessdata path (ex. '/usr/local/share/tessdata/'), default to None
        thresholding_method : int (optional)
            Tesseract binarization methods, default to 0
        preserve_interword_spaces : int (optional)
           Tesseract preserve spaces, default to 1
        """
        self._check_paths(in_pdf_file_path=in_pdf_file_path,
                          out_txt_file_path=out_txt_file_path)
        images_folder_path = self._create_images_folder(in_pdf_file_path=in_pdf_file_path)
        self.pdf_splitter_obj.split_pdf_to_images(in_pdf_file_path=in_pdf_file_path,
                                                  out_images_directory_path=images_folder_path,
                                                  dpi=dpi,
                                                  img_exportation_format="png",
                                                  use_pdf_to_cairo=True,
                                                  first_page=None,
                                                  last_page=None,
                                                  output_filename_prefix="pag")
        tesseract_config = f" -l {lang} " \
                           f"--oem {oem} " \
                           f"--psm {psm} " \
                           f"--dpi {dpi} " \
                           f"-c thresholding_method={thresholding_method} " \
                           f"-c preserve_interword_spaces={preserve_interword_spaces}"
        if tessdata_dir:
            tesseract_config = f"{tesseract_config} --tessdata-dir {tessdata_dir}"
        pages_contents = self._apply_ocr(images_folder_path=images_folder_path,
                                         lang=lang,
                                         tesseract_config=tesseract_config)
        result_str = self._merge_pages_contents(pages_contents=pages_contents)
        self._store(content=result_str, out_txt_file_path=out_txt_file_path)
        self._remove_cache_folder(images_folder_path=images_folder_path)
        del images_folder_path, tesseract_config, pages_contents, result_str


class PoppleractPdfExtractor(HybridPdfExtractor):
    """
     Class that represents a text extractor based on Poppler and Tesseract
     for manage mixed pdf (both machine-readable and not).
     It's based on pdftotext utility of `Poppler <https://poppler.freedesktop.org/>`.
     It's based on OCR system `Tesseract <https://github.com/tesseract-ocr/tesseract>`.
    """

    def extract_text(self,
                     in_pdf_file_path: Union[str, Path],
                     out_txt_file_path: Union[str, Path],
                     minimum_chars_number: int = 20,
                     raw: bool = False,
                     physical: bool = False,
                     dpi: int = 200,
                     lang: str = "eng",
                     oem: int = 3,
                     psm: int = 3,
                     tessdata_dir: Optional[str] = None,
                     thresholding_method: int = 0,
                     preserve_interword_spaces: int = 1):
        """
        Text Extraction from the input pdf document and writing to the output txt file

        Parameters
        ----------
        in_pdf_file_path : Union[str, Path]
            input path of the pdf document
        out_txt_file_path : Union[str, Path]
            output path of the txt file
        minimum_chars_number: int (optional)
            for each page: only if we extract less than this number of chars with Pdftotext, then we apply OCR.
            Default to 20
        raw : bool (optional)
            boolean flag to keep strings in content stream order or not, default to False
        physical : bool (optional)
            boolean flag to maintain original physical layout or not, default to False
        dpi : int (optional)
            DPI for images, default to 200
        lang : str (optional)
            Tesseract OCR language, default to 'eng'
        oem : int (optional)
            Tesseract OCR Engine Modes, default to 3
        psm : int (optional)
            Tesseract Page Segmentation Modes, default to 3
        tessdata_dir : Optional[str] (optional)
            location of tessdata path (ex. '/usr/local/share/tessdata/'), default to None
        thresholding_method : int (optional)
            Tesseract option to perform automatic image thresholding, default to 0
        preserve_interword_spaces : int (optional)
           Tesseract option to preserve spaces, default to 1
        """
        self._check_paths(in_pdf_file_path=in_pdf_file_path,
                          out_txt_file_path=out_txt_file_path)
        # === Initial Extraction with pdftotext === #
        with open(file=in_pdf_file_path, mode="rb") as fr:
            extracted_pages = pdftotext.PDF(pdf_file=fr,
                                            raw=raw,
                                            physical=physical)
            extracted_pages = list(extracted_pages)
        # === Split pdf in many images (one for page) === #
        images_folder_path = self._create_images_folder(in_pdf_file_path=in_pdf_file_path)
        self.pdf_splitter_obj.split_pdf_to_images(in_pdf_file_path=in_pdf_file_path,
                                                  out_images_directory_path=images_folder_path,
                                                  dpi=dpi,
                                                  img_exportation_format="png",
                                                  use_pdf_to_cairo=True,
                                                  first_page=None,
                                                  last_page=None,
                                                  output_filename_prefix="pag")
        imgs_pages = sorted([os.path.join(images_folder_path, fn)
                             for fn in sorted(os.listdir(images_folder_path))])
        # === Comparison among pages extracted from pdf and images pages === #
        if len(extracted_pages) != len(imgs_pages):
            raise ValueError("Number of extracted_pages is different from imgs_pages!")
        # === Applying OCR only on page in which we extracted fewer chars than the minimum === #
        tesseract_config = f" -l {lang} " \
                           f"--oem {oem} " \
                           f"--psm {psm} " \
                           f"--dpi {dpi} " \
                           f"-c thresholding_method={thresholding_method} " \
                           f"-c preserve_interword_spaces={preserve_interword_spaces}"
        if tessdata_dir:
            tesseract_config = f"{tesseract_config} --tessdata-dir {tessdata_dir} "
        result_pages = []
        for page_content, img_path in zip(extracted_pages, imgs_pages):
            # sufficient number of chars ---> use pdftotext output
            if page_content and len(page_content) >= minimum_chars_number:
                result_pages.append(page_content)
            # too few chars ---> apply OCR
            else:
                extracted_text = image_to_string(image=img_path,
                                                 lang=lang,
                                                 config=tesseract_config)
                result_pages.append(extracted_text)
                del extracted_text
        # === Final operations === #
        result_str = self._merge_pages_contents(pages_contents=result_pages)
        self._store(content=result_str, out_txt_file_path=out_txt_file_path)
        self._remove_cache_folder(images_folder_path=images_folder_path)
        del extracted_pages, images_folder_path, imgs_pages, tesseract_config, result_pages, result_str
