import requests

if __name__ == '__main__':
    headers = {
        'accept': 'application/json',
    }

    params = {
        'minimum_chars_number': '20',
        'raw': 'false',
        'physical': 'false',
        'dpi': '200',
        'lang': 'eng',
        'oem': '3',
        'psm': '3',
        'tessdata_dir': None,  # '/usr/local/share/tessdata/',
        'thresholding_method': '0',
        'preserve_interword_spaces': '1',
    }

    files = {
        'input_file': ('doc1.pdf', open('doc1.pdf', 'rb'), 'application/pdf'),
    }

    host = "0.0.0.0"
    port = 50000  # 8080
    response = requests.post(url=f"http://{host}:{port}/extract_text",
                             params=params,
                             headers=headers,
                             files=files)

    print(response.json())
    assert response.status_code == 200
