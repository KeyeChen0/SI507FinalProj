import requests
import json
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')



def get_data_from_API(movie):
    """
    Fetch movie data from the OMDB API.

    This function checks if the movie data is already cached in 'cache.json'.
    If not, it fetches the data from the OMDB API and caches it.

    Parameters:
    movie (str): The title of the movie to fetch data for.

    Returns:
    dict: A dictionary containing movie data.
    """
    api_key = '44c2928e'
    if not os.path.exists('cache.json'):
        with open('cache.json', 'w') as f:
            json.dump({}, f)
    with open('cache.json', 'r') as f:
        data = json.load(f)
    if movie in data:
        return data[movie]
    else: 
        url = f'http://www.omdbapi.com/?t={movie}&apikey={api_key}'
        response = requests.get(url)
        new_data = response.json()
        data[movie] = new_data
        with open('cache.json', 'w') as f:
            json.dump(data, f)
        return new_data



def extract_genres(x):
    """
    Extract genres from a string representation of a list of dictionaries.

    Parameters:
    x (str): A string representation of a list of dictionaries, each containing a genre.

    Returns:
    list: A list of genres extracted from the input string.
    """
    genres = []
    for i in eval(x):
        genres.append(i['name'])
    return genres



def extract_crew(x):
    """
    Extract crew names from a string representation of a crew list.

    Parameters:
    x (str): A string representing a list of crew members in dictionary format.

    Returns:
    list: A list of extracted crew names.
    """
    crews = []
    for i in eval(x):
        crews.append(i['name'])
    return crews



def extract_cast(x):
    """
    Extract cast names from a string representation of a cast list.

    Parameters:
    x (str): A string representing a list of cast members in dictionary format.

    Returns:
    list: A list of extracted cast names.
    """
    casts = []
    for i in eval(x):
        casts.append(i['name'])
    return casts



def read_data_from_csv():
    """
    Read and preprocess movie data from CSV files.

    This function reads data from 'movies_metadata.csv' and 'credits.csv',
    merges them, and preprocesses the data for further analysis.

    Returns:
    DataFrame: A pandas DataFrame containing the processed movie data.
    """
    df_movie_metadata = pd.read_csv('movies_metadata.csv')
    df_credit = pd.read_csv('credits.csv')
    # Merge the dataframes using pd.concat
    total_df = pd.concat([df_movie_metadata, df_credit], axis=1)
    total_df['release_year'] = total_df['release_date'].apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
    extracted_df = total_df[['original_title', 'genres', 'cast', 'crew', 'release_year', 'overview']]
    extracted_df.dropna(subset=['original_title', 'genres'], inplace=True)
    extracted_df['original_title'] = extracted_df['original_title'].apply(lambda x: x.lower())
    extracted_df['genres'] = extracted_df['genres'].apply(extract_genres)
    extracted_df['crew'] = extracted_df['crew'].apply(extract_crew)
    extracted_df['cast'] = extracted_df['cast'].apply(extract_cast)
    return extracted_df



# generate genre dictionary, prepare for fuzzy search
def gen_genre_dic():
    """
    Generate a dictionary of genres for fuzzy search.

    This function creates a dictionary where each key is the first letter of a genre,
    and the value is a list of genres starting with that letter.

    Returns:
    tuple: A tuple containing the genre dictionary and a set of unique genres.
    """
    genres = set()
    for i in extracted_df['genres']:
        for j in i:
            genres.add(j)
    genre_dic = {}
    for genre in genres:
        first_letter = genre[0]
        if first_letter not in genre_dic:
            genre_dic[first_letter] = [genre]
        else:
            genre_dic[first_letter].append(genre)  
    return genre_dic, genres



#1 Single Movie Lookup
def single_movie_lookup(movie_name):
    """
    Look up a single movie in the dataset.

    If multiple movies with the same title are found, the user is asked to specify the release year.

    Parameters:
    movie_name (str): The title of the movie to look up.

    Returns:
    str or None: The overview of the movie if found, or None if not found.
    """
    movie_name = movie_name.lower()
    matching_movies = extracted_df[extracted_df['original_title'] == movie_name]
    if movie_name not in list(extracted_df['original_title']):
        print('Movie not found, please try again.')
        return
    elif len(matching_movies) > 1:
        print('Multiple movies found with the name "{}". Here are their release years:'.format(movie_name))
        for year in matching_movies['release_year'].unique():
            print(year)
        year = input('Enter the release year of the movie: ')  
        if year not in matching_movies['release_year'].unique():
            print('Year not found, please try again.')
            return
        return  matching_movies[matching_movies['release_year'] == year]['overview'].values[0]
    else:
        return matching_movies['overview'].values[0]



def get_required_genre_list():
    """
    Interactively collect a list of user's favorite genres.

    Continuously prompts the user to enter their favorite genres until they type 'stop'.
    Validates if the entered genre exists, offering suggestions if not.

    Returns:
    list: A list of user-specified genres.
    """
    genre_required = input('Enter your favorite genre: ')
    genre_list = []
    while genre_required != 'stop':
        while genre_required not in genres:
            if genre_required[0].upper() in genre_dic:
                print('Genre not found, do you mean {}'.format(genre_dic[genre_required[0].upper()]))
            else:
                print('Genre not found, please try again.')
            genre_required = input('Enter the genre: ')
        genre_list.append(genre_required)
        genre_required = input("Enter the genre (or enter 'stop' to stop): ")
    return genre_list



def relevant_score(list, row_list):
    """
    Calculate the relevance score based on the intersection of two lists.

    Parameters:
    list1 (list): The first list for comparison.
    list2 (list): The second list for comparison.

    Returns:
    int: The count of common elements between the two lists.
    """
    return len(set(list).intersection(set(row_list)))



def get_relevant_movies(genre_list):
    """
    Get movies relevant to the provided list of genres.

    Calculates a relevance score for each movie in the dataset based on the
    intersection of its genres with the input genre list. Returns the top 10 movies.

    Parameters:
    genre_list (list): A list of genres to compare against.

    Returns:
    None: Prints the top 10 relevant movies.
    """
    extracted_df['relevant_score'] = extracted_df['genres'].apply(lambda x: relevant_score(genre_list, x))
    extracted_df.sort_values(by=['relevant_score'], ascending=False, inplace=True)
    recommandtion =  pd.Series(extracted_df['original_title'].values).head(10)
    print('Here is the recommandation of the movie:')
    for i in range(len(recommandtion)):
        print(i+1, recommandtion[i])
    return



def get_movie_recommendation():
    """
    Recommend movies based on a user's favorite movie.

    Asks the user to enter a movie title, finds its genres, and then calls
    `get_relevant_movies` to fetch recommendations.

    Returns:
    None: Directly prints the recommendations.
    """
    mv_name = input('Enter your favorite movie: ').lower()
    if mv_name not in list(extracted_df['original_title']):
        print('Movie not found, please try again.')
        return
    genre_list = extracted_df[extracted_df['original_title']==mv_name]['genres'].values[0]
    get_relevant_movies(genre_list)
    return



def get_shortest_cast_path():
    """
    Find and print the shortest path between two actors in the movie dataset.

    Asks the user to enter the names of two actors and calculates the shortest
    path between them using the cast graph.

    Returns:
    None: Directly prints the shortest path or an error message.
    """
    actor1 = input('Enter the name of the first actor: ')
    actor2 = input('Enter the name of the second actor: ')
    if actor1 not in cast_graph.keys():
        print('Actor not found, please try again.')
        return
    if actor2 not in cast_graph.keys():
        print('Actor not found, please try again.')
        return
    path = shortest_path(cast_graph, actor1, actor2)
    if type(path) == str:
        print(path)
        return
    print('The shortest path between {} and {} is:'.format(actor1, actor2))
    print(' -> '.join(path[:-1]) + ' -> ' + path[-1] if len(path) > 1 else path[0])
    return



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



def bfs(graph, start):
    """
    Perform breadth-first search (BFS) on the graph starting from a given actor.

    Args:
    graph (dict): A graph representation where keys are actor names, and values
                  are sets of actors they have worked with.
    start (str): The name of the starting actor.

    Returns:
    list: A list containing the parent pointers, mean distance, and distance list.
    """
    visited = set()
    queue = [(start, None, 0)]  # Add a tuple of (vertex, parent) to the queue
    visited.add(start)
    distances = {start: 0}
    total_distance = 0  # Variable to store the sum of distances
    parent = {start: None}  # To store the parent of each vertex
    front = 0  # Index to keep track of the front of the queue

    while front < len(queue):
        vertex, prev, distance = queue[front]
        front += 1

        # Process the vertex and update the parent
        parent[vertex] = prev
        distances[vertex] = distance
        total_distance += distance
    
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                queue.append((neighbor, vertex, distance + 1))
                visited.add(neighbor)

        mean_distance = total_distance / len(distances)

    distance_list = []
    for i in distances.keys():
        distance_list.append(distances[i])    

    return [parent, round(mean_distance, 3), distance_list]



def shortest_path(graph, start, end):
    """
    Find the shortest path from a starting actor to Kevin Bacon in the graph.

    Uses breadth-first search (BFS) to traverse the graph and find the shortest path.

    Args:
    graph (dict): A graph representation where keys are actor names, and values
                  are sets of actors they have worked with.
    start (str): The name of the starting actor.
    end (str): The name of the target actor (Kevin Bacon).

    Returns:
    list or str: If a path exists, returns a list representing the shortest path.
                 If no path exists, returns a string indicating that the path does not exist.
    """
    parent = bfs(graph, start)[0]
    if end not in parent:
        return "Path does not exist."
    path = []
    curr = end
    # Reconstruct the path by following the parent pointers
    while curr is not None:
        # path.append('->')
        path.append(curr)
        curr = parent[curr]

    return path[::-1]  # Reverse the path to get it from start to end



def get_shortest_crew_path():
    """
    Find and print the shortest path between two crews in the movie dataset.

    Asks the user to enter the names of two crews and calculates the shortest
    path between them using the crew graph.

    Returns:
    None: Directly prints the shortest path or an error message.
    """
    crew1 = input('Enter the name of the first crew: ')
    crew2 = input('Enter the name of the second crew: ')
    if crew1 not in crew_graph.keys():
        print('Crew not found, please try again.')
        return
    if crew2 not in crew_graph.keys():
        print('Crew not found, please try again.')
        return
    path = shortest_path(crew_graph, crew1, crew2)
    if type(path) == str:
        print(path)
        return
    print('The shortest path between {} and {} is:'.format(crew1, crew2))
    print(' -> '.join(path[:-1]) + ' -> ' + path[-1] if len(path) > 1 else path[0])
    return



def get_correlation():
    """
    Calculate and print a correlation score between two movies.

    The score is based on the similarities in cast, crew, and genres of the two movies.
    Prompts the user to enter the names of two movies for comparison.

    Returns:
    None: Directly prints the correlation score.
    """
    movie1 = input('Enter the name of the first movie: ').lower()
    movie2 = input('Enter the name of the second movie: ').lower()
    if movie1 not in list(extracted_df['original_title']):
        print('Movie not found, please try again.')
        return
    if movie2 not in list(extracted_df['original_title']):
        print('Movie not found, please try again.')
        return
    cast1 = extracted_df[extracted_df['original_title']==movie1]['cast'].values[0]
    cast2 = extracted_df[extracted_df['original_title']==movie2]['cast'].values[0]
    crew1 = extracted_df[extracted_df['original_title']==movie1]['crew'].values[0]
    crew2 = extracted_df[extracted_df['original_title']==movie2]['crew'].values[0]
    genre1 = extracted_df[extracted_df['original_title']==movie1]['genres'].values[0]
    genre2 = extracted_df[extracted_df['original_title']==movie2]['genres'].values[0]
    cast_score = relevant_score(cast1, cast2)
    crew_score = relevant_score(crew1, crew2)
    genre_score = relevant_score(genre1, genre2)
    print('The correlation score between {} and {} is:'.format(movie1, movie2))
    total_score = cast_score + crew_score + genre_score
    total_score = total_score/3
    print(total_score)
    return



if __name__ == "__main__":
    extracted_df = read_data_from_csv()
    genre_dic, genres = gen_genre_dic()
    while True:
        print("\nThe program supports serveral functions: \n1. Single Movie Lookup \n2. Genre Based Recommendations \n3. Distance between Casts/Crews \n4. Correlation Analysis \n5. Exit")
        input_num = input('Please enter the number of the function you want to use: ')
        if input_num == '1':
            movie = input('Enter a movie title: ')
            if movie not in extracted_df['original_title'].values:
                new_data = get_data_from_API()
                #assign the new data to the dataframe
                extracted_df.loc[len(extracted_df)] = [new_data['Title'], new_data['Genre'].split(', '), new_data['Actors'].split(', '), new_data['Director'].split(', '), new_data['Year'], new_data['Plot']]
            print(single_movie_lookup(movie))
        elif input_num == '2':
            options = input('Do you want to search by genre or by movie title? (genre/title): ')
            if options == 'genre':
                get_relevant_movies(get_required_genre_list())
            elif options == 'title':
                if movie not in extracted_df['original_title'].values:
                    new_data = get_data_from_API()
                    #assign the new data to the dataframe
                    extracted_df.loc[len(extracted_df)] = [new_data['Title'], new_data['Genre'].split(', '), new_data['Actors'].split(', '), new_data['Director'].split(', '), new_data['Year'], new_data['Plot']]
                get_movie_recommendation()
        elif input_num == '3':
            cast_graph = build_graph('cast')
            crew_graph = build_graph('crew')
            options = input('Do you want to search by cast or by crew? (cast/crew): ')
            if options == 'cast':
                get_shortest_cast_path()
            elif options == 'crew':
                get_shortest_crew_path()
        elif input_num == '4':
            get_correlation()
        elif input_num == '5':
            print('Thank you for using our program!')
            exit()    