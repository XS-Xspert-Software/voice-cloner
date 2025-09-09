import requests

url = "http://127.0.0.1:8000/clone"
files = {"sample": open("record.wav", "rb")}
data = {"text": "Testing my cloned voice"}
r = requests.post(url, files=files, data=data)

with open("result.wav", "wb") as f:
    f.write(r.content)
