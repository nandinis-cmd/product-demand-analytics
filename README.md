# Product Demand Analytics Dashboard

An interactive dashboard for exploring product demand across warehouses and
product categories, built with Python, Pandas, Plotly and Streamlit.

**Live app:** https://demand-analytics-dashboard.streamlit.app

<!-- Add a screenshot once you have one: ![Dashboard overview](screenshots/overview.png) -->

## Overview
Analyzes 1,037,336 order records covering 2,160 products, 4 warehouses and
33 categories (Jan 2011 to Jan 2017) to show which products, categories and
warehouses drive the most demand.

## Key Findings
- **Demand is concentrated:** 86 products (4%) account for 80% of demand;
  the top 10 account for 34.6%.
- **One category dominates:** Category_019 is 82.6% of demand.
- **One warehouse carries most volume:** Whse_J handles 65.5%, Whse_S 20.2%,
  Whse_C 11.4% and Whse_A 2.9%.
- **The 2012 jump is a data artifact, not demand growth:** monthly records rise
  from 598 (Dec 2011) to 15,614 (Jan 2012), while average demand per record
  stays steady (about 4,500-4,800). Data before late 2011 is very sparse.
- **Seasonality is mild:** monthly demand stays within about 90-109% of the
  average (2012-2016).
- **Yearly totals:** grew from 2012 to 2015, then fell about 10% in 2016. The
  data does not explain why.

## Features
- Date-range filter, KPI cards and monthly demand trend
- Product explorer with per-product demand history
- Top 10 products, category breakdown and top-10 summary table
- Warehouse comparison and product-by-warehouse heatmap
- Live count of filtered records against the full dataset

## Dataset
Source: <!-- add the Kaggle dataset name and link here -->

`cleaned_product_demand.csv` contains:

| Column | Description |
|---|---|
| Product_Code | Unique product identifier |
| Warehouse | Warehouse that fulfilled the order |
| Product_Category | Category of the product |
| Date | Order date |
| Order_Demand | Quantity demanded |

**Cleaning steps:** date parsing, removal of formatting characters from demand
values, required-column validation, and dropping rows with missing values.

## Limitations
- Values written in brackets, such as (500), are treated as positive; their
  original meaning is unverified, so totals and rankings are provisional.
- January 2017 is a partial month (9 days); data before 2012 is sparse.
- The dataset has no inventory levels, so it cannot say how much stock to hold.

## Tech Stack
Python, Streamlit, Pandas, Plotly

## Run Locally
```bash
git clone https://github.com/nandinis-cmd/product-demand-analytics.git
cd product-demand-analytics
pip install -r requirements.txt
streamlit run app.py
```

## Author
Nandini Sondkar
