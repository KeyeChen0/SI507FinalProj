import extrected_df_construction_code as edfcc
import json

def build_graph(column):
    """
    Build a graph representing connections between actors based on movie casts.

    Reads data from a file and constructs a graph where each actor is a node,
    and the edges represent collaborations in movies.

    Returns:
    graph (dict): A dictionary where keys are actor names, and values are sets
                  of actors they have worked with.
    """
    uniqname = []
    film_actor = []
    for i in range(len(extracted_df)):
        film_actor.append(extracted_df.iloc[i][column])
        uniqname.extend(extracted_df.iloc[i][column])  
            
    uniqname = list(set(uniqname))            
    graph = {}.fromkeys(uniqname, set())
    for array in film_actor:
        for name in array:
            graph[name] = graph[name] | set(array)

    return graph


if __name__ == '__main__':
    extracted_df = edfcc.read_data_from_csv()
    crew_graph = build_graph('crew')
    #select the first 1000 crews
    crew_graph = {k: crew_graph[k] for k in list(crew_graph)[:1000]}
    # print the graph to 'crew_graph.json'
    with open('crew_graph.json', 'w') as f:
        json.dump({k: list(v) for k, v in crew_graph.items()}, f)