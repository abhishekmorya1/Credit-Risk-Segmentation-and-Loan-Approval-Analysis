# Runs one query from sql/analysis_queries.sql and prints the result
# Usage: python run_sql.py 1      (runs Q1)
#        python run_sql.py 7      (runs Q7)
#        python run_sql.py        (shows how many queries there are)

import sqlite3
import sys
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

# read the sql file and split it into separate queries
text = open("sql/analysis_queries.sql").read()
queries = []
for part in text.split(";"):
    if "SELECT" in part:
        queries.append(part.strip())

if len(sys.argv) < 2:
    print("There are", len(queries), "queries. Example: python run_sql.py 1")
    sys.exit()

number = int(sys.argv[1])
if number < 1 or number > len(queries):
    print("Please give a number between 1 and", len(queries))
    sys.exit()

query = queries[number - 1]
print(query)
print()

conn = sqlite3.connect("data/processed/loan_data.db")
print(pd.read_sql(query, conn))
conn.close()
