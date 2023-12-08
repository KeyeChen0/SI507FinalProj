#read from 'crew_graph.json'
import json

with open('crew_graph.json', 'r') as f:
    crew_graph = json.load(f)
crew_graph = {k: set(v) for k, v in crew_graph.items()}