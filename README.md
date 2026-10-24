# Product Demand Analytics Dashboard

An interactive dashboard for exploring product demand across warehouses and product categories, built with Streamlit and Plotly.

**Live app:** https://demand-analytics-dashboard.streamlit.app

## Overview
This project analyzes over 1 million order records covering 2,160 unique products (January 2011 to January 2017) to show which products and categories drive the most demand.

## Features

- Date range filter to focus on any time period
- Top 10 products by total demand (bar chart)
- Demand breakdown by product category
- Top 10 product summary table with total demand, number of records, and warehouses
- Live count of filtered records against the full dataset

## Dataset

`cleaned_product_demand.csv` contains the following columns:

| Column | Description |
|---|---|
| Product_Code | Unique product identifier |
| Warehouse | Warehouse that fulfilled the order |
| Product_Category | Category of the product |
| Date | Order date |
| Order_Demand | Quantity demanded |

The data was cleaned before use (date parsing, formatting characters removed from demand values, required-column validation).

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly

## Run Locally

```bash
git clone https://github.com/nandinis-cmd/product-demand-analytics.git
cd product-demand-analytics
pip install -r requirements.txt
streamlit run app.py
```

## Author

Nandini Sondkar
