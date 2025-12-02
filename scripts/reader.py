import json
import pandas as pd
from pathlib import Path
import csv


def read_data(data_path):
    data_path = Path(data_path)
    
    if data_path.suffix == '.jsonl':
        format_type = 'jsonl'
    elif data_path.suffix == '.json':
        format_type = 'json'
    elif data_path.suffix == '.csv':
        format_type = 'csv'
    elif data_path.suffix == '.parquet':
        format_type = 'parquet'
    else:
        raise ValueError(f"Неизвестный формат файла: {data_path.suffix}")
    
    data = []
    
    if format_type == 'jsonl':
        with open(data_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
                    
    elif format_type == 'json':
        with open(data_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            
            if isinstance(data, dict) and "entities" in data:
                data = data["entities"]

            data_list = []
            for item in data:
                if item["text"]:
                    text = item["text"]
                    entities = [(start, end, label) for start, end, label in item["entities"]]
                    data_list.append((text, {"entities": entities}))
                else:
                    text = item["message"]
                    entities = [(start, end, label) for start, end, label in item["entities"]]
                    data_list.append((text, {"entities": entities}))

            return(data_list)
            
    elif format_type == 'csv':
        with open(data_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({"message": row["message"]})
            
    elif format_type == 'parquet':
        df = pd.read_parquet(data_path)
        for _, row in df.iterrows():
            item = {'message': row['message']}
            if 'entities' in row and pd.notna(row['entities']):
                if isinstance(row['entities'], str):
                    item['entities'] = eval(row['entities'])
                else:
                    item['entities'] = row['entities']
            data.append(item)
    
    return data
