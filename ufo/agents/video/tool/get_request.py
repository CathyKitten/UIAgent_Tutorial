import re

def extract_request_from_md(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式提取 request 字段内容
    match = re.search(r'- \*\*request\*\*: (.+)', content)
    if match:
        return match.group(1).strip()
    else:
        return None