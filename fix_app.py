import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_amazon_mercari = r'''# ① Amazonの注文判定
                        if '注文確定' in subject and 'amazon.co.jp' in from_addr.lower():
                            if not re.search(r'[:\s]YG', subject) and 'YG' not in body:
                                continue
                                
                            # メール本文から「商品：」などで行を分割して複数商品（合わせ買い）をすべて抽出する
                            blocks = re.split(r'(?:商品|商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
                            
                            # 万が一「商品：」で分割できなかった場合の救済措置
                            if len(blocks) <= 1:
                                blocks = ["", body]
                                
                            for block in blocks[1:]:
                                # SKUの抽出
                                sku_match = re.search(r'SKU(?:<[^>]*>)*[\s　]*(?:<[^>]*>)*[:：](?:<[^>]*>)*[\s　]*(?:<[^>]*>)*([A-Za-z0-9\-]+)', block)
                                if not sku_match:
                                    sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
                                    if not sku_match:
                                        # 件名からのフォールバック（分割できなかった単一注文などのため）
                                        sku_match_subj = re.search(r'(YG[A-Za-z0-9\-]+)', subject)
                                        if sku_match_subj and len(blocks) <= 2:
                                            sku = sku_match_subj.group(1).strip()
                                        else:
                                            continue
                                    else:
                                        sku = sku_match.group(1).strip()
                                else:
                                    sku = sku_match.group(1).strip()
                                    
                                if not sku.startswith('YG'):
                                    continue
                                
                                # 商品名の抽出 (ブロックの先頭)
                                product_name = ""
                                if len(blocks) > 1:
                                    p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r<]+)', block)
                                    if p_match:
                                        product_name = p_match.group(1).strip()
                                        
                                if not product_name:
                                    # 以前のフォールバック
                                    p_match = re.search(r'(?:商品|商品名)\s*[:：]\s*([^\n\r]+)', body)
                                    if p_match:
                                        product_name = p_match.group(1).strip()
                                    else:
                                        product_name = subject
                                        if '注文確定' in product_name:
                                            product_name = product_name.split('注文確定')[-1]
                                            
                                # 商品名クリーニング
                                product_name = re.sub(r'^\s*[\-\:]?\s*出品者出荷のご注文\s*[\-\:]?\s*', '', product_name)
                                product_name = re.sub(r'^[\s:\-]*', '', product_name)
                                product_name = re.sub(r'^(?:SKU\s*[:\-]?\s*)?[A-Za-z0-9\-_]+\s+', '', product_name)
                                product_name = re.sub(r'\s*\[Tankobon.*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'\s*\[JP Oversized.*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'\s*\[(?:単行本|文庫|ペーパーバック|大型本|新書)\].*', '', product_name)
                                product_name = re.sub(r'\s*\((?:単行本|文庫|ペーパーバック|大型本|新書)\).*', '', product_name)
                                product_name = re.sub(r'^[:：\s]*(?:SKU)?[:：\s]*YG[A-Za-z0-9\-]+[\s:：\-]*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'^[:：\-\s]+', '', product_name).strip()
                                product_name = re.sub(r'<[^>]+>', '', product_name).strip()
                                
                                # 数量の抽出
                                qty_match = re.search(r'数\s*量(?:<[^>]*>|[^0-9])*?([0-9]+)', block)
                                if qty_match:
                                    quantity_val = int(qty_match.group(1))
                                    if quantity_val > 1:
                                        quantity_display = f"🚨 {quantity_val}冊"
                                    else:
                                        quantity_display = "1"
                                else:
                                    idx = block.find('数')
                                    if idx != -1:
                                        debug_text = block[idx:idx+40].replace('\n', ' ')
                                        quantity_display = f"⚠️ {debug_text}"
                                    else:
                                        quantity_display = "⚠️ 本文に'数'が存在しません"
                                        
                                orders.append({
                                    "受信日時": formatted_date,
                                    "プラットフォーム": "📦 Amazon",
                                    "SKU": sku,
                                    "数量": quantity_display,
                                    "商品名": product_name.strip(),
                                    "ステータス": "🔴 未発注_八木"
                                })
                                
                        # ② メルカリShopsの注文判定
                        elif '【メルカリShops】' in subject:
                            if ('発送' in subject or '購入' in subject) and 'メッセージ' not in subject:
                                if 'YG' not in body and '商品管理コード : YG' not in body:
                                    continue
                                    
                                # メルカリも複数商品を考慮して分割
                                blocks = re.split(r'(?:商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
                                
                                if len(blocks) <= 1:
                                    blocks = ["", body]
                                    
                                for block in blocks[1:]:
                                    # SKUの抽出
                                    sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
                                    if not sku_match:
                                        if len(blocks) <= 2:
                                            sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', body)
                                            if not sku_match:
                                                continue
                                        else:
                                            continue
                                            
                                    sku = sku_match.group(1).strip()
                                    if not sku.startswith('YG'):
                                        continue
                                        
                                    p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r]+)', block)
                                    if p_match and len(blocks) > 1:
                                        product_name = p_match.group(1).strip()
                                    else:
                                        subj_match = re.search(r'「(.*?)」', subject)
                                        product_name = subj_match.group(1) if subj_match else subject.replace('【メルカリShops】', '')

                                    product_name = re.sub(r'<[^>]+>', '', product_name).strip()
                                    
                                    quantity_display = "1"
                                    
                                    orders.append({
                                        "受信日時": formatted_date,
                                        "プラットフォーム": "🔴 メルカリShops",
                                        "SKU": sku,
                                        "数量": quantity_display,
                                        "商品名": product_name,
                                        "ステータス": "🔴 未発注_八木"
                                    })
'''

# We want to replace from "# ① Amazonの注文判定" to the END of "ステータス\": \"🔴 未発注_八木\"\n                                })" inside the get_recent_orders loop.
# Let's find exactly the range:
import builtins
start_idx = content.find("# ① Amazonの注文判定")
if start_idx == -1:
    print("Could not find start")
    exit(1)
    
end_str = '"ステータス": "🔴 未発注_八木"\n                                })'
end_idx = content.find(end_str, start_idx)

if end_idx != -1:
    # replace till the end of the end_str
    actual_end = end_idx + len(end_str)
    new_content = content[:start_idx] + new_amazon_mercari + content[actual_end:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Replaced logic correctly")
else:
    print("Could not find end")
