# Step 1 - Data Cleaning and Merging
# Project: Credit Risk Segmentation and Loan Approval Analysis
#
# What this script does:
#   1. Loads the two raw Excel files and checks them
#   2. Handles missing values (stored as -99999 in this data)
#   3. Joins both datasets on PROSPECTID
#   4. Runs data quality checks (duplicates, wrong values, outliers)
#   5. Adds a few columns (age group, income band, etc.) for analysis
#   6. Saves the clean file and a cleaning log in data/processed/

import pandas as pd

RAW_1 = "data/raw/case_study1.xlsx"   # internal bank data
RAW_2 = "data/raw/case_study2.xlsx"   # external credit bureau data
OUTPUT = "data/processed/loan_data_clean.csv"
LOG_FILE = "data/processed/cleaning_log.csv"

cleaning_log = []


def add_log(step, rows, columns):
    cleaning_log.append({"Step": step, "Rows": rows, "Columns": columns})
    print(step, "->", rows, "rows,", columns, "columns")


# ---------- 1. Load data ----------
df1 = pd.read_excel(RAW_1)
df2 = pd.read_excel(RAW_2)
add_log("Raw dataset 1", df1.shape[0], df1.shape[1])
add_log("Raw dataset 2", df2.shape[0], df2.shape[1])

# ---------- 2. Initial checks on the raw data ----------
print("\nDuplicate PROSPECTID in dataset 1:", df1["PROSPECTID"].duplicated().sum())
print("Duplicate PROSPECTID in dataset 2:", df2["PROSPECTID"].duplicated().sum())
print("Real NaN values in dataset 1:", df1.isnull().sum().sum())
print("Real NaN values in dataset 2:", df2.isnull().sum().sum())
print("Same customers in both files:", set(df1["PROSPECTID"]) == set(df2["PROSPECTID"]))

# ---------- 3. Missing values ----------
# There are no blank cells. Missing values are stored as -99999.
print("\nColumns with -99999 in dataset 1:")
for col in df1.columns:
    count = (df1[col] == -99999).sum()
    if count > 0:
        print("  ", col, count)

# Dataset 1: only Age_Oldest_TL and Age_Newest_TL have -99999 (40 rows),
# so we simply remove those rows.
df1 = df1[df1["Age_Oldest_TL"] != -99999]
add_log("Dataset 1 after removing -99999 rows", df1.shape[0], df1.shape[1])

# Dataset 2: some columns have too many missing values (more than 10,000 rows).
# Dropping rows would lose too much data, so we drop these columns instead.
cols_to_drop = []
for col in df2.columns:
    if (df2[col] == -99999).sum() > 10000:
        cols_to_drop.append(col)

print("\nColumns dropped from dataset 2:", cols_to_drop)
df2 = df2.drop(columns=cols_to_drop)
add_log("Dataset 2 after dropping high-missing columns", df2.shape[0], df2.shape[1])

# The remaining columns have few missing values, so drop those rows
df2 = df2[(df2 != -99999).all(axis=1)]
add_log("Dataset 2 after removing -99999 rows", df2.shape[0], df2.shape[1])

# ---------- 4. Merge ----------
# Inner join keeps only customers that are present in both datasets
df = pd.merge(df1, df2, on="PROSPECTID", how="inner")
add_log("Merged dataset", df.shape[0], df.shape[1])

# ---------- 5. Data quality checks ----------
print("\n--- Data quality checks ---")
print("Duplicate customers:", df["PROSPECTID"].duplicated().sum())
print("Fully duplicate rows:", df.duplicated().sum())
print("Null values:", df.isnull().sum().sum())
print("Remaining -99999 values:", (df == -99999).sum().sum())

# Negative values are not expected in this data
numeric_cols = df.drop(columns=["PROSPECTID"]).select_dtypes(exclude=["object", "string"])
print("Columns with negative values:", int((numeric_cols < 0).any().sum()))

# Text columns: remove extra spaces and check the categories
text_cols = list(df.select_dtypes(include=["object", "string"]).columns)
for col in text_cols:
    df[col] = df[col].str.strip()
print("Text columns checked:", text_cols)
print("Education categories:", sorted(df["EDUCATION"].unique()))
print("Marital status categories:", sorted(df["MARITALSTATUS"].unique()))
print("Risk categories:", sorted(df["Approved_Flag"].unique()))

# Age range
print("Age range:", df["AGE"].min(), "to", df["AGE"].max())

# Income outliers (IQR method). We only report them and keep the rows,
# because very high incomes are possible for real customers.
q1 = df["NETMONTHLYINCOME"].quantile(0.25)
q3 = df["NETMONTHLYINCOME"].quantile(0.75)
iqr = q3 - q1
outliers = df[(df["NETMONTHLYINCOME"] > q3 + 1.5 * iqr) | (df["NETMONTHLYINCOME"] < q1 - 1.5 * iqr)]
print("Income outliers (kept):", len(outliers), "| maximum income:", df["NETMONTHLYINCOME"].max())

# ---------- 6. New columns for analysis ----------
# Age group
df["Age_Group"] = pd.cut(
    df["AGE"],
    bins=[0, 25, 35, 45, 55, 100],
    labels=["21-25", "26-35", "36-45", "46-55", "55+"],
)

# Income band (monthly income in rupees)
df["Income_Band"] = pd.cut(
    df["NETMONTHLYINCOME"],
    bins=[-1, 15000, 25000, 40000, 60000, float("inf")],
    labels=["Below 15K", "15K-25K", "25K-40K", "40K-60K", "Above 60K"],
)

# Credit score band
df["Score_Band"] = pd.cut(
    df["Credit_Score"],
    bins=[0, 600, 650, 700, 750, 900],
    labels=["Below 600", "600-650", "650-700", "700-750", "750+"],
)

# Customers who missed at least one payment
df["Has_Missed_Payment"] = (df["Tot_Missed_Pmnt"] > 0).astype(int)

# Readable names for the approval categories
# P1 = lowest risk (best customers), P4 = highest risk
risk_names = {
    "P1": "P1 - Low Risk",
    "P2": "P2 - Medium Risk",
    "P3": "P3 - High Risk",
    "P4": "P4 - Very High Risk",
}
df["Risk_Category"] = df["Approved_Flag"].map(risk_names)

# ---------- 7. Save ----------
df.to_csv(OUTPUT, index=False)
add_log("Final clean file (with 5 new columns)", df.shape[0], df.shape[1])

pd.DataFrame(cleaning_log).to_csv(LOG_FILE, index=False)
print("\nSaved:", OUTPUT, df.shape)
print("Saved cleaning log:", LOG_FILE)
