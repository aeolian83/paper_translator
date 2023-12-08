import requests
import json
import time


headers={
    "app_id": "your mathpix app id",
    "app_key": "your mathpix app key"
}

def call_api(filename, headers):
    options = {
        "conversion_formats": {"md": True},
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True,
        "enable_tables_fallback": True,
    }

    r = requests.post("https://api.mathpix.com/v3/pdf",
        headers=headers,
        data={
            "options_json": json.dumps(options)
        },
        files={
            "file": open("./pdf/" + filename + ".pdf","rb")
        }
    )


    return r

def get_pdf_id(response):
    r = json.loads(response.text.encode("utf8"))
    return r.get("pdf_id")


def make_md(pdf_id, headers):
    start_time = time.time()
    url_1 = "https://api.mathpix.com/v3/pdf/" + pdf_id
    while time.time() - start_time < 60:
        r = requests.get(url_1, headers=headers)
        r = json.loads(r.text.encode("utf8"))
        if r.get("status") == "completed":
            print("OCR is done")
            break
        time.sleep(3)
        print(r.get("status"))

    
    url_2 = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".md"
    response = requests.get(url_2, headers=headers)
    with open("./markdown/" + pdf_id + ".md", "w") as f:
        f.write(response.text)
    
    