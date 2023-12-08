import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

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

if __name__ == '__main__':
    extracted_df = read_data_from_csv()
    print(extracted_df.head())
    extracted_df.head(100).to_json('extracted_df.json', orient='records')