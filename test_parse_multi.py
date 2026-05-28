import re

body_amazon = '''
出荷予定日：2026/06/01
商品： ぷ損調[Tankobon Hardcover][1998]
コンディション： 新品
SKU： YG202505080950-100
数量： 1
価格： ￥ 1429

出荷予定日：2026/06/01
商品名： 月(絵本グリムの森4)
コンディション： 新品
SKU： NC20250629
数量： 2
'''

body_mercari = '''▼商品情報
注文番号 : order_2JRjXmHnSngunVJm4UF6bg
商品名 : ｃｒａｆｔ　ａｒｔ　ＤＯＬＬ　２０１６
商品管理コード : YG20250426161247446749-700-1760-3200
商品価格 : ¥2,429

商品名 : 他の本
商品管理コード : NC123
商品価格 : ¥1000
'''

def parse_amazon(body, subject, formatted_date):
    orders = []
    blocks = re.split(r'(?:商品|商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
    if len(blocks) <= 1:
        blocks = ["", body]
        
    for block in blocks[1:]:
        sku_match = re.search(r'SKU(?:<[^>]*>)*[\s　]*(?:<[^>]*>)*[:：](?:<[^>]*>)*[\s　]*(?:<[^>]*>)*([A-Za-z0-9\-]+)', block)
        if not sku_match:
            sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
            if not sku_match:
                sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', subject)
                if sku_match and len(blocks) <= 2:
                    pass
                else:
                    continue
        sku = sku_match.group(1).strip()
        if not sku.startswith('YG'):
            continue
            
        product_name = ""
        if len(blocks) > 1:
            p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r]+)', block)
            if p_match:
                product_name = p_match.group(1).strip()
                
        if not product_name:
            product_name = subject
                
        product_name = re.sub(r'<[^>]+>', '', product_name).strip()
        
        qty_match = re.search(r'数\s*量(?:<[^>]*>|[^0-9])*?([0-9]+)', block)
        if qty_match:
            quantity_val = int(qty_match.group(1))
            quantity_display = f"🚨 {quantity_val}冊" if quantity_val > 1 else "1"
        else:
            quantity_display = "⚠️ 本文に'数'が存在しません"
            
        orders.append({"SKU": sku, "Quantity": quantity_display, "Product": product_name})
    return orders

def parse_mercari(body, subject, formatted_date):
    orders = []
    blocks = re.split(r'(?:商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
    if len(blocks) <= 1:
        blocks = ["", body]
        
    for block in blocks[1:]:
        sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
        if not sku_match:
            if len(blocks) <= 2:
                sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', body)
            if not sku_match: continue
                
        sku = sku_match.group(1).strip()
        if not sku.startswith('YG'): continue
            
        p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r]+)', block)
        if p_match and len(blocks) > 1:
            product_name = p_match.group(1).strip()
        else:
            product_name = subject
            
        product_name = re.sub(r'<[^>]+>', '', product_name).strip()
        
        orders.append({"SKU": sku, "Quantity": "1", "Product": product_name})
    return orders

print("Amazon:", parse_amazon(body_amazon, "", ""))
print("Mercari:", parse_mercari(body_mercari, "", ""))
