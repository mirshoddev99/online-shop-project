import requests

endpoint = 'http://127.0.0.1:8000/api/crud-product/2/'
data = requests.get(endpoint)
print(data.json())
