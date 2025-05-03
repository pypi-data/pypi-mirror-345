#!/usr/bin/python3
"""
This is an ETL pipeline script that defines three classes(Extract, Transform, Load)
"""
import pandas as pd
import psycopg2
from sqlalchemy import URL
from sqlalchemy import create_engine
from tqdm import tqdm 


class Extract:
    """
    Class used to extract data from sources (PARQUET,)

    Methods:
        load_parquet(path): Loads a parquet file to a pandas data frame
    """
    @staticmethod
    def load_parquet(path:str):
        """
        Loads data from a parquet file to a pandas data frame

        Args:
            path(str): Path to the location of parquet file.

        Returns:
            df : A pandas data frame.

        Raises:
            FileNotFoundError: Error raised when wrong file path is submitted
            ImportError: Error raised when dependencies are not found
        """
        try:
            df = pd.read_parquet(path)
            df['created_at'] = pd.Timestamp.now()
            return df
        except FileNotFoundError:
            print(f'File {http://localhost:8888/tree?token=f56abbe7298ff9b18dd1cd187c162395bacf5d7a33b95929path} not found')
        except ImportError:
            print('Required parquet engine not installed (pyarrow or fastparquet)')
        except Exception as e:
            print(f'Error in reading parquet file: {e}')

class Transform:
    """
    Class used to transform extracted data

    Methods:
        remove_duplicates(df): Remove duplicates in the dataframe
        remove_blanks(): Handle blank fields in the dataframe
    """
    @staticmethod
    def remove_duplicates(df):
        """
        Removes duplicate rows from the dataframe

        Args:
            df(DataFrame): Data frame

        Returns:
            df: A processed data frame without duplicates

        Raises:
        AttributeError: If a wrong object is passed instead of a data frame.
        """
        try:
            new_df = df.drop_duplicates()
            return new_df
        except AttributeError:
            print('Error: Passed parameter is not a pandas dataframe')
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def remove_blanks(df):
        """
        Removes rows with columns that are empty

        Args:
            df(DataFrame): Data frame

        Returns:
            df: A processed data frame without blank columns

        Raises:
            AttributeError: If a wrong object is passed instead of a data frame.

        """
        try:
            new_df = df.dropna()
            return new_df
        except AttributeError:
            print('Error: Passed parameter is not a pandas dataframe')
        except Exception as e:
            print(f'Error: {e}')

class Load:
    """
    Class used to load data to various destinations.

    Methods:
        connect_postgres(): Connect to postgres DB
        write_to_db(): Write data to the database

    """
    @staticmethod
    def connect_postgres(database:str, host:str, user:str, password:str, port:int = 5432):
        """
        Connects to postgres database

        Args:
            database(str): database name
            host(str): host
            user(str): user
            password(str): password
            port(int): port (default=5432)
        
        Returns: A connection object

        Raises:
            ConnectionError: If passed args fails to create a connection to the database.

        """
        try:
            url_object = URL.create(
                "postgresql+psycopg2",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            engine = create_engine(url_object)
            return engine
        except ConnectionError as e:
            print(f'Failed to connect to the database: {e}')
        except Exception as e:
            print(f'Error occured while connecting to database: {e}')

    @staticmethod
    def write_to_db(df:pd.DataFrame, table_name:str, conn:object, chunk_size:int = 1000):
        """
        Writes dataframe to database

        Args:
            df(Data frame): Dataframe
            table_name(str): Table name
            conn(obj): Database connection object
        """
        try:
            # Create or replace schema/table
            df.head(0).to_sql(name=table_name, con=conn, if_exists='replace', index=False)
            print(f"Initialized table `{table_name}` in database.")

            # Write in chunks with feedback
            total_rows = len(df)
            print(f"Loading {total_rows} rows in chunks of {chunk_size}...")

            for i in tqdm(range(0, total_rows, chunk_size)):
                chunk = df.iloc[i:i+chunk_size]
                chunk.to_sql(name=table_name, con=conn, if_exists='append', index=False)
            
            print("✅ Successfully loaded dataframe to database.")
        except Exception as e:
            print(f'Error in loading dataframe to db: {e}')
