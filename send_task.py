# script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///

import requests

def send_task():
    payload = {
        "email": "student@example.com",
        "secret": "mysecretkey",
        "task": "captcha-solver-...",
        "round": 1,
        "nonce": "ab1-...",
        "brief": "Create a captive solver that handles furl=https://.../image.png Default to attached sam",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds",
            # ...
        ],
        "evaluation_url": "https://example.com/notify",
        "attachments": [ # attachments will be encoded as data URIs
            {"name": "sample.png", "url": "data:image/png;base64,iVBORw..."}
        ]
    }

    # The request is sent to the local FastAPI server
    response = requests.post("http://localhost:8000/handle_task", json=payload)
    print(response.text)

# Assuming this file would be executed to run the function:
if __name__ == "__main__":
    send_task()
