import json

with open('../data/isbn_sku_map.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sku_to_isbn = {}
for isbn, info in data.items():
    if "sku" in info:
        sku_to_isbn[info["sku"]] = isbn

with open('sku_to_isbn.json', 'w', encoding='utf-8') as f:
    json.dump(sku_to_isbn, f)

print(f"Items: {len(sku_to_isbn)}")
