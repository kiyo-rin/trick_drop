from sp_api.api import CatalogItems
from sp_api.base import Marketplaces
import sys, os
sys.path.append(os.path.abspath('.'))
from exports.amazon_sp_api_config import SP_API_CONFIG

ci = CatalogItems(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
res = ci.get_catalog_item("4490210531", includedData=["images"])
print("Images for 4490210531:")
print(res.payload.get("images"))
