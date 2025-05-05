import json
from .github_manager import update_github_file,get_github_file

def get_stock_data(file_path, repo_owner, repo_name, github_token):
    """GitHub에서 주식 데이터를 불러오는 함수"""
    stock_data = json.loads(get_github_file(file_path, repo_owner, repo_name, github_token))
    return stock_data

def update_stock_data(file_path, repo_owner, repo_name, github_token, symbol, new_price):
    """주식 데이터 업데이트 및 GitHub에 반영하는 함수"""
    stock_data = get_stock_data(file_path, repo_owner, repo_name, github_token)

    if symbol not in stock_data:
        stock_data[symbol] = {"price": 0, "history": []}

    stock_data[symbol]["price"] = new_price
    stock_data[symbol]["history"].append(new_price)

    new_content = json.dumps(stock_data, ensure_ascii=False, indent=4)
    update_github_file(file_path, new_content, repo_owner, repo_name, github_token)
