# Step 3 - Load clean data into a SQLite database
# After this, open sql/analysis_queries.sql in VS Code and run the queries.

import sqlite3
import pandas as pd

df = pd.read_csv("data/processed/loan_data_clean.csv")

# keep only the columns we need for the SQL analysis
columns = [
    "PROSPECTID", "AGE", "Age_Group", "GENDER", "MARITALSTATUS", "EDUCATION",
    "NETMONTHLYINCOME", "Income_Band", "Time_With_Curr_Empr",
    "Credit_Score", "Score_Band", "Approved_Flag", "Risk_Category",
    "Total_TL", "Tot_Active_TL", "Tot_Closed_TL", "Tot_Missed_Pmnt",
    "Has_Missed_Payment", "Age_Oldest_TL", "Home_TL", "Auto_TL", "CC_TL", "PL_TL",
    "tot_enq", "enq_L6m", "enq_L12m", "num_times_delinquent",
    "first_prod_enq2", "last_prod_enq2",
]
customers = df[columns].copy()
customers.columns = [c.lower() for c in customers.columns]

conn = sqlite3.connect("data/processed/loan_data.db")
customers.to_sql("customers", conn, if_exists="replace", index=False)

# a quick check that the table was created
count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
print("Rows in customers table:", count)
conn.close()
