from sp_api.api import Orders
from sp_api.base import Marketplaces
import sys
import os
sys.path.append(os.path.abspath('.'))
from exports.amazon_sp_api_config import SP_API_CONFIG
import datetime

orders_api = Orders(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
created_after = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
res = orders_api.get_orders(CreatedAfter=created_after, OrderStatuses=["Unshipped"])
orders = res.payload.get("Orders", [])

for o in orders[:5]:
    items = orders_api.get_order_items(o['AmazonOrderId']).payload.get("OrderItems", [])
    for it in items:
        asin = it.get("ASIN", "")
        print(f"SKU: {it.get('SellerSKU')} | ASIN: {asin} | Title: {it.get('Title')[:20]}")
