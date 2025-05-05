import requests
import psycopg2 
import pandas as pd 


class Extractor:
    @staticmethod
    def from_csv(file_path:str):
        ###Extract data from a CSV file
        return pd.read_csv(file_path)# converting to pandas df

    @staticmethod
    def from_api(url):
        ### Extract data from an API
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for bad responses
        return response.json()

    @staticmethod
    def from_db(database:str,query:str,user:str,password:str,host:str='localhost',port:str='5432'):
        ### Extract data from a PostgreSQL database
        db_connection =psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host,
            port=port) 
        data=pd.read_sql_query(query,db_connection)##reading data from db using pandas
        db_connection.close()
        return data