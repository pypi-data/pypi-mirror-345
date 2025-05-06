import os
import sys
import logging
import subprocess
import pandas as pd
import pyodbc
import sqlite3
# import psycopg2
# import mysql.connector


class DatabaseType():
    MSSQL       = "MSSQL"
    POSTGRESQL  = "POSTGRESQL"
    MYSQL       = "MYSQL"
    SQLITE      = "SQLITE"


class Database():
    """
    Support for MSSQL and SQLite Exists.
    Support for PostgreSQL and MySQL likely to be added in the future.
    """

    def __init__(self, database:str=None, server:str=None, username:str=None, password:str=None, 
                 driver:str=None, host:str=None, port:int=None, sqlite_path:str=None,
                 db_type:DatabaseType=None,
                 connection_string:str=None, use_active_connection:bool=False, ignore:bool=False,
                 log_level=logging.INFO,
                 *args, **kwargs):
        """
        Args:
            database (str, optional): Database name. 
            server (str, optional): Server name. 
            username (str, optional): Username. 
            password (str, optional): Password. 
            driver (str, optional): Driver. 
            host (str, optional): Host.
            port (int, optional): Port.
            db_type (DatabaseType, optional): Database type. Defaults to DatabaseType.MSSQL.
            connection_string (str, optional): Connection string. 
            use_active_connection (bool, optional): Use active connection. Defaults to False.
            ignore (bool, optional): True to ignore asserts. Defaults to False.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logger(log_level)
        self.DATABASE = database
        self.SERVER   = server
        self.USERNAME = username
        self.PASSWORD = password
        self.DRIVER   = driver
        self.HOST     = host
        self.PORT     = port
        self.DB_TYPE  = db_type
        self.SQLITE_PATH = sqlite_path
        self.ignore   = ignore
        self.connection             = None  
        self.use_active_connection  = use_active_connection
        self._connection_string     = connection_string if connection_string else self.get_connection_string()
        self.connection             = self._open_connection() if self.use_active_connection else None

      
    def _setup_logger(self, log_level):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(name)s - %(message)s')
        handler.setFormatter(formatter)

        # Avoid duplicate logs if root logger already has handlers
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Don't bubble to root logger


    def get_connection_string(self):
        if self.DB_TYPE == DatabaseType.MSSQL:          return self.get_mssql_connection_string()
        elif self.DB_TYPE == DatabaseType.POSTGRESQL:   return self.get_postgresql_connection_string()
        elif self.DB_TYPE == DatabaseType.MYSQL:        return self.get_mysql_connection_string()
        elif self.DB_TYPE == DatabaseType.SQLITE:       return self.get_sqlite_connection_string()
        elif self.DB_TYPE is None:                      return self.get_mssql_connection_string()   # Default to MSSQL
        else:
            raise ValueError(f"Invalid database type: {self.DB_TYPE}")

    def get_mssql_connection_string(self):
        if not self.ignore:
            assert self.DATABASE, "Database name is required"
            assert self.SERVER,   "Server name is required"
            assert self.USERNAME, "Username is required"
            assert self.PASSWORD, "Password is required"
            assert self.DRIVER,   "Driver is required | Maybe try 'ODBC Driver 17 for SQL Server'"
        return f"DRIVER={self.DRIVER};SERVER={self.SERVER};DATABASE={self.DATABASE};UID={self.USERNAME};PWD={self.PASSWORD}"
    
    def get_postgresql_connection_string(self):
        if not self.ignore:
            assert self.DATABASE, "Database name is required"
            assert self.HOST,     "Host is required"
            assert self.PORT,     "Port is required"
            assert self.USERNAME, "Username is required"
            assert self.PASSWORD, "Password is required"
        return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
    
    def get_mysql_connection_string(self):
        if not self.ignore:
            assert self.DATABASE, "Database name is required"
            assert self.HOST,     "Host is required"
            assert self.PORT,     "Port is required"
            assert self.USERNAME, "Username is required"
            assert self.PASSWORD, "Password is required"
        return f"mysql+pymysql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
    
    def get_sqlite_connection_string(self):
        if not self.ignore:
            assert self.SQLITE_PATH, "SQLite database file path is required"
        return f"sqlite:///{self.SQLITE_PATH}"


    def _open_connection(self):
        if self.connection is not None:
            return self.connection
        try:
            
            if self.DB_TYPE == DatabaseType.MSSQL:
                self.connection = pyodbc.connect(self._connection_string)

            elif self.DB_TYPE == DatabaseType.POSTGRESQL:
                self.connection = pyodbc.connect(self._connection_string)

            elif self.DB_TYPE == DatabaseType.MYSQL:
                self.connection = pyodbc.connect(self._connection_string)

            elif self.DB_TYPE == DatabaseType.SQLITE:
                self.connection = sqlite3.connect(self.SQLITE_PATH)

            self.logger.info(f"Opened DB connection")

        except Exception as e:
            self.logger.error(f"Failed to open DB connection: {e}")
            return None
        return self.connection

    def close_connection(self, force=False):
        if self.connection is None:
            return
        if force or not self.use_active_connection:
            
            if self.DB_TYPE == DatabaseType.MSSQL:
                self.connection.close()

            elif self.DB_TYPE == DatabaseType.POSTGRESQL:
                self.connection.close()

            elif self.DB_TYPE == DatabaseType.MYSQL:
                self.connection.close()

            elif self.DB_TYPE == DatabaseType.SQLITE:
                self.connection.close()
            
            self.logger.info(f"Closed DB connection")
            self.connection = None
    
    def _is_connection_open(self):
        return self.connection is not None

    def __del__(self):
        self.close_connection(force=True)


    def run_query(self, query):
        conn = self._open_connection()
        if conn is None:
            self.logger.error("Failed to open connection")
            return pd.DataFrame()

        query_output_df = pd.read_sql_query(query, conn)
        self.close_connection()
        return query_output_df
        
    def run_execute(self, query):
        query = query.replace('"', '\\"')
        command = [
            "sqlcmd",
            "-S", self.SERVER,
            "-U", self.USERNAME,
            "-P", self.PASSWORD,
            "-d", self.DATABASE,
            "-Q", query
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True  # Raises CalledProcessError if exit code != 0
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"SQLCMD Error (code {e.returncode}): {e.stderr.strip()}")
            raise RuntimeError(f"SQLCMD Error (code {e.returncode}): {e.stderr.strip()}")

    def run_transaction(self, commands:list[str]):
        """ Order of commands is important. All commands run within 1 transaction. """ 
        status = False
        connection = self._open_connection()
        if connection is None:
            self.logger.error("Failed to open connection")
            return False
        cursor = connection.cursor()
        try:
            # Start a transaction
            connection.autocommit = False

            # Execute SQL statements within the transaction
            for command in commands:
                cursor.execute(command)

            # Commit the transaction
            connection.commit()
            status = True

        except Exception as e:
            # Rollback the transaction in case of an error
            self.logger.error(f"Error: {e}")
            connection.rollback()

        finally:
            # Close the database connection
            connection.autocommit = True
            self.close_connection()

        return status


    def create_database(self):
        try:
            if self.DB_TYPE == DatabaseType.MSSQL:
                return self._create_mssql_database()

            elif self.DB_TYPE == DatabaseType.POSTGRESQL:
                return self._create_postgresql_database()

            elif self.DB_TYPE == DatabaseType.MYSQL:
                return self._create_mysql_database()

            elif self.DB_TYPE == DatabaseType.SQLITE:
                return self._create_sqlite_database()

        except Exception as e:
            self.logger.error(f"Error creating database: {e}")
            return False
        
        return False

    def _create_mssql_database(self):
        try:
            conn_str = f'DRIVER={self.DRIVER};SERVER={self.SERVER};UID={self.USERNAME};PWD={self.PASSWORD};DATABASE=master'
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{self.DATABASE}') CREATE DATABASE [{self.DATABASE}];")
                return True
        except Exception as e:
            self.logger.error(f"Error creating MSSQL database: {e}")
            return False

    def _create_postgresql_database(self):
        try:
            conn_str = f'DRIVER={self.DRIVER};SERVER={self.HOST};UID={self.USERNAME};PWD={self.PASSWORD};PORT={self.PORT};DATABASE=postgres'
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = ?;", (self.DATABASE,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute(f"CREATE DATABASE {self.DATABASE};")
                return True
        except Exception as e:
            self.logger.error(f"Error creating PostgreSQL database: {e}")
            return False

    def _create_mysql_database(self):
        try:
            conn_str = f'DRIVER={self.DRIVER};SERVER={self.HOST};UID={self.USERNAME};PWD={self.PASSWORD};PORT={self.PORT};DATABASE=information_schema'
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.DATABASE}`;")
                return True
        except Exception as e:
            self.logger.error(f"Error creating MySQL database: {e}")
            return False

    def _create_sqlite_database(self):
        try:
            conn = sqlite3.connect(self.SQLITE_PATH)
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error creating SQLite database: {e}")
            return False





