import pandas as pd
import json
import os
import re

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import get_recent_orders

try:
    df = get_recent_orders()
    if not df.empty:
        df['販売数_buggy'] = df['数量'].astype(str).str.extract(r'(\d+)').astype(float).fillna(1).astype(int)
        df['販売数_fixed'] = df['数量'].astype(str).str.extract(r'(\d+)', expand=False).astype(float).fillna(1).astype(int)
        print("Buggy dtypes:\n", df['販売数_buggy'].dtypes)
        print("Fixed dtypes:\n", df['販売数_fixed'].dtypes)
        print("Buggy sum:", df['販売数_buggy'].sum())
        print("Fixed sum:", df['販売数_fixed'].sum())
        print(df['販売数_buggy'].head())
    else:
        print("Empty DF")
except Exception as e:
    print(e)
