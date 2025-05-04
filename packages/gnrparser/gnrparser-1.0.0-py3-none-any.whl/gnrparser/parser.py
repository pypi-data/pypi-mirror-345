import re

def read(raw_data: str="") -> dict[dict, list]:
    tags_raw = re.findall(r'\[(.*?)\]', raw_data, flags=re.DOTALL)
    tags, moves = [], []

    for tag in tags_raw:
        try:
            parts = [x.strip() for x in tag.split(':', 1)]
            if re.match(r'^P\d+', parts[0]):
                parts[0] = re.match(r'(P\d+)', parts[0]).group(1)
            tags.append(parts)
        except:
            continue

    try:
        matched = re.findall(r'\s*(\d+\.)\s*(.*)', raw_data)
        for matching in matched:
            if not matching[1].strip().endswith(']'):
                move_list = matching[1].strip()
                moves_raw = re.split(r'\d+\.\s*', move_list)
                for move in moves_raw:
                    if move.strip():
                        moves.append(move.strip().split())
                break
    except:
        pass

    return {"data": dict(tags), "moves": moves}

def analyzer(data: dict={}) -> dict:
    analized = {"players": {1: "White", 2: "Black"}}

    for tag, value in data["data"].items():
        if tag.lower().startswith('p'):
            analized["players"][tag[1:]] = value

        elif tag.lower() == "start position":
            position = []
            for layer in value.split(':'):
                layer = layer.replace('/', '1empty')
                layer_processed = []
                layer_raw = re.findall(r'\d+[a-zA-Z]+', layer)
                for row in layer_raw:
                    count = re.findall(r'\d+', row)[0]
                    replaced_row = row.replace(count, '')
                    if replaced_row == "empty":
                        layer_processed.extend(['']*int(count))
                    else:
                        layer_processed.extend([replaced_row]*int(count))
                position.append(layer_processed)
            analized["position"] = position

        elif tag.lower() == "time limit":
            time_value = value.split('+') # ["base of time", "time addition"]
            condition = None if len(time_value) == 1 and time_value[0].lower() in ("null", "nil", "nan", "not", "none") else time_value
            analized["time_limit"] = condition

        elif tag.lower() == "date":
            analized["date"] = value.split('.') # Good only for DD:MM:YYYY format.

        elif tag.lower() == "field size":
            analized["size"] = [int(axis.strip()) for axis in value.split(',')]

        else:
            analized[tag.lower()] = value
    analized["moves"] = data["moves"]
    
    keys = {
        "version": 1,
        "game": "Unknown",
        "variation": "Standart",
        "termination": "",
        "date": "01.01.1970",
        "size": [8, 8],
        "time_limit": None,
        "organization": "Home Game",
        "position": [[], [], [], [], [], [], [], []],
        "moves": []
    }
    for key, default_value in keys.items():
        if key not in analized:
            analized[key] = default_value
    
    return analized

__all__ = ["read", "analyzer"]

if __name__ == "__main__":
    import sys
    import os

    if getattr(sys, 'frozen', False):
        DIR = os.path.dirname(sys.executable)
    else:
        DIR = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(os.path.dirname(DIR), "file.gnr"), 'r', encoding='utf-8') as file:
            DATA = file.read()
    except Exception as e:
        print(e)
    
    print(analyzer(read(DATA)))