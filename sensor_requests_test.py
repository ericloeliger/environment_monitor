import requests

url = 'http://192.168.0.184/temp'
r = requests.get(url, timeout=60)
response = r.text
print("Raw binary response: %s" % response.encode('utf-8'))