# Step 1 - Data Cleaning and Merging
# Project: Credit Risk and Loan Approval Analysis
#
# What this script does:
#   1. Loads the two raw Excel files
#   2. Handles missing values (stored as -99999 in this data)
#   3. Joins both datasets on PROSPECTID
#   4. Adds a few columns (age group, income band, etc.) for analysis
#   5. Saves the clean file in data/processed/

import pandas as pd

RAW_1 = "data/raw/case_study1.xlsx"   # internal bank data
RAW_2 = "data/raw/case_study2.xlsx"   # external credit bureau data
OUTPUT = "data/processed/loan_data_clean.csv"

# ---------- Load data ----------
df1 = pd.read_excel(RAW_1)
df2 = pd.read_excel(RAW_2)

print("Raw dataset 1 shape:", df1.shape)
print("Raw dataset 2 shape:", df2.shape)

# ---------- Missing values ----------
# Missing values are stored as -99999, not as NaN.

# Dataset 1: only Age_Oldest_TL and Age_Newest_TL have -99999 (40 rows),
# so we simply remove those rows.
df1 = df1[df1["Age_Oldest_TL"] != -99999]

# Dataset 2: some columns have too many missing values (more than 10,000 rows).
# Dropping rows would lose too much data, so we drop these columns instead.
cols_to_drop = []
for col in df2.columns:
    if (df2[col] == -99999).sum() > 10000:
        cols_to_drop.append(col)

print("Columns dropped from dataset 2:", cols_to_drop)
df2 = df2.drop(columns=cols_to_drop)

# The remaining columns have very few missing values, so drop those rows
df2 = df2[(df2 != -99999).all(axis=1)]

print("Dataset 1 after cleaning:", df1.shape)
print("Dataset 2 after cleaning:", df2.shape)

# ---------- Merge ----------
# Inner join keeps only customers that are present in both datasets
df = pd.merge(df1, df2, on="PROSPECTID", how="inner")
print("Merged shape:", df.shape)

# ---------- Basic checks ----------
print("Duplicate customers:", df["PROSPECTID"].duplicated().sum())
print("Null values:", df.isnull().sum().sum())

# ---------- New columns for analysis ----------
# Age group
df["Age_Group"] = pd.cut(
    df["AGE"],
    bins=[0, 25, 35, 45, 55, 100],
    labels=["21-25", "26-35", "36-45", "46-55", "55+"],
)
# the first bin starts from 0, so ages like 21 fall in "21-25"

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

# ---------- Save ----------
df.to_csv(OUTPUT, index=False)
print("Saved:", OUTPUT, df.shape)
