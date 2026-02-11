#!/bin/bash
BASE="http://127.0.0.1:5000/api"

echo "=== 1. GET ALL PRODUCTS ==="
curl -s "$BASE/products/" | python -m json.tool | head -15

echo -e "\n=== 2. GET CATEGORIES ==="
curl -s "$BASE/products/categories" | python -m json.tool

echo -e "\n=== 3. FILTER BY CATEGORY (T-Shirts, ID=15) ==="
curl -s "$BASE/products/?category_id=15" | python -m json.tool | grep -E '"name"|"category_name"' | head -6

echo -e "\n=== 4. FILTER BY PRICE (min=2000, max=5000) ==="
curl -s "$BASE/products/?min_price=2000&max_price=5000" | python -m json.tool | grep -E '"name"|"price"' | head -10

echo -e "\n=== 5. SEARCH BY NAME (search=jacket) ==="
curl -s "$BASE/products/?search=jacket" | python -m json.tool | grep -E '"name"' | head -5

echo -e "\n=== 6. GET SINGLE PRODUCT (ID=27) ==="
curl -s "$BASE/products/27" | python -m json.tool | grep -E '"name"|"price"|"category_name"'

echo -e "\n=== 7. COMBINED FILTERS (category=16, min_price=3000) ==="
curl -s "$BASE/products/?category_id=16&min_price=3000" | python -m json.tool | grep -E '"name"|"price"|"category_name"' | head -9

echo -e "\n✅ All endpoint tests completed!"
