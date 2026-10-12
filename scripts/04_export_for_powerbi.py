# Step 4 - Prepare a Power BI friendly file
# Power BI needs readable text columns (not one-hot encoded numbers),
# so we keep only the useful columns and give them proper names.

import pandas as pd

df = pd.read_csv("data/processed/loan_data_clean.csv")

# Full names for product codes
product_names = {
    "PL": "Personal Loan",
    "CC": "Credit Card",
    "AL": "Auto Loan",
    "HL": "Home Loan",
    "ConsumerLoan": "Consumer Loan",
    "others": "Other",
}
df["First_Product"] = df["first_prod_enq2"].map(product_names)
df["Last_Product"] = df["last_prod_enq2"].map(product_names)

df["Gender"] = df["GENDER"].map({"M": "Male", "F": "Female"})

# Sort columns: Power BI sorts text alphabetically, so we add a number
# column and use "Sort by column" for bands that have a natural order.
age_sort = {"21-25": 1, "26-35": 2, "36-45": 3, "46-55": 4, "55+": 5}
income_sort = {"Below 15K": 1, "15K-25K": 2, "25K-40K": 3, "40K-60K": 4, "Above 60K": 5}
score_sort = {"Below 600": 1, "600-650": 2, "650-700": 3, "700-750": 4, "750+": 5}
df["Age_Group_Sort"] = df["Age_Group"].map(age_sort)
df["Income_Band_Sort"] = df["Income_Band"].map(income_sort)
df["Score_Band_Sort"] = df["Score_Band"].map(score_sort)

columns = [
    "PROSPECTID", "AGE", "Age_Group", "Age_Group_Sort", "Gender", "MARITALSTATUS",
    "EDUCATION", "NETMONTHLYINCOME", "Income_Band", "Income_Band_Sort",
    "Credit_Score", "Score_Band", "Score_Band_Sort", "Approved_Flag", "Risk_Category",
    "Total_TL", "Tot_Active_TL", "Tot_Closed_TL", "Tot_Missed_Pmnt", "Has_Missed_Payment",
    "tot_enq", "enq_L6m", "enq_L12m", "First_Product", "Last_Product",
]
out = df[columns].copy()
out = out.rename(columns={
    "PROSPECTID": "Customer_ID",
    "AGE": "Age",
    "MARITALSTATUS": "Marital_Status",
    "EDUCATION": "Education",
    "NETMONTHLYINCOME": "Monthly_Income",
    "tot_enq": "Total_Enquiries",
    "enq_L6m": "Enquiries_Last_6M",
    "enq_L12m": "Enquiries_Last_12M",
})

out.to_csv("data/processed/powerbi_data.csv", index=False)
print("Saved data/processed/powerbi_data.csv", out.shape)
