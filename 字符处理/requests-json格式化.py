import requests
import json
import sys

url = sys.argv[1]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36','Connection': 'close'}
response = requests.get(url, headers=headers, timeout=30,verify=False)
res = response.json()
result = json.dumps(res, indent=4,ensure_ascii=False)
print(result)

with open("r.txt", "w", encoding="utf-8") as f:
    f.write(result)
