import pandas as pd

if __name__ == '__main__':
    extracted_df = pd.read_json('extracted_df.json')
    print(extracted_df.head())