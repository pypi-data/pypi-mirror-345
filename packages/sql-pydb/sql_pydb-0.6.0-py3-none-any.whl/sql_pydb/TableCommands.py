

class TableCommandsMSSQL:
    TABLE_SCHEMA = """SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH AS SIZE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'dbo';"""
    
    COLUMN_TRY_CAST          = "SELECT * FROM {database_table_combined} WHERE TRY_CAST({column} AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    COLUMN_TRY_CAST_REPLACED = "SELECT * FROM {database_table_combined} WHERE TRY_CAST(REPLACE({column}, ',', '') AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    DROP_COLUMN              = "ALTER TABLE {database_table_combined} DROP COLUMN {column_name};\n"
    MODIFY_COLUMN            = "ALTER TABLE {database_table_combined} ALTER COLUMN {column_name} {new_type};\n"
    DOES_TABLE_EXIST         = "SELECT COUNT(*) FROM {database}.information_schema.tables WHERE table_name = '{table_name}'; \n"

class TableCommandsPostgres:
    TABLE_SCHEMA = """SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH AS SIZE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'public';"""
    COLUMN_TRY_CAST          = "SELECT * FROM {database_table_combined} WHERE CAST({column} AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    COLUMN_TRY_CAST_REPLACED = "SELECT * FROM {database_table_combined} WHERE CAST(REPLACE({column}, ',', '') AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    DROP_COLUMN              = "ALTER TABLE {database_table_combined} DROP COLUMN {column_name};\n"
    MODIFY_COLUMN            = "ALTER TABLE {database_table_combined} ALTER COLUMN {column_name} TYPE {new_type};\n"
    DOES_TABLE_EXIST         = "SELECT COUNT(*) FROM {database}.information_schema.tables WHERE table_name = '{table_name}'; \n"

class TableCommandsMySQL:
    TABLE_SCHEMA = """SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH AS SIZE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{table_name}';"""
    COLUMN_TRY_CAST          = "SELECT * FROM {database_table_combined} WHERE CAST({column} AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    COLUMN_TRY_CAST_REPLACED = "SELECT * FROM {database_table_combined} WHERE CAST(REPLACE({column}, ',', '') AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    DROP_COLUMN              = "ALTER TABLE {database_table_combined} DROP COLUMN {column_name};\n"
    MODIFY_COLUMN            = "ALTER TABLE {database_table_combined} MODIFY COLUMN {column_name} {new_type};\n"
    DOES_TABLE_EXIST         = "SELECT COUNT(*) FROM {database}.information_schema.tables WHERE table_name = '{table_name}'; \n"

class TableCommandsSQLite:
    TABLE_SCHEMA             = """PRAGMA table_info('{table_name}'); """
    COLUMN_TRY_CAST          = "SELECT * FROM {database_table_combined} WHERE CAST({column} AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    COLUMN_TRY_CAST_REPLACED = "SELECT * FROM {database_table_combined} WHERE CAST(REPLACE({column}, ',', '') AS {new_type}) IS NULL AND {column} IS NOT NULL; \n"
    DROP_COLUMN              = "-- NO DROP COLUMN in SQLite. Need to recreate Table\n"
    MODIFY_COLUMN            = "-- NO MODIFY COLUMN TYPES in SQLite. Need to recreate Table\n"
    DOES_TABLE_EXIST         = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name = '{table_name}'; --{database} \n"

class TableCommands:
    MSSQL       = TableCommandsMSSQL
    POSTGRESQL  = TableCommandsPostgres
    MYSQL       = TableCommandsMySQL
    SQLITE      = TableCommandsSQLite
