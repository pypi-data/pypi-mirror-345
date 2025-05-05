import pandas as pd
import sqlalchemy
import json

class Loader:
    @staticmethod
    def to_csv(df: pd.DataFrame, file_path: str):
        try:
            df.to_csv(file_path, index=False)
            print(f"DataFrame successfully written to CSV at {file_path}")
        except Exception as e:
            print(f"Failed to write to CSV: {e}")
            raise

    @staticmethod
    def to_json(df: pd.DataFrame, file_path: str):
        try:
            df.to_json(file_path, orient='records', lines=True)
            print(f"DataFrame successfully written to JSON at {file_path}")
        except Exception as e:
            print(f"Failed to write to JSON: {e}")
            raise

    @staticmethod
    def to_db(df: pd.DataFrame, table_name: str, database: str, user: str, password: str,
              host: str = 'localhost', port: str = '5432', driver: str = 'postgresql'):
        try:
            engine = sqlalchemy.create_engine(
                f'{driver}://{user}:{password}@{host}:{port}/{database}'
            )
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            print(f"DataFrame successfully written to DB table '{table_name}'")
        except Exception as e:
            print(f"Failed to write to database: {e}")
            raise
