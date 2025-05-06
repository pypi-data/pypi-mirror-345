import os
import sys
import re
import pandas as pd
import numpy as np
from dateutil.parser import parse as date_parse

def is_item_null(item, null_items=[None, np.nan, pd.NaT]):
    if item is pd.NaT:      return True
    if item in null_items:  return True
    if type(item) == float:
        if np.isnan(item):  return True
    if pd.isna(item):       return True
    return False

def get_item_bool_version(item):
    """ Provides either True, False, or None """
    if is_item_null(item):  return None
    if item == True:        return True
    if item == False:       return False
    if item == 1:           return True
    if item == 0:           return False
    if item == 1.0:         return True
    if item == 0.0:         return False
    if str(item).upper() == "TRUE":     return True
    if str(item).upper() == "FALSE":    return False
    if str(item).upper() == "1":        return True
    if str(item).upper() == "0":        return False
    if str(item).upper() == "1.0":      return True
    if str(item).upper() == "0.0":      return False
    return None

def infer_sql_type_from_value(value:str):
    if value == "":     return "EMPTY"
    if value == None:   return "EMPTY"
    if value is np.nan: return "EMPTY"
    if value is pd.NaT: return "EMPTY"

    # Regular expressions for different data types
    int_regex           = re.compile(r'^-?\d+$')
    int_comma_regex     = re.compile(r'^-?\d+(,\d+)+$')
    float_regex         = re.compile(r'^-?\d*\.\d+$')
    float_comma_regex   = re.compile(r'^-?\d+(,\d+)+\.\d+$')
    bool_regex          = re.compile(r'^(True|False|true|false)$')

    # Check for each data type
    if int_regex.match(value):              return "INTEGER"
    elif int_comma_regex.match(value):      return "INTEGER"
    elif float_regex.match(value):          return "FLOAT"
    elif float_comma_regex.match(value):    return "FLOAT"
    elif bool_regex.match(value):           return "BOOLEAN"

    try:
        parsed = date_parse(value)
        # Decide DATE or DATETIME based on presence of time
        if parsed.time().hour == 0 and parsed.time().minute == 0 and parsed.time().second == 0:
            return "DATE"
        else:
            return "DATETIME"
    except (ValueError, OverflowError):
        pass
    
    try:
        value.encode('ascii')  # Try encoding as ASCII
    except UnicodeEncodeError:
        return "NVARCHAR"  # If it fails, it's a Unicode string
    
    return "VARCHAR"    # Default to VARCHAR

def determine_final_type(types:list[str], column_name:str=None):
    if "NVARCHAR" in types: return "NVARCHAR"
    if "VARCHAR" in types:  return "VARCHAR"
    if "DATETIME" in types: return "DATETIME"
    if "DATE" in types:     return "DATE"
    if "FLOAT" in types:    return "FLOAT"
    if "INTEGER" in types:  return "INTEGER"
    if "BOOLEAN" in types:  return "BOOLEAN"
    return "VARCHAR"  # Default if no types are identified

def clean_value_with_type(value, column_type:str="VARCHAR", null_items:list[object]=[None, np.nan, pd.NaT]):
    # Returns values with the quotes also for easy insert use

    if is_item_null(value, null_items):
        return f"NULL"
    
    if value == "":
        return f"NULL"

    if column_type in ["NVARCHAR", "VARCHAR"]:
        if value == "":
            return f"NULL"
        value = str(value).replace("'", "''")
        return f"'{value}'"

    if column_type in ["FLOAT", "INTEGER"]:
        value = str(value).replace(",", "").replace("'", "").replace('"', "")
        if value == "":
            return f"NULL"
        return f"{value}"

    if column_type in ["DATETIME", "DATETIME2", "DATE", "TIME", "SMALLDATETIME"]:
        if value == "":
            return f"NULL"
        return f"'{value}'"

    if column_type == "BOOLEAN":
        value_bool = get_item_bool_version(value)
        if value_bool == True:  return f"1"
        if value_bool == False: return f"0"
    
    return f"NULL"


