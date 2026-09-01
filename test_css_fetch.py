import urllib.request

url = "https://mnemehq.com/audit/workspace/assets/index-wc1ltCA-.css"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Headers:", response.headers)
        content = response.read(200)
        print("Content prefix:", content)
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print("Headers:", e.headers)
    print("Body prefix:", e.read()[:200])
except Exception as e:
    print("Error:", e)