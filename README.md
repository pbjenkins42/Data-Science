# Industrial Vending Demand Forecasting

This project builds a time series forecasting model to optimize inventory management for industrial vending machines. It leverages historical dispensing and restocking data to predict future demand at the SKU and device level. This project is still a work in process.

## Problem Statement

In the context of industrial vending machines that dispense essential tools and supplies, accurate demand forecasting is crucial for minimizing downtime and maintaining operational efficiency. This project aims to predict future demand based on historical inventory and restocking data.

## Key Features

* Cleaned and prepared inventory and restocking datasets
* Performed exploratory data analysis (EDA) to uncover demand patterns and seasonality
* Engineered time-based features (day of week, month, lags, etc.)
* Modeled SKU-level demand using time series techniques (e.g., ARIMA, Prophet)
* Visualized trends, seasonality, and forecast performance

## Tech Stack

* Python (Pandas, NumPy, Matplotlib, Seaborn)
* Time Series Models: ARIMA, SARIMA, Prophet
* Jupyter Notebook
* GitHub for version control

## Project Structure

```
Predictive-Demand-Forecasting-Project/
├── Vending_Analysis.ipynb         # Annotated notebook with EDA and modeling
├── Inventory_Turnover.csv         # Historical dispensing data
├── Restock_data.csv               # Historical restocking data
├── README.md                      # Project overview (this file)
```

## How to Run

1. Clone the repo:

   ```
   git clone https://github.com/pbjenkins42/Predictive-Demand-Forecasting-Project.git
   cd Predictive-Demand-Forecasting-Project
   ```

2. Open `Vending_Analysis.ipynb` in Jupyter Notebook or Google Colab.

3. Follow the notebook cells in order to reproduce the analysis and modeling pipeline.

## Future Improvements

* Automate SKU-wise modeling using a loop or pipeline
* Deploy forecasting model via API or dashboard
* Add cost-based optimization for restocking strategies

## Author

**Paul Jenkins**
[LinkedIn](https://www.linkedin.com/in/paul-jenkins-32410353)
[paul.brown.jenkins@gmail.com](mailto:paul.brown.jenkins@gmail.com)
