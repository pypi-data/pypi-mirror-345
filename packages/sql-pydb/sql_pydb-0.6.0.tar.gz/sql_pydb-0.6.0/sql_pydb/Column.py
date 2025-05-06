


class Column():

    """
    Support for VARCHAR, NVARCHAR, INT, FLOAT, DATE, DATETIME, BOOLEAN
    
    Support coming for the following types:
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        tinyint_col TINYINT,
        smallint_col SMALLINT,
        mediumint_col MEDIUMINT,
        bigint_col BIGINT,
        decimal_col DECIMAL(10,2),
        bit_col BIT(1),
        char_col CHAR(10),
        varchar_col VARCHAR(255),
        text_col TEXT,
        tinytext_col TINYTEXT,
        mediumtext_col MEDIUMTEXT,
        longtext_col LONGTEXT,
        binary_col BINARY(16),
        varbinary_col VARBINARY(255),
        blob_col BLOB,
        tinyblob_col TINYBLOB,
        mediumblob_col MEDIUMBLOB,
        longblob_col LONGBLOB,
        timestamp_col TIMESTAMP,
        time_col TIME,
        year_col YEAR
    
    """
    
    def __init__(self, column_name, data_type="VARCHAR", size=None, database=None, table=None, primary_key=None):
        self.DATABASE   = database
        self.TABLE      = table
        self.COLUMN     = column_name
        self.DATA_TYPE  = data_type.upper()
        self.SIZE       = size if size else None
        self.PRIMARY_STR= primary_key            # "PRIMARY KEY" or "AUTO_INCREMENT PRIMARY KEY"
        self.cleanup()
    
    def cleanup(self):
        if self.DATA_TYPE == "INT":     # Rename to full name
            self.DATA_TYPE = "INTEGER"
        if self.DATA_TYPE == "DOUBLE":  # Rename to FLOAT
            self.DATA_TYPE = "FLOAT"
        if not self.SIZE and self.DATA_TYPE in ["VARCHAR", "NVARCHAR"]:
            self.SIZE = 255     # Default value
        if self.SIZE and self.DATA_TYPE not in ["VARCHAR", "NVARCHAR"]:
            self.SIZE = None    # No size for INT, FLOAT, DATE, etc
        if self.SIZE:
            if type(self.SIZE) == float:
                self.SIZE = int(self.SIZE)
            if type(self.SIZE) == str:
                try:
                    # If a "," is present, leave it be for DOUBLE(10,2)
                    if "." in self.SIZE:
                        self.SIZE = float(self.SIZE)
                    self.SIZE = int(self.SIZE)
                except:
                    pass        
    
    def get_create_column_line(self):
        if self.PRIMARY_STR:
            # Example: "    column_name VARCHAR(255) PRIMARY KEY"
            # Example: "    column_name VARCHAR(255) AUTO_INCREMENT PRIMARY KEY"
            statement = "\t{column_name} {column_type_and_size} {primary_str}".format(
                column_name          = self.COLUMN,
                column_type_and_size = f"{self.DATA_TYPE}({self.SIZE})" if self.SIZE else self.DATA_TYPE,
                primary_str          = self.PRIMARY_STR,
            )
            return statement
        # Example: "    column_name VARCHAR(255)"
        # Example: "    column_name FLOAT"
        statement = "\t{column_name} {column_type_and_size}".format(
            column_name          = self.COLUMN,
            column_type_and_size = f"{self.DATA_TYPE}({self.SIZE})" if self.SIZE else self.DATA_TYPE,
        )
        return statement

    def get_sql_type(self):
        """
        Returns VARCHAR(SIZE) or FLOAT or DOUBLE(SIZE)=DOUBLE(10,3)
        """
        return f"{self.DATA_TYPE}({self.SIZE})" if self.SIZE else self.DATA_TYPE

    def __str__(self):
        return f"Column(DATABASE={self.DATABASE}, TABLE={self.TABLE}, COLUMN={self.COLUMN}, DATA_TYPE={self.DATA_TYPE}, SIZE={self.SIZE})"

    def __repr__(self):
        return f"Column(DATABASE={self.DATABASE}, TABLE={self.TABLE}, COLUMN={self.COLUMN}, DATA_TYPE={self.DATA_TYPE}, SIZE={self.SIZE})"

    def __eq__(self, other):
        if isinstance(other, Column):
            return (self.DATABASE, self.TABLE, self.COLUMN, self.DATA_TYPE, self.SIZE) == (other.DATABASE, other.TABLE, other.COLUMN, other.DATA_TYPE, other.SIZE)
        return False
