# script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi[standard]",
#     "uvicorn",
#     "requests",
# ]
# ///
import requests
import os
import base64
from fastapi import FastAPI
from sympy import content
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
def validate_secret(secret: str):
    return secret == os.getenv("secret")
def create_github_repo(repo_name: str):
    #use api to create repo with the given name
    payload={"name": repo_name, 
            "private": False,
            "auto_init": True,
            "license_template": "mit"
            }
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json=payload
        )
    if response.status_code != 201:
        raise Exception(f"Failed to create repo: {response.status_code}, {response.text}")
    else:
        return response.json()

def enable_github_pages(repo_name: str):
    #takes repo name as argument and enables github pages on it
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload={
        "build_type": "legacy",
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    response = requests.post(
        f"https://api.github.com/repos/23f3001596-star/{repo_name}/pages",
        headers=headers,
        json=payload
        )
    if response.status_code != 201:
        raise Exception(f"Failed to create repo: {response.status_code}, {response.text}")
    else:
        return response.json()
def get_sha_of_latest_commit(repo_name: str, branch: str = "main") -> str:
    #takes repo name and branch name as argument and returns the sha of the latest commit on that branch
    response = requests.get(
        f"https://api.github.com/repos/23f3001596-star/{repo_name}/git/refs/heads/{branch}",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get latest commit: {response.status_code}, {response.text}")
    return response.json()["object"]["sha"]

def push_files_to_repo(repo_name: str, files: list[dict], round: int):
    if round == 2:
        latest_sha = get_sha_of_latest_commit(repo_name)
    else:
        latest_sha = None
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    for file in files:
        file_name = file.get("name")
        file_content = file.get("content")

        if not file_name or file_content is None:
            continue

        # Encode content to Base64 (strings or bytes)
        if isinstance(file_content, str):
            file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
        elif isinstance(file_content, bytes):
            file_content = base64.b64encode(file_content).decode("utf-8")
        else:
            raise ValueError("File content must be str or bytes")

        payload = {
            "message": f"Add {file_name}",
            "content": file_content
        }
        if latest_sha:
            payload["sha"] = latest_sha

        response = requests.put(
            f"https://api.github.com/repos/23f3001596-star/{repo_name}/contents/{file_name}",
            headers=headers,
            json=payload
        )
        if response.status_code not in [201, 200]:
            raise Exception(f"Failed to push file: {response.status_code}, {response.text}")
def write_code_with_llm():
    #hardcode with a single file for now
    # TODO: integrate with LLM to generate code based
    return [
        {"name": "index.html",
        "content": """
           <!DOCTYPE html>
           <html lang="en">
           <head>
           <meta charset="UTF-8">
           <meta name="viewport" content="width=device-width, initial-scale=1.0">
           <title>Hello World</title>
           </head>
           <body>
           <h1>Hello, World!</h1>
           <p>This is a test page pushed by LLM for round 1 for github pages deployment</p>
           </body>
           </html>
        """
        }
    ]
def round1(data):
    files=write_code_with_llm()
    #create_github_repo(f"{data['task']}_{data['nonce']}")
    #enable_github_pages(f"{data['task']}_{data['nonce']}")
    #push_files_to_repo(f"{data['task']}_{data['nonce']}", files, 1)

def round2():
    pass
app = FastAPI()

# post endpoint that takes a json object with following filed: email, secret, task, round, nonce,
# breif, checks(array), evaluation_url, attachments(array with object with fields name and url)
@app.post("/handle_task")
def handle_task(data: dict):
    # validate the secret
    if not validate_secret(data.get("secret", "")):
        return {"error": "Invalid secret"}
    else:
        #process the task
        #depending on the round field, call different functions
        if data.get("round") == 1:
            round1(data)
            return {"message": "Round 1 task started"}
        elif data.get("round") == 2:
            round2(data)
            return {"message": "Round 2 task started"}
        else:
            return {"error": "Invalid round"}
        
    return {"message": "Task received", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
