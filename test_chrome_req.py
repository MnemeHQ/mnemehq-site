import urllib.request

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/css,*/*;q=0.1',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Dest': 'style',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://mnemehq.com/audit/workspace/',
}

url = "https://mnemehq.com/audit/workspace/assets/index-wc1ltCA-.css"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        print("Response code:", resp.status)
        print("Headers:", resp.headers)
        print("Read len:", len(resp.read()))
except urllib.error.HTTPError as e:
    print("HTTPError code:", e.code)
    print("Headers:", e.headers)
    print("Body:", e.read()[:500])
except Exception as e:
    print("Other error:", e)