import os.path
import shutil

from fastapi.testclient import TestClient

from text_extraction_service.services import app

fast_api_client = TestClient(app)


def test_health_service():
    resp = fast_api_client.get(url="/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_text_extraction_service():
    headers = {
        'accept': 'application/json',
    }
    params = {
        'minimum_chars_number': '20',
        'raw': 'false',
        'physical': 'false',
        'dpi': '200',
        'lang': 'eng+ita',
        'oem': '3',
        'psm': '3',
        'tessdata_dir': None,
        'thresholding_method': '0',
        'preserve_interword_spaces': '1',
    }
    file_b = "doc1_2.pdf"
    shutil.copyfile(src="doc1.pdf", dst=file_b)
    files = {
        'input_file': (file_b, open(file_b, 'rb'), 'application/pdf'),
    }
    resp = fast_api_client.post(url="/extract_text",
                                params=params,
                                headers=headers,
                                files=files)
    assert resp.status_code == 200
    assert resp.json()["file_name"] == file_b
    assert resp.json()["file_size_mb"] >= 0.1
    assert resp.json()["num_extracted_chars"] >= 500
    extracted_text = resp.json()["extracted_text"]
    assert extracted_text and isinstance(extracted_text, str)
    if os.path.isfile(file_b):
        os.remove(file_b)
