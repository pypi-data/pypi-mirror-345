
# SQLPy



<p align="center">
    SQLPy (sql_pydb) is a Python library to bridge the gap between Python and Database Tables. 
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/dwarakhnv/SQLPy/refs/heads/main/media/sql_pydb_logo.png" alt="SQLPy"/>
</p>
<br>

---

## Instalation Guide

```python
pip install sql_pydb
```
- sql_pydb requires the following packages: Pandas, Numpy, pyodbc, python-dateutil


## Overview: 

- You can connect to MSSQL and SQLite.
- You can perform operations such as:
    - Create Database(s)
    - Create Table(s)
    - Drop Column(s)
    - Add Column(s)
    - Alter Column Types (If database supports it)
        - Performs a Try Cast check to be safe. (i.e. VARCHAR to INTEGER)
    - Read from Table
    - Delete from Table
    - Drop Table(s)


## Usage

1. Example: Upload Pandas DataFrame to a MSSQL Database
```python
from sql_pydb.Database import DatabaseType 
from sql_pydb.Table import TableActions

table = TableActions(database=DATABASE, table_name=TABLE_NAME, 
                driver="ODBC Driver 17 for SQL Server",
                server="url,port",
                username="admin",
                password="admin",
                db_type=DatabaseType.MSSQL)

df = pd.read_csv("...file.csv")
table.identify_schema(df)   # Figures out the best column types. Only needed 1 time per TableActions instance
table.sync_schema(update_column_types=True, add_new_columns=True, delete_old_columns=False) # Optional
status = table.insert_df(df, batch=1_000)
assert status == True
```


2. Example: Upload Pandas DataFrame to a SQLite Database
```python
from sql_pydb.Database import DatabaseType 
from sql_pydb.Table import TableActions

table = TableActions(table_name=TABLE_NAME, 
                sqlite_path = SQLITE_PATH,  # "./path/file.db"
                db_type=DatabaseType.SQLITE)

df = pd.read_csv("...file.csv")
table.identify_schema(df)   # Figures out the best column types. Only needed 1 time per TableActions instance
table.sync_schema(update_column_types=True, add_new_columns=True, delete_old_columns=False) # Optional
status = table.insert_df(df, batch=1_000)
assert status == True
```


3. Example: Query Table
```python
table = TableActions(...)
# ...
command = table.generate_select_all_sql()
df = table.run_query(command)   # Returns pd.DataFrame
```


4. Example: Execute Transactions
```python
table = TableActions(...)
# ...
command1 = table.generate_add_columns_sql()
command2 = table.generate_drop_column_sql(column_name="UNUSED_COLUMN")
# ...
commandX = table.generate_insert_sql(df_new_records)
status = table.run_transaction([command1, command2, ..., commandX])
assert status == True
```

5. Example: Create Table
```python
from sql_pydb.Column import Column
from sql_pydb.Table import TableActions

table = TableActions(...)
# ...
user_defined_columns = [
    Column("FIRST_NAME", data_type="VARCHAR", size=100),
    ...
    Column("ADDRESS", data_type="VARCHAR"), # Default 255 for strings
]
table.identify_schema(df, user_defined_columns)
# Option 1: Let it automatically sync with the new defined columns
status = table.sync_schema(update_column_types=True, add_new_columns=True, delete_old_columns=False)
# Option 2: Manually create the table
command = table.generate_create_table_sql()
status = table.run_transaction([command])
assert status == True
```
- You may choose to replace `user_defined_columns` with a pd.DataFrame with `["COLUMN", "DATA_TYPE", "SIZE"]` columns. `["DATABASE", "TABLE"]` columns may also be passed in. 



---

### Support:
- If you have a question or need additional support, please create an issue ticket on [SQLPy](https://github.com/dwarakhnv/SQLPy) GitHub Repo. 


### Additional:
- PyPI link: [sql-pydb](https://pypi.org/project/sql-pydb/)
- GitHub Link: [sql-pydb](https://github.com/dwarakhnv/SQLPy) 
