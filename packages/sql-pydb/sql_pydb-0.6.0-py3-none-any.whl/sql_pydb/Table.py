import os
import sys
import pandas as pd
import numpy as np
import logging

from sql_pydb.Database import Database
from sql_pydb.Column import Column
from sql_pydb.Cell import clean_value_with_type, infer_sql_type_from_value, determine_final_type
from sql_pydb.TableCommands import TableCommands


class TableActions(Database):
    
    def __init__(self, database:str, table_name:str, log_level=logging.INFO, *args, **kwargs):
        super().__init__(database, log_level=log_level, *args, **kwargs)
        self.DATABASE   = database
        self.TABLE      = table_name
        self.user_schema= {
            # "COLUMN_1_NAME": Column("COLUMN_1_NAME", "VARCHAR", 255),
            # ...
        }
        self.db_table_column_schema_df = pd.DataFrame()
        self.db_schema  = {
            # "COLUMN_1_NAME": Column("COLUMN_1_NAME", "VARCHAR", 255),
            # ...
        }
        self.get_db_table_schema()  # TODO: Should we have this here?
        self.NULL_ITEMS = [None, np.nan, pd.NaT]    # Additional Types: "#N/A", 'NA'
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logger(log_level)
      
    def _setup_logger(self, log_level):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(name)s - %(message)s')
        handler.setFormatter(formatter)

        # Avoid duplicate logs if root logger already has handlers
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Don't bubble to root logger


    def schema_df_to_objects(self, df):
        if isinstance(df, list):
            return df
        if not isinstance(df, pd.DataFrame):
            return []

        must_have_columns = ["COLUMN", "DATA_TYPE", "SIZE"]
        for column in must_have_columns:
            if column not in list(df.columns):
                return []
        column_objs = []
        for i, row in df.iterrows():
            database    = row["DATABASE"] if "DATABASE" in row else self.DATABASE
            table       = row["TABLE"]    if "TABLE"    in row else self.TABLE
            column_obj  = Column(column_name=row["COLUMN"], data_type=row["DATA_TYPE"], 
                                        size=row["SIZE"],
                                        database=database,
                                        table=table)
            column_objs.append(column_obj)
        return column_objs

    def identify_schema(self, df, user_schema_records:list[object]=[]):
        """
        user_schema_records can either be...
            1. List of Columns or
            2. DataFrame that contains columns COLUMN_NAME, DATA_TYPE, SIZE
        Schema Identification Priority
            1: Use user defined Schema first if given
            2. Then use the DB existing Schema if exists
            3. Identify schema based on column values
        """

        user_schema_records = self.schema_df_to_objects(user_schema_records)

        self.get_db_table_schema()
        self.user_schema = {}

        for column in list(df.columns):
            # 1: Use user defined Schema first
            user_column_info = None
            for user_column in user_schema_records:
                if user_column.DATABASE and user_column.DATABASE != self.DATABASE:
                    continue
                if user_column.TABLE and user_column.TABLE != self.TABLE:
                    continue
                if user_column.COLUMN == column:
                    user_column_info = user_column
                    break
            if user_column_info:
                column_obj = Column(column, data_type=user_column_info.DATA_TYPE, 
                                           size=user_column_info.SIZE,
                                           database=self.DATABASE,
                                           table=self.TABLE)
                self.user_schema[column] = column_obj
                # print(f"{column} | USER")
                continue

            # 2. Then use the DB existing Schema
            db_column_info = None
            for db_column_name, column_obj in self.db_schema.items():
                if db_column_name == column:
                    db_column_info = column_obj
                    break
            if db_column_info:
                column_obj = Column(column, data_type=db_column_info.DATA_TYPE, 
                                           size=db_column_info.SIZE,
                                           database=self.DATABASE,
                                           table=self.TABLE)
                self.user_schema[column] = column_obj
                # print(f"{column} | DB")
                continue

            # 3. Identify schema based on column values
            inferred_types = set()
            for value in df[column]:
                value = str(value)
                if type(value) == str:
                    value = value.replace("NULL", "").replace("null", "")
                    value = value.replace("nan", "").replace("NAN", "")
                inferred_types.add(infer_sql_type_from_value(str(value)))
            column_type = determine_final_type(inferred_types, column_name=column)
            column_obj = Column(column, data_type=column_type, database=self.DATABASE, 
                                       table=self.TABLE)
            self.user_schema[column] = column_obj
            # print(f"{column} | PROGRAM")

        return self.user_schema

    def get_db_table_schema(self):
        command = self.generate_schema_table_sql()
        self.db_table_column_schema_df = self.run_query(command)
        # print(self.db_table_column_schema_df)
        for i, row in self.db_table_column_schema_df.iterrows():
            column_name = row.get("COLUMN_NAME") if row.get("COLUMN_NAME")  else row.get("name")
            data_type   = row.get("DATA_TYPE")   if row.get("DATA_TYPE")    else row.get("type")
            size        = row.get("SIZE")

            if "VARCHAR" in data_type or "NVARCHAR" in data_type:
                data_type = data_type.split("(")[0]     # Sometimes it's NVARCHAR(255) or VARCHAR(255)
                if len(data_type.split("(")) > 1:
                    size = int(data_type.split("(")[1].split(")")[0])
                
            column_obj = Column(column_name, data_type=data_type, 
                                           size=size,
                                           database=self.DATABASE,
                                           table=self.TABLE)
            self.db_schema[column_name] = column_obj
        return self.db_table_column_schema_df


    def insert_df(self, df, batch=None):
        commands = [""]
        if not batch:
            commands = [self.generate_insert_sql(df)]
        else:
            commands = [self.generate_insert_sql(df[i:i+batch]) for i in range(0, len(df), batch)]
        return self.run_transaction(commands)


    def sync_schema(self, update_column_types:bool=True, add_new_columns:bool=True, delete_old_columns:bool=False):
        """
        Has ability to do the following: 
        0. Create the table if it doesn't exist
        1. Update the column types that don't match in DB and preserve the data.
        2. ADD any new columns the DB doesn't have
        3. DELETE any old columns that the source does not have. (FOR ETL PROCESSES)
        """
        if len(self.db_table_column_schema_df) == 0:
            self.logger.warning(f"Need to create table {self.DATABASE}.{self.TABLE}")
            command = self.generate_create_table_sql()
            self.run_transaction([command])
            return
        
        status1, status2, status3 = True, True, True
        
        if update_column_types: # 1: UPDATE COLUMN TYPES
            status1 = self.update_column_types()

        if add_new_columns:     # 2. ADD NEW COLUMNS
            status2 = self.add_new_columns()

        if delete_old_columns:  # 3. DELETE OLD COLUMNS
            status3 = self.delete_old_columns()

        return status1 and status2 and status3

    def update_column_types(self):
        columns_to_update = []
        for column, column_obj in self.user_schema.items():
            if self.db_schema.get(column) and column_obj != self.db_schema.get(column):
                columns_to_update.append(column_obj)
                self.logger.info(f"""UPDATE Column {self.DATABASE}.{self.TABLE}.{column} to {column_obj.DATA_TYPE} SIZE({column_obj.SIZE})""")

        status = True
        for column_obj in columns_to_update:
            # Try cast first, if 0 records found, then actually cast. 
            query = self.generate_column_try_cast_sql(column_name=column_obj.COLUMN, column_type=column_obj.DATA_TYPE)
            df = self.run_query(query)
            if len(df) > 0:
                self.logger.warning(f"WARNING: TRY CAST Column '{column_obj.COLUMN}' to {column_obj.DATA_TYPE} SIZE({column_obj.SIZE}). Failed try cast rows: \n{df}")
                status = status & False
                continue
            command = self.generate_modify_column_type_sql(column_name=column_obj.COLUMN, column_type=column_obj.get_sql_type())
            status_temp = self.run_transaction([command])
            if not status_temp:
                self.logger.error(f"ERROR: UPDATE Column '{column_obj.COLUMN}' to {column_obj.DATA_TYPE} SIZE({column_obj.SIZE}) | {command}")
            status = status & status_temp
        return status

    def add_new_columns(self):
        new_columns = []
        for column, column_obj in self.user_schema.items():
            if column not in self.db_schema.keys():
                new_columns.append(column_obj)
                self.logger.info(f"""ADD Column {self.DATABASE}.{self.TABLE}.{column} as {column_obj.DATA_TYPE} SIZE({column_obj.SIZE})""")
        commands = []
        for column_obj in new_columns:
            commands.append(
                self.generate_add_columns_sql(column_name=column_obj.COLUMN, 
                                              column_type=column_obj.get_sql_type())
            )
        status = self.run_transaction(commands)
        if not status:
            for command in commands:
                self.logger.error(f"ERROR: ADD Column | {command}")
        return status

    def delete_old_columns(self):
        columns_to_delete = []
        for column, db_column_obj in self.db_schema.items():
            if column not in self.user_schema.keys():
                columns_to_delete.append(db_column_obj)
                self.logger.info(f"""DELETE Column {self.DATABASE}.{self.TABLE}.{column}""")
        commands = []
        for db_column_obj in columns_to_delete:
            commands.append(
                self.generate_drop_column_sql(column_name=db_column_obj.COLUMN)
            )
        status = self.run_transaction(commands)
        if not status:
            for command in commands:
                self.logger.error(f"ERROR: DELETE Column | {command}")
        return status

    def does_table_exist(self, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        query = getattr(TableCommands, self.DB_TYPE).DOES_TABLE_EXIST.format(
            database    = database,
            table_name  = table_name,
        )
        df = self.run_query(query)
        return df.iloc[0, 0] == 1


    def generate_select_all_sql(self, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        
        statement = "SELECT * FROM {database_table_combined}; \n".format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
        )
        # print(statement)
        return statement

    def generate_schema_table_sql(self, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        
        statement = getattr(TableCommands, self.DB_TYPE).TABLE_SCHEMA
        statement = statement.format(table_name = table_name)
        # print(statement)
        return statement

    def generate_column_try_cast_sql(self, column_name:str, column_type:str=None, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        new_type    = column_type if column_type else self.user_schema[column_name].DATA_TYPE
        old_type    = self.db_schema[column_name].DATA_TYPE

        # statement_g = "SELECT * FROM {database_table_combined} WHERE TRY_CAST({column} AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
        # statement_r = "SELECT * FROM {database_table_combined} WHERE TRY_CAST(REPLACE({column}, ',', '') AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"

        if old_type in ["VARCHAR", "NVARCHAR"] and new_type in ["INTEGER", "FLOAT"]:
            statement = getattr(TableCommands, self.DB_TYPE).COLUMN_TRY_CAST_REPLACED.format(
                database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
                column                  = column_name,
                new_type                = new_type.upper(),
            )
        else:
            statement = getattr(TableCommands, self.DB_TYPE).COLUMN_TRY_CAST.format(
                database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
                column                  = column_name,
                new_type                = new_type.upper(),
            )
        # print(statement)
        return statement
        
    def generate_add_columns_sql(self, column_name:str, column_type:str=None, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        column_info = column_type if column_type else self.user_schema[column_name].get_sql_type()

        statement   = "ALTER TABLE {database_table_combined} ADD {column} {column_type_and_size}; \n".format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            column                  = column_name,
            column_type_and_size    = column_info,
        )
        # print(statement)
        return statement

    def generate_drop_table_sql(self, database:str=None, table_name:str=None):
        database    = database   if database   else self.DATABASE
        table_name  = table_name if table_name else self.TABLE
        statement   = "DROP TABLE IF EXISTS {database_table_combined}; \n".format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
        )
        # print(statement)
        return statement
    
    def generate_drop_column_sql(self, column_name:str, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE

        statement = getattr(TableCommands, self.DB_TYPE).DROP_COLUMN.format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            column_name             = column_name
        )
        # print(statement)
        return statement

    def generate_modify_column_type_sql(self, column_name:str=None, column_type:str=None, database:str=None, table_name:str=None):
        database    = database    if database    else self.DATABASE
        table_name  = table_name  if table_name  else self.TABLE
        new_type    = column_type if column_type else self.user_schema[column_name].get_sql_type()

        statement = getattr(TableCommands, self.DB_TYPE).MODIFY_COLUMN.format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            column_name             = column_name,
            new_type                = new_type.upper(),
        )
        # print(statement)
        return statement
        
    def generate_delete_from_table_sql(self, database:str=None, table_name:str=None, column_name:str=None, column_value:str=None, delete_all:bool=False):
        database    = database   if database   else self.DATABASE
        table_name  = table_name if table_name else self.TABLE
        statement   = "DELETE FROM {database_table_combined} "
        w_statement = "DELETE FROM {database_table_combined} WHERE {column_name} {column_value} "
        if not column_name and not column_value and not delete_all:     # Safety measure don't delete unless delete_all is true
            return ""
        
        if column_name and column_value:
            column_value = clean_value_with_type(column_value, 
                                                 column_type=self.user_schema[column_name].DATA_TYPE, 
                                                 null_items=self.NULL_ITEMS)
            statement = w_statement.format(
                database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
                column_name             = column_name,
                column_value            = "="+column_value if "NULL" != column_value else "IS "+column_value,
            )
        else:
            statement = statement.format(
                database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            )
        # print(statement)
        return statement

    def generate_create_table_sql(self):
        database    = self.DATABASE
        table_name  = self.TABLE
        statement   = "CREATE TABLE {database_table_combined} (\n{column_and_types}\n); \n"

        column_and_types = []
        column_obj:Column
        for name, column_obj in self.user_schema.items():
            column_and_types.append(column_obj.get_create_column_line())
        column_and_types_str = ",\n".join(column_and_types)

        statement = statement.format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            column_and_types        = column_and_types_str,
        )
        # print(statement)
        return statement

    def generate_insert_sql(self, dataframe, database:str=None, table_name:str=None):
        dataframe = dataframe
        database    = database   if database   else self.DATABASE
        table_name  = table_name if table_name else self.TABLE
        statement   = "INSERT INTO {database_table_combined} ({columns}) VALUES\n {every_row_values}; \n"

        columns_str_list    = ', '.join(dataframe.columns)
        row_values_str_list = self._get_row_values(dataframe)
        every_row_values    = ",\n".join(row_values_str_list)

        statement = statement.format(
            database_table_combined = f"{database}.dbo.{table_name}" if database else table_name,
            columns                 = columns_str_list,
            every_row_values        = every_row_values,
        )
        # print(statement)
        return statement

    def _get_row_values(self, dataframe):
        dataframe = dataframe
        row_values_str_list = []
        for index, row in dataframe.iterrows():
            clean_values = []
            for column_name in list(dataframe.columns):
                clean_values.append(clean_value_with_type(row[column_name], 
                                                          column_type=self.user_schema[column_name].DATA_TYPE, 
                                                          null_items=self.NULL_ITEMS))
            values = ', '.join(clean_values)
            row_values_str_list.append(f"({values})")
        return row_values_str_list



if __name__ == "__main__":
    # python ./PySQL/Table.py

    pass
