from urllib.parse import urljoin

root_url = {
    "portal": "https://portal.ustc.edu.cn",
    "id": "https://id.ustc.edu.cn",
    "bb": "https://www.bb.ustc.edu.cn",
}

def generate_url(website: str, path: str) -> str:
    return urljoin(root_url[website], path)
