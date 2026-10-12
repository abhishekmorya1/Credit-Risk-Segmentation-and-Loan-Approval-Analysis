# Step 2 - Exploratory Data Analysis (EDA)
# Reads the clean file and saves charts in the images/ folder

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # so charts are saved without opening a window
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/processed/loan_data_clean.csv")
sns.set_style("whitegrid")

order = ["P1", "P2", "P3", "P4"]


def save_chart(name):
    plt.tight_layout()
    plt.savefig("images/" + name, dpi=120)
    plt.close()


# ---------- Quick overview ----------
print(df.shape)
print(df[["AGE", "NETMONTHLYINCOME", "Credit_Score"]].describe())
print(df["Approved_Flag"].value_counts(normalize=True) * 100)

# ---------- 1. Customers in each risk category ----------
counts = df["Approved_Flag"].value_counts().reindex(order)
plt.figure(figsize=(7, 5))
ax = sns.barplot(x=counts.index, y=counts.values, color="steelblue")
for i, v in enumerate(counts.values):
    ax.text(i, v + 200, str(v), ha="center")
plt.title("Customers by Risk Category")
plt.xlabel("Risk Category (P1 = lowest risk)")
plt.ylabel("Number of customers")
save_chart("01_risk_category_count.png")

# ---------- 2. Age distribution ----------
plt.figure(figsize=(7, 5))
plt.hist(df["AGE"], bins=20, edgecolor="black", color="steelblue")
plt.title("Age Distribution")
plt.xlabel("Age")
plt.ylabel("Number of customers")
save_chart("02_age_distribution.png")

# ---------- 3. Gender split ----------
gender = df["GENDER"].value_counts()
plt.figure(figsize=(5, 5))
plt.pie(gender.values, labels=["Male", "Female"], autopct="%1.1f%%",
        colors=["steelblue", "lightcoral"])
plt.title("Gender Split")
save_chart("03_gender_split.png")

# ---------- 4. Risk category by gender (percentage) ----------
gender_risk = pd.crosstab(df["GENDER"], df["Approved_Flag"], normalize="index") * 100
gender_risk = gender_risk[order]
gender_risk.plot(kind="bar", figsize=(7, 5))
plt.title("Risk Category Share by Gender (%)")
plt.xlabel("Gender")
plt.ylabel("Percentage")
plt.xticks(rotation=0)
save_chart("04_risk_by_gender.png")

# ---------- 5. Credit score by risk category ----------
plt.figure(figsize=(7, 5))
sns.boxplot(data=df, x="Approved_Flag", y="Credit_Score", order=order, color="lightblue")
plt.title("Credit Score by Risk Category")
plt.xlabel("Risk Category")
plt.ylabel("Credit Score")
save_chart("05_score_by_risk.png")

# ---------- 6. Average income by education ----------
edu = df.groupby("EDUCATION")["NETMONTHLYINCOME"].mean().sort_values()
plt.figure(figsize=(8, 5))
edu.plot(kind="barh", color="steelblue")
plt.title("Average Monthly Income by Education")
plt.xlabel("Average monthly income")
plt.ylabel("")
save_chart("06_income_by_education.png")

# ---------- 7. Risk category by income band ----------
income_order = ["Below 15K", "15K-25K", "25K-40K", "40K-60K", "Above 60K"]
inc_risk = pd.crosstab(df["Income_Band"], df["Approved_Flag"], normalize="index") * 100
inc_risk = inc_risk.reindex(income_order)[order]
inc_risk.plot(kind="bar", stacked=True, figsize=(8, 5))
plt.title("Risk Category Mix by Income Band (%)")
plt.xlabel("Income band")
plt.ylabel("Percentage")
plt.xticks(rotation=0)
save_chart("07_risk_by_income.png")

# ---------- 8. Risk category by age group ----------
age_order = ["21-25", "26-35", "36-45", "46-55", "55+"]
age_risk = pd.crosstab(df["Age_Group"], df["Approved_Flag"], normalize="index") * 100
age_risk = age_risk.reindex(age_order)[order]
age_risk.plot(kind="bar", stacked=True, figsize=(8, 5))
plt.title("Risk Category Mix by Age Group (%)")
plt.xlabel("Age group")
plt.ylabel("Percentage")
plt.xticks(rotation=0)
save_chart("08_risk_by_age.png")

# ---------- 9. First product enquired ----------
first_prod = df["first_prod_enq2"].value_counts()
plt.figure(figsize=(8, 5))
first_prod.plot(kind="bar", color="steelblue")
plt.title("First Product Enquired")
plt.xlabel("Product")
plt.ylabel("Number of customers")
plt.xticks(rotation=0)
save_chart("09_first_product_enquired.png")

# ---------- 10. Missed payments per loan account ----------
# P1 customers have more loan accounts, so total missed payments look high.
# Missed payments per account is a fairer comparison.
grp = df.groupby("Approved_Flag")
missed = (grp["Tot_Missed_Pmnt"].sum() / grp["Total_TL"].sum()).reindex(order)
plt.figure(figsize=(7, 5))
ax = sns.barplot(x=missed.index, y=missed.values, color="indianred")
for i, v in enumerate(missed.values):
    ax.text(i, v + 0.002, str(round(v, 3)), ha="center")
plt.title("Missed Payments per Loan Account")
plt.xlabel("Risk Category")
plt.ylabel("Missed payments per account")
save_chart("10_missed_payment_by_risk.png")

# ---------- 11. Correlation heatmap (a few key columns) ----------
key_cols = ["Credit_Score", "AGE", "NETMONTHLYINCOME", "Tot_Missed_Pmnt",
            "Total_TL", "Tot_Active_TL", "tot_enq", "Time_With_Curr_Empr"]
plt.figure(figsize=(8, 6))
sns.heatmap(df[key_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation between Key Columns")
save_chart("11_correlation_heatmap.png")

# ---------- Key numbers for the README ----------
print("\nAverage values by risk category")
print(df.groupby("Approved_Flag")[["Credit_Score", "AGE", "NETMONTHLYINCOME",
                                    "Tot_Missed_Pmnt", "tot_enq"]].mean().round(1))
print("\nCharts saved in images/")
