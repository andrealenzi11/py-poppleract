import gc
import json
import logging
import os
import shutil
import sys
import traceback
from pathlib import Path
from typing import Union, Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from starlette.responses import JSONResponse

from poppleract.text_extraction import PoppleractPdfExtractor

SERVICES_HOST = "0.0.0.0"
SERVICES_PORT = 8080


class TextResponse(BaseModel):
    file_name: str
    file_size_mb: float
    num_extracted_chars: int
    extracted_text: str


class ErrorResponse(BaseModel):
    error: str
    stack_trace: str


# ===== Define Logger ===== #
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)
# ========================= #

# ===== Read version ========= #
with open(file=os.path.join(Path(os.getcwd()).parent, "version.json"), mode="r", encoding="utf-8") as fr1:
    VERSION = str(json.load(fr1)["version"])
logger.info(f">>>>> app version: {str(VERSION)} \n")
# ============================= #

# ===== FastAPI app ===== #
app = FastAPI(
    title="Poppleract-Services",
    description="A set of APIs for extract text from a mixed pdf document",
    version=VERSION,
    logger=logger,
)
# ======================= #

# ===== Poppleract Extractor ===== #
CACHE_IMG_FOLDER = "imgs"
if not os.path.isdir(CACHE_IMG_FOLDER):
    os.mkdir(CACHE_IMG_FOLDER)
hybrid_extr_obj = PoppleractPdfExtractor(cache_folder=CACHE_IMG_FOLDER,
                                         preserve_cache=False)
# ================================== #


@app.get("/")
def read_root() -> JSONResponse:
    """ This service reads the application root path and returns a welcome message """
    return JSONResponse(content={"message": f"text-extraction-service ({VERSION}) root page!"}, status_code=200, )


@app.get("/version")
def version() -> JSONResponse:
    """ This service returns the application version """
    return JSONResponse(content={"version": str(VERSION)}, status_code=200)


@app.get("/health")
def health() -> JSONResponse:
    """ Health service """
    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.post(
    path="/extract_text",
    response_model=TextResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Unprocessable Entity"},
        404: {"model": ErrorResponse, "description": "File Not Found"},
        500: {"model": ErrorResponse, "description": "Generic Server Error"},
    },
)
async def extract_text(
        minimum_chars_number: int = 20,
        raw: bool = False,
        physical: bool = False,
        dpi: int = 200,
        lang: str = "eng",
        oem: int = 3,
        psm: int = 3,
        tessdata_dir: Optional[str] = None,  # "/usr/local/share/tessdata/",
        thresholding_method: int = 0,
        preserve_interword_spaces: int = 1,
        input_file: UploadFile = File(...),
) -> Union[TextResponse, JSONResponse]:
    """
    Text Extraction Service
    - **input**: pdf input file
    - **output**: extracted text
    """
    pdf_file_path, txt_file_path, content = None, None, None
    try:
        logger.info(f"- input_filename: '{input_file.filename}'")
        file_size = round(input_file.size / 1000 / 1000, 4)
        logger.info(f"- file size: '{file_size} MB'")

        # ===== Store input file to local File System ====== #
        pdf_file_path = Path(os.path.join(os.getcwd(), input_file.filename))
        try:
            with pdf_file_path.open("wb") as buffer:
                shutil.copyfileobj(input_file.file, buffer)
        finally:
            input_file.file.close()

        # ===== Text Extraction ====== #
        if pdf_file_path.suffixes:
            txt_file_path = f"{pdf_file_path.name.split(pdf_file_path.suffixes[0])[0]}.txt"
        else:
            txt_file_path = f"{pdf_file_path.name}.txt"
        hybrid_extr_obj.extract_text(in_pdf_file_path=pdf_file_path,
                                     out_txt_file_path=txt_file_path,
                                     minimum_chars_number=minimum_chars_number,
                                     raw=raw,
                                     physical=physical,
                                     dpi=dpi,
                                     lang=lang,
                                     oem=oem,
                                     psm=psm,
                                     tessdata_dir=tessdata_dir,
                                     thresholding_method=thresholding_method,
                                     preserve_interword_spaces=preserve_interword_spaces)
        with open(file=txt_file_path, mode="r", encoding="utf-8") as fr:
            content = fr.read()
            logger.info(f"- num extracted chars: {len(content)} \n")

        # ====== Deletion of files and return of response with extracted text ===== #
        os.remove(pdf_file_path)
        os.remove(txt_file_path)
        return TextResponse(
            file_name=input_file.filename,
            file_size_mb=file_size,
            num_extracted_chars=len(content),
            extracted_text=content
        )
    except (ValueError, TypeError) as ex:
        return JSONResponse(
            status_code=422,  # Un-processable Entity
            content=dict(ErrorResponse(error=str(ex), stack_trace=str(traceback.format_exc()))),
        )
    except FileNotFoundError as ex:
        return JSONResponse(
            status_code=404,  # File Not Found
            content=dict(ErrorResponse(error=str(ex), stack_trace=str(traceback.format_exc()))),
        )
    except Exception as ex:
        logger.error("Error in 'text_extraction' service!", exc_info=True)
        return JSONResponse(
            status_code=500,  # General Server Error
            content=dict(ErrorResponse(error=str(ex), stack_trace=str(traceback.format_exc()))),
        )
    finally:
        del minimum_chars_number, raw, physical, dpi, lang, oem, psm, \
            tessdata_dir, thresholding_method, preserve_interword_spaces, \
            input_file, file_size, pdf_file_path, txt_file_path, content
        gc.collect()


if __name__ == "__main__":
    # Set Uvicorn logger
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s  %(process)d  %(thread)d  %(levelprefix)s  %(message)s"
    # Run Uvicorn Asynchronous Server Gateway Interface (ASGI) server
    uvicorn.run(
        app="services:app",
        host=str(SERVICES_HOST),
        port=int(SERVICES_PORT),
        log_level="info",
        log_config=log_config,
        use_colors=True,
        access_log=False,
        timeout_keep_alive=30,  # 5
        workers=1,
    )
