import json, sys

with open('data.json', 'r') as f:
    data = json.load(f)
    print(data[str(input())])
