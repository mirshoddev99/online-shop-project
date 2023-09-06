import requests

endpoint = 'http://127.0.0.1:8000/api/product-list/'
data = requests.get(endpoint)
print(data.json())
