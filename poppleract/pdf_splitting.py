import os
from pathlib import Path
from typing import Union, Optional

from pdf2image import convert_from_path


class PdfSplitter:
    """
    Class to split a pdf document into images representing pages.
    It's a wrapper of Python library `pdf2image <https://github.com/Belval/pdf2image>`.
    It's based on OS library `Poppler <https://poppler.freedesktop.org/>`.
    """

    def __init__(self):
        self.obj_repr = f"{self.__class__.__name__}(id={id(self)})"

    def __str__(self) -> str:
        return self.obj_repr

    def __repr__(self) -> str:
        return self.obj_repr

    @staticmethod
    def _check_paths(in_pdf_file_path: Union[str, Path], out_images_directory_path: Union[str, Path]):
        """ Check input path for pdf file and output path for images directory """
        assert os.path.isfile(in_pdf_file_path)
        assert in_pdf_file_path != out_images_directory_path
        if not os.path.isdir(out_images_directory_path):
            father_directory_path = Path(out_images_directory_path).parent.absolute()
            assert os.path.isdir(father_directory_path)
            os.mkdir(out_images_directory_path)

    def split_pdf_to_images(self,
                            in_pdf_file_path: str,
                            out_images_directory_path: str,
                            dpi: int = 200,
                            img_exportation_format: str = "png",
                            use_pdf_to_cairo: bool = True,
                            first_page: Optional[int] = None,
                            last_page: Optional[int] = None,
                            output_filename_prefix: str = "pag",
                            **kwargs):
        """
        Split the specified input pdf document in many images (one for page) and
        save them in the specified output folder

        Parameters
        ----------
        in_pdf_file_path : str
            Path of the input pdf file
        out_images_directory_path : str
            Path of the output folder in which store the images
        dpi : int (optional)
            Image quality in DPI, defaults to 200
        img_exportation_format: str (optional)
            Format of the output images (ex. 'png', 'ppm', etc.), default to 'png '
        use_pdf_to_cairo : bool (optional)
            Boolean flag for choose the Poppler engine to use (pdftocairo instead of pdftoppm), default to True
        first_page : int (optional)
            First page to process, defaults to None
        last_page : int (optional)
            Last page to process, defaults to None
        output_filename_prefix: str (optional)
            prefixes of the output images, default to 'page'
        """
        self._check_paths(in_pdf_file_path=in_pdf_file_path,
                          out_images_directory_path=out_images_directory_path)
        convert_from_path(
            pdf_path=in_pdf_file_path,
            dpi=dpi,
            output_folder=out_images_directory_path,
            fmt=img_exportation_format,
            use_pdftocairo=use_pdf_to_cairo,
            first_page=first_page,
            last_page=last_page,
            output_file=output_filename_prefix,
            **kwargs
        )
