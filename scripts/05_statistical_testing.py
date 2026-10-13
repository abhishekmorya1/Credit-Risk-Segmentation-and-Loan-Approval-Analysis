# Step 5 - Statistical Testing
# Project: Credit Risk Segmentation and Loan Approval Analysis
#
# Question: which columns are really linked to the risk category (Approved_Flag)?
#
# Tests used:
#   1. Chi-Square test   -> categorical columns vs Approved_Flag
#   2. ANOVA (F-test)    -> numerical columns vs Approved_Flag
#   3. VIF               -> remove numerical columns that repeat the same information
#
# Note: with 42,000+ rows almost every p-value is tiny, so we also calculate an
# "effect size" (Cramer's V and eta squared) to see HOW STRONG each link is.

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, f_oneway

df = pd.read_csv("data/processed/loan_data_clean.csv")

# Remove the columns we created for the analysis, we only test the original columns
created_columns = ["Age_Group", "Income_Band", "Score_Band", "Has_Missed_Payment", "Risk_Category"]
df = df.drop(columns=created_columns)

target = "Approved_Flag"
alpha = 0.05   # significance level

# =========================================================
# 1. Chi-Square test for categorical columns
# H0: the column and the risk category are independent
# H1: the column and the risk category are related
# =========================================================
categorical_columns = []
for col in df.select_dtypes(include=["object", "string"]).columns:
    if col != target:
        categorical_columns.append(col)

chi_rows = []
for col in categorical_columns:
    table = pd.crosstab(df[col], df[target])
    chi2, p_value, dof, expected = chi2_contingency(table)

    # Cramer's V: strength of the link (0 = no link, 1 = perfect link)
    n = table.values.sum()
    smaller_side = min(table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * smaller_side))

    chi_rows.append({
        "Feature": col,
        "Chi2": round(chi2, 1),
        "P_Value": p_value,
        "Cramers_V": round(cramers_v, 3),
        "Result": "Related" if p_value < alpha else "Not related",
    })

chi_results = pd.DataFrame(chi_rows).sort_values("Cramers_V", ascending=False)
print("\n=== Chi-Square test (categorical columns) ===")
print(chi_results.to_string(index=False))

# =========================================================
# 2. ANOVA for numerical columns
# H0: the average of the column is the same in P1, P2, P3 and P4
# H1: at least one risk category has a different average
# =========================================================
numerical_columns = list(df.select_dtypes(exclude=["object", "string"]).columns)
numerical_columns.remove("PROSPECTID")   # only an ID

categories = sorted(df[target].unique())
n_total = len(df)
k = len(categories)

anova_rows = []
for col in numerical_columns:
    groups = [df.loc[df[target] == c, col] for c in categories]
    f_stat, p_value = f_oneway(*groups)

    # eta squared: share of the variation in the column explained by the risk category
    eta_squared = (f_stat * (k - 1)) / (f_stat * (k - 1) + (n_total - k))

    anova_rows.append({
        "Feature": col,
        "F_Statistic": round(f_stat, 1),
        "P_Value": p_value,
        "Eta_Squared": round(eta_squared, 4),
    })

anova_results = pd.DataFrame(anova_rows).sort_values("F_Statistic", ascending=False)
significant = anova_results[anova_results["P_Value"] < alpha]

print("\n=== ANOVA (numerical columns) ===")
print("Columns tested:", len(anova_results))
print("Significant at 0.05:", len(significant))
print("\nTop 10 columns by F-statistic:")
print(anova_results.head(10).to_string(index=False))

# =========================================================
# 3. VIF (multicollinearity)
# VIF shows how well one column can be predicted from the other columns.
# VIF above 5 means the column mostly repeats information we already have.
# =========================================================
def calculate_vif(data):
    # Regress every column on all the other columns using the correlation matrix
    corr = data.corr().values
    n_cols = corr.shape[0]
    vif_values = []
    for i in range(n_cols):
        others = [j for j in range(n_cols) if j != i]
        corr_others = corr[np.ix_(others, others)]
        corr_with_i = corr[others, i]
        beta = np.linalg.lstsq(corr_others, corr_with_i, rcond=None)[0]
        r_squared = corr_with_i @ beta
        if r_squared > 0.999999:
            vif_values.append(np.inf)
        else:
            vif_values.append(1 / (1 - r_squared))
    return pd.Series(vif_values, index=data.columns)


# keep only the significant columns, and remove columns that never change
features = [c for c in significant["Feature"] if df[c].std() > 0]
f_stat_of = anova_results.set_index("Feature")["F_Statistic"]

print("\n=== VIF ===")
print("Columns before VIF:", len(features))

# Credit_Score is the strongest column in the ANOVA results and its VIF is only
# slightly above 5, so we always keep it
always_keep = ["Credit_Score"]

removed = []
while True:
    vif = calculate_vif(df[features])
    candidates = vif.drop(labels=always_keep, errors="ignore")
    if candidates.max() <= 5:
        break
    # if several columns are perfectly repeated (VIF = infinity),
    # remove the one that is least related to the risk category
    infinite = candidates[np.isinf(candidates)].index.tolist()
    if len(infinite) > 0:
        to_remove = min(infinite, key=lambda c: f_stat_of[c])
    else:
        to_remove = candidates.idxmax()
    removed.append(to_remove)
    features.remove(to_remove)

print("Columns removed:", len(removed))
print("Columns kept:", len(features))

final_vif = calculate_vif(df[features]).round(2)
selected = pd.DataFrame({
    "Feature": features,
    "VIF": [final_vif[c] for c in features],
    "F_Statistic": [f_stat_of[c] for c in features],
}).sort_values("F_Statistic", ascending=False)

print("\nSelected numerical columns (top 15):")
print(selected.head(15).to_string(index=False))

# =========================================================
# Save results and charts
# =========================================================
chi_results.to_csv("data/processed/stats_chi_square.csv", index=False)
anova_results.to_csv("data/processed/stats_anova.csv", index=False)
selected.to_csv("data/processed/stats_selected_features.csv", index=False)

# Chart 12: strength of link for categorical columns
plt.figure(figsize=(7, 4))
ordered = chi_results.sort_values("Cramers_V")
plt.barh(ordered["Feature"], ordered["Cramers_V"], color="steelblue")
plt.title("Link with Risk Category: Categorical Columns (Cramer's V)")
plt.xlabel("Cramer's V (higher = stronger link)")
plt.tight_layout()
plt.savefig("images/12_chi_square_cramers_v.png", dpi=120)
plt.close()

# Chart 13: top 15 numerical columns by F-statistic
top = selected.head(15).sort_values("F_Statistic")
plt.figure(figsize=(8, 6))
plt.barh(top["Feature"], top["F_Statistic"], color="steelblue")
plt.title("Top 15 Numerical Columns (ANOVA F-statistic, after VIF)")
plt.xlabel("F-statistic (higher = stronger difference between P1 to P4)")
plt.tight_layout()
plt.savefig("images/13_anova_top_features.png", dpi=120)
plt.close()

print("\nSaved: stats_chi_square.csv, stats_anova.csv, stats_selected_features.csv")
print("Charts saved: images/12_chi_square_cramers_v.png, images/13_anova_top_features.png")
