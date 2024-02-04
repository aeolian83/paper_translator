import requests
import json
import time


mathpix_url = "https://api.mathpix.com/v3/pdf"


# Mathpix functions
def call_mathpix_api(file, headers):
    options = {
        "conversion_formats": {"md": True},
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True,
        "enable_tables_fallback": True,
        "numbers_default_to_math": True,
    }

    r = requests.post(
        "https://api.mathpix.com/v3/pdf",
        headers=headers,
        data={"options_json": json.dumps(options)},
        files={"file": file},
    )
    return r


def call_convert_api(md_content, headers):
    url = "https://api.mathpix.com/v3/converter"
    payload = json.dumps(
        {
            "mmd": md_content,
            "formats": {
                "html": True,
            },
        }
    )
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def get_id(response, type="pdf"):
    """for pdf type="pdf"
    for md type="conversion"
    """
    r = json.loads(response.text.encode("utf8"))
    return r.get(type + "_id")


def check_status(id, headers, type="pdf"):
    """for pdf type="pdf"
    for md type="converter"
    """
    url = "https://api.mathpix.com/v3/" + type + "/" + id
    r = requests.get(url, headers=headers)
    r = json.loads(r.text.encode("utf8"))
    if type == "pdf":
        return r.get("status")
    elif type == "converter":
        return r.get("conversion_status")
    else:
        return None


def get_result(id, headers, type="pdf"):
    """for pdf type="pdf"
    for md type="converter"
    """
    if type == "pdf":
        url = "https://api.mathpix.com/v3/" + type + "/" + id + ".md"
    elif type == "converter":
        url = "https://api.mathpix.com/v3/" + type + "/" + id + ".html"
    response = requests.get(url, headers=headers)
    return response
