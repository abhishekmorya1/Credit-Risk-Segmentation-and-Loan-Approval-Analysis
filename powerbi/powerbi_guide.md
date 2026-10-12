# Power BI Dashboard Guide

Data file: `data/processed/powerbi_data.csv` (42,064 rows, 25 columns)

## 1. Load the data
1. Open Power BI Desktop > **Get Data > Text/CSV** > select `powerbi_data.csv` > **Transform Data**.
2. Check data types in Power Query: `Customer_ID` as Text, `Monthly_Income` and `Credit_Score` as Whole Number.
3. **Close & Apply**.

## 2. Sort the band columns
Text columns sort alphabetically, which gives a wrong order ("15K-25K" before "Below 15K").
Select the column in Data view > **Column tools > Sort by column**:
- `Age_Group` sort by `Age_Group_Sort`
- `Income_Band` sort by `Income_Band_Sort`
- `Score_Band` sort by `Score_Band_Sort`

## 3. DAX measures
Create these under **New measure**:

```
Total Customers = COUNTROWS(powerbi_data)

Avg Credit Score = AVERAGE(powerbi_data[Credit_Score])

Avg Monthly Income = AVERAGE(powerbi_data[Monthly_Income])

Low Risk Customers = CALCULATE([Total Customers], powerbi_data[Approved_Flag] = "P1")

High Risk Customers =
CALCULATE([Total Customers], powerbi_data[Approved_Flag] IN {"P3", "P4"})

High Risk % = DIVIDE([High Risk Customers], [Total Customers], 0)

Low Risk % = DIVIDE([Low Risk Customers], [Total Customers], 0)

Missed Payments per Account =
DIVIDE(SUM(powerbi_data[Tot_Missed_Pmnt]), SUM(powerbi_data[Total_TL]), 0)

Avg Enquiries 12M = AVERAGE(powerbi_data[Enquiries_Last_12M])
```

## 4. Page layout

**Page 1 - Overview**
| Visual | Fields |
|---|---|
| 4 Cards (top row) | Total Customers, Avg Credit Score, High Risk %, Avg Monthly Income |
| Donut chart | Legend: `Risk_Category`, Values: `Total Customers` |
| Clustered column | Axis: `Age_Group`, Values: `High Risk %` |
| Clustered column | Axis: `Score_Band`, Values: `Total Customers` |
| Slicers | `Gender`, `Education`, `Marital_Status` |

**Page 2 - Customer Profile**
| Visual | Fields |
|---|---|
| 100% stacked column | Axis: `Income_Band`, Legend: `Risk_Category`, Values: `Total Customers` |
| Bar chart | Axis: `Education`, Values: `Avg Monthly Income` |
| Bar chart | Axis: `First_Product`, Values: `Low Risk %` |
| Matrix | Rows: `Age_Group`, Columns: `Risk_Category`, Values: `Total Customers` |

**Page 3 - Risk Behaviour**
| Visual | Fields |
|---|---|
| Clustered column | Axis: `Risk_Category`, Values: `Missed Payments per Account` |
| Clustered column | Axis: `Risk_Category`, Values: `Avg Enquiries 12M` |
| Scatter chart | X: `Monthly_Income`, Y: `Credit_Score`, Legend: `Risk_Category` |
| Slicers | `Age_Group`, `Income_Band` |

## 5. Tips
- Use the same colour for each risk category on every page (for example green for P1 and red for P4).
- Give every visual a clear title and add a page title text box.
- `Monthly_Income` has a few extreme values (maximum is 25 lakh), so use average carefully or filter outliers in the scatter chart.
- Save a screenshot of each page in `images/` (for example `powerbi_page1.png`) and add it to the README.
