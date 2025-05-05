import requests ###Extracting data from API
import psycopg2 ##extracting data from database
import pandas as pd ##Extracting data from csv

class Transformer:
    @staticmethod
   # Remove duplicates
    def remove_duplicates(data:pd.DataFrame):
        return data.drop_duplicates()

        # Handle missing values (drop rows with missing values)
    @staticmethod
    def remove_missing(data:pd.DataFrame):
        return data.dropna()

        # Rename columns if provided
    @staticmethod
    def rename_columns(data:pd.DataFrame,columns:dict):
        return data.rename(columns=columns)

        # Convert date columns to datetime (if specified)
    @staticmethod
    def convert_datetime(data:pd.DataFrame,column:str):
        if column in data.columns:
            data[column] = pd.to_datetime(data[column], errors='coerce')

        return data

