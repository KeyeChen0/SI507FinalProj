#read from 'cast_graph.json'
import json

with open('cast_graph.json', 'r') as f:
    cast_graph = json.load(f)
cast_graph = {k: set(v) for k, v in cast_graph.items()}

