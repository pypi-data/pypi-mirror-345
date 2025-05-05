import requests
import base64

def get_github_file(file_path, repo_owner, repo_name, github_token):
    """GitHub에서 파일 내용을 불러오고, 내용과 SHA를 반환"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        content = base64.b64decode(file_data['content']).decode('utf-8')
        sha = file_data['sha']
        return content, sha
    else:
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")

def update_github_file(file_path, new_content, repo_owner, repo_name, github_token, commit_message="Update stock data"):
    """GitHub 파일을 수정하고 푸시"""
    content, sha = get_github_file(file_path, repo_owner, repo_name, github_token)
    updated_content = base64.b64encode(new_content.encode()).decode()

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}
    payload = {
        "message": commit_message,
        "sha": sha,
        "content": updated_content,
    }

    response = requests.put(url, json=payload, headers=headers)
    if response.status_code in (200, 201):
        print("✅ GitHub 파일이 성공적으로 업데이트되었습니다.")
    else:
        raise Exception(f"❌ GitHub 파일 업데이트 실패: {response.status_code} - {response.text}")
