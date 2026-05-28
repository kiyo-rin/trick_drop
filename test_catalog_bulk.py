from sp_api.api import CatalogItems
from sp_api.base import Marketplaces
import sys, os
sys.path.append(os.path.abspath('.'))
from exports.amazon_sp_api_config import SP_API_CONFIG

ci = CatalogItems(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
res = ci.search_catalog_items(identifiers=["4490210531", "4776212943"], identifiersType="ASIN", includedData=["images"])
print("Bulk images:", res.payload)
