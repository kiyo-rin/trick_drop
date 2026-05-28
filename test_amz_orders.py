from sp_api.api import Orders
from sp_api.base import Marketplaces
import sys
import os
sys.path.append(os.path.abspath('.'))
from exports.amazon_sp_api_config import SP_API_CONFIG
import datetime

orders_api = Orders(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
created_after = (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()
print(f"Fetching from: {created_after}")
try:
    res = orders_api.get_orders(CreatedAfter=created_after, OrderStatuses=["Unshipped", "PartiallyShipped"])
    orders = res.payload.get("Orders", [])
    print(f"Got {len(orders)} unshipped orders.")
    if orders:
        items_res = orders_api.get_order_items(orders[0]['AmazonOrderId'])
        print(f"Order 0 items count:", len(items_res.payload.get('OrderItems', [])))
        print(items_res.payload.get('OrderItems')[0].get("Title"))
except Exception as e:
    print(str(e))

