import requests

BASE_URL = "http://127.0.0.1:5000/api"

print("Testing Product Catalog API...\n")

# Test 1: Get all categories
print("1. GET /products/categories")
response = requests.get(f"{BASE_URL}/products/categories")
print(f"Status: {response.status_code}")
print(f"Categories: {len(response.json())}")
print(f"Data: {response.json()}\n")

# Test 2: Get all products
print("2. GET /products/")
response = requests.get(f"{BASE_URL}/products/")
print(f"Status: {response.status_code}")
print(f"Products: {len(response.json())}")
for p in response.json()[:3]:
    print(f"  - {p['name']}: ${p['price']}")
print()

# Test 3: Filter by category
print("3. GET /products/?category_id=1")
response = requests.get(f"{BASE_URL}/products/?category_id=1")
print(f"Status: {response.status_code}")
print(f"Filtered Products: {len(response.json())}\n")

# Test 4: Search products
print("4. GET /products/?search=shirt")
response = requests.get(f"{BASE_URL}/products/?search=shirt")
print(f"Status: {response.status_code}")
print(f"Search Results: {len(response.json())}\n")

# Test 5: Get single product
print("5. GET /products/1")
response = requests.get(f"{BASE_URL}/products/1")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    product = response.json()
    print(f"Product: {product['name']} - ${product['price']}\n")

print("✅ All tests completed!")
