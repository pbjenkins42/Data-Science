# -*- coding: utf-8 -*-
"""Vending Analysis.ipynb

Original file is located at
    https://colab.research.google.com/drive/1621q38x3O-SuRBhhaDMTdD8RYvLrl8Wv
"""

# Step 1 load data and pandas
import pandas as pd

#read csvs
pd.read_csv('/content/Inventory_Turnover.csv')
pd.read_csv('/content/Restock_data.csv')

#create copies of files
df_inventory = pd.read_csv('/content/Inventory_Turnover.csv').copy()
df_restock = pd.read_csv('/content/Restock_data.csv').copy()

# confirm csvs are loaded
print(df_inventory.head())
print(df_restock.head())

print(df_inventory.tail())
print(df_restock.tail())

# Step 2 and 3: data cleaning and exploratory data analysis

# 2a. Handling null values:

# Count null values
print('Null Values:', df_inventory.isnull().sum())
print('Null Values:',df_restock.isnull().sum())

# there are zero null values

# 2b. Handling duplicates

# find total rows
total_rows_inventory = len(df_inventory)
total_rows_restock = len(df_restock)

print('Total Rows Count', total_rows_inventory)
print('Total Rows Count', total_rows_restock)

# count unique rows
unique_rows_inventory = df_inventory.drop_duplicates()
unique_rows_restock = df_restock.drop_duplicates()

# find the difference between total_rows and unique_rows
print('Total Duplicate Rows', total_rows_inventory - len(unique_rows_inventory))
print('Total Duplicate Rows', total_rows_restock - len(unique_rows_restock))

# there are no duplicate rows or null values and thus none to drop or fill in

# 2c. Handling data types
print('Data Types:\n', df_inventory.dtypes)
print()
print('Data Types:\n', df_restock.dtypes)

# 2c. Convert data types: object -> string, dispense_date and restock_date -> datetime

# convert object data types to strings in inventory csv
for col in ['sku', 'device_id']:
    df_inventory[col] = df_inventory[col].astype('string')

# convert object data types to strings in restock csv
for col in ['device_id', 'global_order_id','currency_code']:
    df_restock[col] = df_restock[col].astype('string')

# convert dates to date_time
df_inventory['dispense_date'] = pd.to_datetime(df_inventory['dispense_date'], dayfirst=False)
df_restock['restock_date'] = pd.to_datetime(df_restock['restock_date'], dayfirst=False)

# make the date column the index for TSA
df_inventory.index = df_inventory['dispense_date']

df_restock.index = df_restock['restock_date']


print('Data Types:\n', df_inventory.dtypes)
print()
print('Data Types:\n', df_restock.dtypes)

print(df_inventory.head())
print(df_restock.head())

# all data has been converted to the correct formats

# Step 3 exploratory data analysis

# 3a. Descriptive stats

# Numeric summary
print("Inventory numeric summary:\n", df_inventory.describe().T)
print("\nRestock numeric summary:\n", df_restock.describe().T)

# All‐column summary (including object types)
print("\nInventory full describe:\n", df_inventory.describe(include='all').T)
print("\nRestock full describe:\n", df_restock.describe(include='all').T)

"""Dispense events are typically small (< 12 units), but there are outliers (up to 162 units).

package_qty is almost always 1, so you can treat each row as “one package = one item” in your modeling.

One machine handles roughly 25 % of all dispenses and ~20 % of all restocks, so machine‐level effects matter (e.g. that high‐volume device will dominate forecasts).

Restocks average ~272 units (± 100), with most fills between 200–350, but outliers up to ~612; again, machine‐level fill events are highly variable.
"""

# need to find the last date for both inventory and restock
print('First Date Inventory:', df_inventory['dispense_date'].min())
print('First Date Restock:', df_restock['restock_date'].min())

print('Last Date Inventory:', df_inventory['dispense_date'].max())
print('Last Date Restock:', df_restock['restock_date'].max())

# 3b. Categorical distributions

# find the count of unique skus and device_ids
print('Unique skus:', df_inventory['sku'].nunique())
print('\nUnique device_ids df_inventory:', df_inventory['device_id'].nunique())
print('Unique device_ids df_restock:', df_restock['device_id'].nunique())


# inventory device_id and sku frequency
print('\nCount of device_ids:', df_inventory['device_id'].value_counts().head(5))
print('\nCount of skus top 20:', df_inventory['sku'].value_counts().head(20))
print('\nCount of skus bottom 20:',df_inventory['sku'].value_counts().tail(20))

# restock device_id counts
print('\n',df_restock['device_id'].value_counts().head(5))

"""There are 82 unique skus

There are only 5 distinct device_id

device_af645ebf4c96eb6e430529a2a9913686 has the highest count in df_inventory and 2nd highest count in df_restock

device_c287be7e02167387bf9e7eca061ce5b5 has the 2nd highest count in df_inventory and highest count in df_restock

Given that they are both at the top of df_inventory you'd expect them to also be at the top of df_restock

The top 17 skus are very close in their counts

higest sku count is 690b7d2f4218991b6496be8eb456a943 with 726 and
lowest skus are 461104747ec72f92b0faf4da6d904934 and 924aa4fc983c1f8364e5bd1f04cbb062 with 2
"""

import matplotlib.pyplot as plt

# 3c. Histograms
df_inventory[['qty_dispensed']].hist(bins=20, figsize=(8,4))
plt.suptitle('Inventory numeric distributions')
plt.show()

df_restock['total'].hist(bins=20, figsize=(4,3))
plt.title('Restock total distribution')
plt.show()

# Box plots
plt.figure()
plt.boxplot(df_inventory['qty_dispensed'].dropna(), vert=False)
plt.title('Boxplot of Quantity Dispensed')
plt.xlabel('qty_dispensed')
plt.tight_layout()
plt.show()

plt.figure()
plt.boxplot(df_restock['total'].dropna(), vert=False)
plt.title('Boxplot of Total Restocked')
plt.xlabel('total_restocked')
plt.tight_layout()
plt.show()

# Scatter: qty_dispensed vs package_qty
plt.scatter(df_inventory['package_qty'], df_inventory['qty_dispensed'], alpha=0.6)
plt.xlabel('package_qty'); plt.ylabel('qty_dispensed')
plt.title('Dispensed vs In‐Stock')
plt.show()

"""Inventory histogram: quantity‐dispensed is heavily right‐skewed, with the vast majority of events under 20 units.
A handful of events exceed 100 units and should be flagged for potential outlier handling.

Restock histogram: Total restocked per transaction is closer to a normal distribution centered around ~250–300 units, though a few restocks exceed 500.
We might treat those as high‐volume replenishments but they are not as extreme as the dispense outliers

The “Quantity Dispensed” boxplot is heavily right-skewed: most daily dispense events fall roughly in the 40–110 range, but there are a large number of high outliers extending past 150. In other words, although a typical machine dispenses on the order of tens of units a day, occasionally there are very large single-day spikes.

The “Total Restocked” boxplot is more symmetric (centered around roughly 200–350 units) but still shows some high outliers near 600. This tells us that most restock shipments are a few hundred units at a time, with only a handful of unusually large replenishments.

Scatter plot: Over 99 % of dispense‐actions request exactly one package,
yet the actual units dispensed in those single‐package events range from 1 up to >150.
In other words, package_qty by itself does not strongly predict the numeric volume dispensed
"""

# 3d. Date based exploration

import matplotlib.pyplot as plt

# monthly counts
inv_monthly = df_inventory['dispense_date'].dt.to_period('M') \
                        .value_counts().sort_index()
rest_monthly = df_restock['restock_date'].dt.to_period('M') \
                        .value_counts().sort_index()

# rolling stats
inv_rm = inv_monthly.rolling(3).mean()
inv_rs = inv_monthly.rolling(3).std()

rest_rm = rest_monthly.rolling(3).mean()
rest_rs = rest_monthly.rolling(3).std()


# 1) Dispenses — line + rolling stats
plt.figure(figsize=(8,3))
inv_monthly.plot(label='Monthly Dispenses')
inv_rm.plot(label='3-Mo Rolling Mean', linestyle='--')
inv_rs.plot(label='3-Mo Rolling Std',    linestyle=':')
plt.title('Dispenses per Month (with Rolling Stats)')
plt.xlabel('Month')
plt.ylabel('Count')
plt.legend()
plt.tight_layout()
plt.show()


# 2) Restocks — line + rolling stats
plt.figure(figsize=(8,3))
rest_monthly.plot(label='Monthly Restocks')
rest_rm.plot(label='3-Mo Rolling Mean', linestyle='--')
rest_rs.plot(label='3-Mo Rolling Std',    linestyle=':')
plt.title('Restocks per Month (with Rolling Stats)')
plt.xlabel('Month')
plt.ylabel('Count')
plt.legend()
plt.tight_layout()
plt.show()

"""Dispenses: There is a clear seasonal cycle: a big summer peak (~July), then a sharp drop in January, and a muted, steadier plateau for the rest of the year
The early-2023 months (Jan–Mar) stand out as unusually volatile—both mean and standard deviation spiked—so a forecasting model will need to handle that transition (e.g., a structural break or extra volatility term)

Restocks: Restocks also exhibit a seasonal build-up in spring 2023 (similar to how dispenses spiked in summer 2022).
After a few months of “learning the pattern,” restock counts stabilize around 60–65/month, with very low volatility (rolling std near 0–5).
The small February 2024 spike—followed by a March drop—hints at a minor seasonal tweak but doesn’t come close to the large January 2023 disruption seen on the dispense side.


Instant Insight (Dispenses):

We see a clear mid-2022 peak (1 900/month), followed by a sharp January 2023 drop (800/month).
After March 2023, volume flattens into a stable \~900–1 600 range with low volatility.

Instant Insight (Restocks):

Restocks begin in March 2023 at \~15/mo, ramp to \~60–65/mo by mid-2023, and then largely stabilize.
Volatility is low after June 2023 (rolling std ≈ 0–5), so restocking has become predictable.

"""

# Need to check if data is stationary

from statsmodels.tsa.stattools import adfuller

# --- run the tests on the numeric series only ---
adft_inventory = adfuller(df_inventory['qty_dispensed'], autolag="AIC")
adft_restock   = adfuller(df_restock['total'],         autolag="AIC")

# --- common metric labels ---
metrics = [
    "Test Statistic",
    "p-value",
    "No. of lags used",
    "Number of observations used",
    "Crit. Val. (1%)",
    "Crit. Val. (5%)",
    "Crit. Val. (10%)"
]

# --- build your two result DataFrames ---
output_inventory = pd.DataFrame({
    "Metric": metrics,
    "Value": [
        adft_inventory[0],
        adft_inventory[1],
        adft_inventory[2],
        adft_inventory[3],
        adft_inventory[4]["1%"],
        adft_inventory[4]["5%"],
        adft_inventory[4]["10%"],
    ]
})

output_restock = pd.DataFrame({
    "Metric": metrics,
    "Value": [
        adft_restock[0],
        adft_restock[1],
        adft_restock[2],
        adft_restock[3],
        adft_restock[4]["1%"],
        adft_restock[4]["5%"],
        adft_restock[4]["10%"],
    ]
})

print("ADF Test — Inventory Series")
print(output_inventory, "\n")

print("ADF Test — Restock Series")
print(output_restock)

"""The p-values are both less than 0.01 so both series strongly reject the unit‐root null hypothesis and so can be treated as stationary"""

# Checking for autocorrelation

# 1) Build true monthly‐quantity series
inv_monthly_qty = (
    df_inventory
      .set_index('dispense_date')
      .resample('ME')['qty_dispensed']
      .sum()
)
rest_monthly_qty = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']
      .sum()
)

# 2) Compute only quantity‐based autocorrelations at 1, 3, 6 and 9 months
for name, series in [
    ('Inventory (qty)', inv_monthly_qty),
    ('Restock   (qty)', rest_monthly_qty),
]:
    print(f"{name} autocorrelations:")
    for lag in [1, 3, 6, 9]:
        ac = series.autocorr(lag=lag)
        print(f"  {lag}-month lag: {ac:.3f}")
    print()

"""There is a strong positive autocorrelation at lag = 1 (short‐term persistence).
There is a flip to negative values around lags = 6–9, highlighting a clear annual seasonality.
Any ARIMA/SARIMA (or seasonal regression) should include at least a seasonal lag of 12 and potentially seasonal differencing) to capture the fact that “busy months tend to be offset by slow months roughly nine–twelve months later.”
"""

# Looking into lag features

import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# 1) Build true monthly‐quantity series
inv_monthly_qty = (
    df_inventory
      .set_index('dispense_date')
      .resample('ME')['qty_dispensed']
      .sum()
)
rest_monthly_qty = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']
      .sum()
)

# 2) Determine max lags per series
max_acf_inv  = min(24, len(inv_monthly_qty)  - 1)
max_pacf_inv = min(max_acf_inv, (len(inv_monthly_qty)//2) - 1)

max_acf_rest  = min(24, len(rest_monthly_qty)  - 1)
max_pacf_rest = min(max_acf_rest, (len(rest_monthly_qty)//2) - 1)

# 3) Plot for Inventory
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
plot_acf(inv_monthly_qty, lags=max_acf_inv, ax=axes[0],
         title=f'Inventory Qty ACF ({max_acf_inv} lags)')
plot_pacf(inv_monthly_qty, lags=max_pacf_inv, ax=axes[1],
          title=f'Inventory Qty PACF ({max_pacf_inv} lags)')
plt.tight_layout()
plt.show()

# 4) Plot for Restock
fig, axes = plt.subplots(2, 1, figsize=(10, 6))
plot_acf(rest_monthly_qty, lags=max_acf_rest, ax=axes[0],
         title=f'Restock Qty ACF ({max_acf_rest} lags)')
plot_pacf(rest_monthly_qty, lags=max_pacf_rest, ax=axes[1],
          title=f'Restock Qty PACF ({max_pacf_rest} lags)')
plt.tight_layout()
plt.show()

"""Both series show a large spike at lag 1 in PACF (inventory ≈ 0.53, restock ≈ 0.25). A simple AR(1) term captures most short-term momentum.

ACF becomes strongly negative around lags 6–9, then flips positive again at lag 12. A 12-month seasonal component is required.

Negative ACF around lag 7–9 indicates a mid-year trough following high-volume months. Expect busy spring months to be followed by quieter fall months.

Inventory lag 1 ACF (~ 0.63) is much larger than restock lag 1 (~ 0.25). Inventory is more “sticky” month-to-month; restocks are less so.
"""

from statsmodels.tsa.seasonal import seasonal_decompose

# Inventory (12-month seasonality)
decomp_inv = seasonal_decompose(inv_monthly_qty, model='additive', period=12)
fig = decomp_inv.plot()
fig.set_size_inches(10, 8)
fig.suptitle('Inventory Qty Decomposition (12-month)', y=1.02)
plt.tight_layout()
plt.show()

# Restock (6-month seasonality)
decomp_rest = seasonal_decompose(rest_monthly_qty, model='additive', period=6)
fig = decomp_rest.plot()
fig.set_size_inches(10, 8)
fig.suptitle('Restock Qty Decomposition (6-month)', y=1.02)
plt.tight_layout()
plt.show()

"""Inventory Trend: Clear upward trajectory from early 2022 into late-2022/early-2023, followed by a steady decline through 2023.
Suggests demand peaked north of 20 k units/month around Jan ’23, then tapered toward ~10 k by mid-2023.

Inventory Seasonality: Strong positive seasonal peaks around mid-year (July/August) and again at year-end, with deep negative deviations in late winter (Feb/March).
Implies consistent summertime/wintertime surges, with off-peak slumps each spring.

Inventory Residuals: One large positive spike around September ’23 (actual >> expected), and a notable negative anomaly in August ’23 (actual << expected).
Points to one-off events (e.g., promotions or stockouts) that drove volume well outside normal seasonal/trend patterns.

Restock Trend: Gradual increase from spring ’23 into late ’23, peaking around Nov ’23 (~18 k units), then dipping in early ’24.
Indicates restocking ramped up through fall, then pulled back slightly as inventory demand softened.

Restock Seasonality: Seasonal highs in mid-year (July) and turn-of-year (Jan ’24), with pronounced troughs around April and October.
Suggests biannual restock campaigns—heavy summer and year-end replenishment, lighter in spring and early fall.

Restock Residuals: A large negative outlier in July ’23 (actual restock << expected), and a sharp positive outlier in January ’24.
May reflect supply-chain disruptions mid-year and an end-of-year push to top off stock.
"""

# Step 4 Feature Engineering

# Create Daily Level Inventory Table
daily_inventory = (
    df_inventory
      .groupby(['device_id', df_inventory['dispense_date'].dt.date])
      .agg(qty_dispensed=('qty_dispensed','sum'))
      .reset_index()
      .rename(columns={'dispense_date':'date'})
)

# Now add calendar fields
daily_inventory['date']         = pd.to_datetime(daily_inventory['date'])
daily_inventory['day_of_week']  = daily_inventory['date'].dt.dayofweek        # 0=Mon … 6=Sun
daily_inventory['is_weekend']   = daily_inventory['day_of_week'].isin([5,6]).astype(int)
daily_inventory['day_of_month'] = daily_inventory['date'].dt.day
daily_inventory['month']        = daily_inventory['date'].dt.month
daily_inventory['quarter']      = daily_inventory['date'].dt.quarter
daily_inventory['year']         = daily_inventory['date'].dt.year

print(daily_inventory)

# Create Daily Level Inventory Table
daily_restock = (
    df_restock
      .groupby(['device_id', df_restock['restock_date'].dt.date])
      .agg(total_restocked=('total','sum'))
      .reset_index()
      .rename(columns={'restock_date':'date'})
)

# Now add calendar fields
daily_restock['date']         = pd.to_datetime(daily_restock['date'])
daily_restock['day_of_week']  = daily_restock['date'].dt.dayofweek
daily_restock['is_weekend']   = daily_restock['day_of_week'].isin([5,6]).astype(int)
daily_restock['day_of_month'] = daily_restock['date'].dt.day
daily_restock['month']        = daily_restock['date'].dt.month
daily_restock['quarter']      = daily_restock['date'].dt.quarter
daily_restock['year']         = daily_restock['date'].dt.year

print(daily_restock.head())
print(daily_restock.dtypes)

# Both data frames have been updated with new datetime features

# Add lag features

import pandas as pd

# --- 0) Rebuild daily_inventory / daily_restock to guarantee a proper 'date' column ---
# (We assume df_inventory has a datetime column 'dispense_date',
#  and df_restock has a datetime column 'restock_date'.)

# 0A) Daily Inventory: one row per (device_id, date), with qty_dispensed summed
daily_inventory = (
    df_inventory
      .assign(date=df_inventory['dispense_date'].dt.normalize())   # extract just the date (no time)
      .groupby(['device_id', 'date'], as_index=False)
      .agg(qty_dispensed=('qty_dispensed', 'sum'))
)

# 0B) Daily Restock: one row per (device_id, date), with total_restocked summed
daily_restock = (
    df_restock
      .assign(date=df_restock['restock_date'].dt.normalize())
      .groupby(['device_id', 'date'], as_index=False)
      .agg(total_restocked=('total', 'sum'))
)

# Now both daily_inventory and daily_restock have a true datetime64[ns] column named "date".


# --- 1) Build true monthly‐quantity series from each daily table ---

# 1A) Inventory: sum qty_dispensed per calendar‐month (month‐end as index)
inv_monthly = (
    daily_inventory
      .set_index('date')                       # make 'date' the index
      .resample('ME')[['qty_dispensed']]       # 'ME' = month‐end
      .sum()
      .rename(columns={'qty_dispensed':'dispensed_qty'})
      .sort_index()
)

# 1B) Restock: sum total_restocked per calendar‐month
rest_monthly = (
    daily_restock
      .set_index('date')                       # make 'date' the index
      .resample('ME')[['total_restocked']]     # 'ME' = month‐end
      .sum()
      .rename(columns={'total_restocked':'monthly_restocked_qty'})
      .sort_index()
)


# --- 2) Create lagged and rolling‐window features on the monthly series ---

# 2A) Inventory lags + rolling stats
inv_monthly['lag_1']       = inv_monthly['dispensed_qty'].shift(1)
inv_monthly['lag_3']       = inv_monthly['dispensed_qty'].shift(3)
inv_monthly['lag_12']      = inv_monthly['dispensed_qty'].shift(12)

inv_monthly['roll_mean_3'] = (
    inv_monthly['dispensed_qty']
      .rolling(window=3, min_periods=1)
      .mean()
)
inv_monthly['roll_std_3']  = (
    inv_monthly['dispensed_qty']
      .rolling(window=3, min_periods=1)
      .std()
)

inv_monthly['roll_mean_12'] = (
    inv_monthly['dispensed_qty']
      .rolling(window=12, min_periods=1)
      .mean()
)
inv_monthly['roll_std_12']  = (
    inv_monthly['dispensed_qty']
      .rolling(window=12, min_periods=1)
      .std()
)

# 2B) Restock lags + rolling stats
rest_monthly['lag_1']       = rest_monthly['monthly_restocked_qty'].shift(1)
rest_monthly['lag_3']       = rest_monthly['monthly_restocked_qty'].shift(3)
rest_monthly['lag_12']      = rest_monthly['monthly_restocked_qty'].shift(12)

rest_monthly['roll_mean_3'] = (
    rest_monthly['monthly_restocked_qty']
      .rolling(window=3, min_periods=1)
      .mean()
)
rest_monthly['roll_std_3']  = (
    rest_monthly['monthly_restocked_qty']
      .rolling(window=3, min_periods=1)
      .std()
)

rest_monthly['roll_mean_12'] = (
    rest_monthly['monthly_restocked_qty']
      .rolling(window=12, min_periods=1)
      .mean()
)
rest_monthly['roll_std_12']  = (
    rest_monthly['monthly_restocked_qty']
      .rolling(window=12, min_periods=1)
      .std()
)


# --- 3) Merge those monthly features back onto the daily tables ---

# 3A) Create a 'month_end' column in each daily table so we can join on month‐end
daily_inventory['month_end'] = (
    daily_inventory['date']
      .dt.to_period('M')
      .dt.to_timestamp('M')
)
daily_restock['month_end'] = (
    daily_restock['date']
      .dt.to_period('M')
      .dt.to_timestamp('M')
)

# 3B) Left‐merge inv_monthly onto daily_inventory (on month_end)
daily_inventory = daily_inventory.merge(
    inv_monthly,
    how='left',
    left_on='month_end',
    right_index=True
)

# 3C) Left‐merge rest_monthly onto daily_restock (on month_end)
daily_restock = daily_restock.merge(
    rest_monthly,
    how='left',
    left_on='month_end',
    right_index=True
)

# (Optional) Drop the helper 'month_end' if you don’t need it anymore:
# daily_inventory.drop(columns=['month_end'], inplace=True)
# daily_restock.drop(columns=['month_end'], inplace=True)


# --- 4) Sanity check: confirm that the new columns appear correctly ---

print("=== daily_inventory with lag/rolling features ===")
print(daily_inventory.head(10))
print(daily_inventory.columns.tolist())

print("\n=== daily_restock with lag/rolling features ===")
print(daily_restock.head(10))
print(daily_restock.columns.tolist())

import numpy as np

# --- Ensure day_of_week and month exist on daily_inventory ---
# (Recompute them from the 'date' column so we know they’re there.)
daily_inventory['day_of_week']  = daily_inventory['date'].dt.dayofweek
daily_inventory['month']        = daily_inventory['date'].dt.month

# Now compute the four cyclical features
daily_inventory['dow_sin'] = np.sin(2 * np.pi * daily_inventory['day_of_week'] / 7)
daily_inventory['dow_cos'] = np.cos(2 * np.pi * daily_inventory['day_of_week'] / 7)
daily_inventory['m_sin']   = np.sin(2 * np.pi * (daily_inventory['month'] - 1) / 12)
daily_inventory['m_cos']   = np.cos(2 * np.pi * (daily_inventory['month'] - 1) / 12)

print(daily_inventory[['date','day_of_week','month','dow_sin','dow_cos','m_sin','m_cos']].head())


# --- Ensure daily_inventory has a column named "date" too ---
if "date" not in daily_inventory.columns:
    if "dispense_date" in daily_inventory.columns:
        daily_inventory = daily_inventory.rename(columns={"dispense_date": "date"})
    else:
        raise KeyError("daily_inventory must have either 'date' or 'dispense_date'.")

daily_inventory["date"] = pd.to_datetime(daily_inventory["date"])
daily_inventory["day_of_week"] = daily_inventory["date"].dt.dayofweek
daily_inventory["month"]       = daily_inventory["date"].dt.month

daily_inventory["dow_sin"] = np.sin(2 * np.pi * daily_inventory["day_of_week"] / 7)
daily_inventory["dow_cos"] = np.cos(2 * np.pi * daily_inventory["day_of_week"] / 7)
daily_inventory["m_sin"]   = np.sin(2 * np.pi * (daily_inventory["month"] - 1) / 12)
daily_inventory["m_cos"]   = np.cos(2 * np.pi * (daily_inventory["month"] - 1) / 12)

print(daily_inventory[["date","day_of_week","month","dow_sin","dow_cos","m_sin","m_cos"]].head())

# Looking for some insights with new datetime features

# Make sure daily_inventory has day_of_week, is_weekend, day_of_month, month
daily_inventory['day_of_week']  = daily_inventory['date'].dt.dayofweek     # 0=Mon … 6=Sun
daily_inventory['is_weekend']   = daily_inventory['day_of_week'].isin([5,6]).astype(int)
daily_inventory['day_of_month'] = daily_inventory['date'].dt.day
daily_inventory['month']        = daily_inventory['date'].dt.month

# Same for daily_restock:
if daily_restock.index.name == 'date':
    daily_restock = daily_restock.reset_index()

daily_restock['day_of_week']     = daily_restock['date'].dt.dayofweek
daily_restock['is_weekend']      = daily_restock['day_of_week'].isin([5,6]).astype(int)
daily_restock['day_of_month']    = daily_restock['date'].dt.day
daily_restock['month']           = daily_restock['date'].dt.month


# insights from daily_inventory
print('Quantity Dispensed on Weekends:', daily_inventory.groupby('is_weekend')['qty_dispensed'].mean())
print('\nQuantity Dispensed by Day of Week:', daily_inventory.groupby('day_of_week')['qty_dispensed'].mean())
print('\nQuantity Dispensed by Day of Month:', daily_inventory.groupby('day_of_month')['qty_dispensed'].mean())
print('\nQuantity Dispense by Month:', daily_inventory.groupby('month')['qty_dispensed'].mean())

# insights from daily_restock
print('\nTotal Restocked on Weekends:', daily_restock.groupby('is_weekend')['total_restocked'].mean())
print('\nTotal Restocked by Day of Week:', daily_restock.groupby('day_of_week')['total_restocked'].mean())
print('\nTotal Restocked by Day of Month:', daily_restock.groupby('day_of_month')['total_restocked'].mean())
print('\nTotal Restocked by Month:', daily_restock.groupby('month')['total_restocked'].mean())

"""Weekday vs. Weekend Dispensing: Weekday average (89 units/day) is only slightly higher than weekend (83 units/day). In other words, usage is fairly consistent seven days a week—there isn’t a huge drop-off on Saturdays/Sundays.

Day-of-Week Dispensing Pattern: Mondays (day\_of\_week=0) see the highest average (97 units), while Fridays (4) and Saturdays (5) dip to the mid-70s. Mid-week (Tues–Thurs) sits around 88–91 units. This suggests a “Monday pickup” and a “Friday/Saturday lull.”

Day-of-Month Dispensing: The 12th of each month is noticeably high (101 units), and the 23rd and 31st drop to 77 units. Most other days cluster around 85–90 units. So there’s a modest bump around mid-month (around the 12th) and troughs at month-end (23rd & 31st).

Monthly Dispensing Trends: December (12) is the busiest average (108 units/day). February (2) is quietest (69 units/day). There’s a steady ramp from Feb → Dec, peaking in Q4.

Weekday vs. Weekend Restocking: Restocks average 285 units on weekdays vs. 235 on weekends. So restock activity drops about 20% on weekends.

Day-of-Week Restocking: Mondays (0) see the highest average restock (334 units), while Thursdays (3) are lowest (189 units). In other words, most fill-ups happen early in the week.

Day-of-Month Restocking: The 5th (350 units) and 9th (342 units) have the highest average restocks; the 1st (230) and 2nd (281) are lighter. No extreme “end-of-month” spike—instead it’s more spread out around days 4–9.

Monthly Restocking Patterns: May (5) is peak restock (404 units/day), whereas February (2) is lowest (236 units/day). There’s a strong ramp from Q1 → May, then a slight dip in summer, and a secondary bump around January.

Aggregating to daily totals doesn’t fundamentally alter the fact that both dispensing and restocking are right‐skewed and punctuated by occasional high‐volume days.
The only “new” insight here is that those extreme values aren’t just large individual transactions—they’re genuinely high‐demand (or high‐fill) days.
Everything else (central tendency, spread, long‐tail behavior) remains essentially the same once you move from per‐transaction to per‐day.
"""

# convert date into the index
daily_inventory.index = daily_inventory['date']
del daily_inventory['date']
print(daily_inventory.head())

daily_restock.index = daily_restock['date']
del daily_restock['date']
print(daily_restock.head())

# Trends and Seasonality Analysis: Analyze the total quantity dispensed and restocked over time to identify any visible trends or seasonal patterns.

# Top 20 SKUs dispensed
sku_totals = (
    df_inventory
      .groupby('sku')['qty_dispensed']
      .sum()
      .sort_values(ascending=False)
)
print(sku_totals.head(20))

# Top 20 SKUs restocked
sku_restocked_totals = (
    df_restock
      .groupby('device_id')['total']
      .sum()
      .sort_values(ascending=False)
)
print(sku_restocked_totals.head(20))

"""Top SKUs by Total Units Dispensed
The single highest‐turnover SKU (b1cfc8c80d03027941b0bce8d2ff3deb) has moved 21,845 units, roughly 25% more than the next best.

Five SKUs (b1cfc8c8…, be61be55…, 93d664dd…, 9a154810…, da3562c5…) each exceed 14,000 units, indicating a classic “80/20” demand curve: a small handful of SKUs drive most movement.

Beyond the top 10, there’s a long tail of lower‐volume SKUs (for example, rank 20 is under 6,000 units). This suggests significant SKU diversity with a heavy concentration at the top.

Top Devices by Total Restocked
Device\_af645ebf4c96eb6e430529a2a9913686 leads all machines with 44,832.09 restocked—about 8% more than the #2 device—highlighting one particularly active location.

The top four devices each exceed 37K in restock value; beyond that, the drop‐off is steep (the 5th device is at 32K). Again, restocking effort is highly concentrated among a few machines.

Those top‐5 machines together account for roughly 60–65% of total restock dollars, suggesting that focusing on these “high‐throughput” sites could yield outsized inventory‐optimization gains.

Combined Takeaways
Both SKU and device distributions exhibit a strong “heavy‐head/long‐tail” pattern: a small subset of SKUs and machines drive the majority of activity.

Aligning the top SKUs with each top device (for example, does device\_af645ebf4c96eb6e430529a2a9913686 stock predominantly the top‐3 SKUs?) could uncover whether demand concentration is uniform across locations or driven by local preferences.

From an inventory‐planning perspective, it may make sense to prioritize forecasting accuracy and safety‐stock for the top \~10 SKUs and top \~5 machines before optimizing the long tail.

"""

# Trends and Seasonality Analysis:
# Analyze the total quantity dispensed and restocked over time to identify any visible trends or seasonal patterns.

# 0) Ensure your dispense_date/restock_date columns are datetime
df_inventory['dispense_date'] = pd.to_datetime(df_inventory['dispense_date'])
df_restock  ['restock_date']  = pd.to_datetime(df_restock['restock_date'])

# 1) Build monthly‐quantity series

# Inventory (qty_dispensed per month, month‐end index)
inv_monthly_qty = (
    df_inventory
      .set_index('dispense_date')           # ensure 'dispense_date' is datetime64
      .resample('ME')['qty_dispensed']      # 'ME' = Month End
      .sum()
      .sort_index()
)

# Restock (total restocked per month, month‐end index)
rest_monthly_qty = (
    df_restock
      .set_index('restock_date')            # ensure 'restock_date' is datetime64
      .resample('ME')['total']              # 'ME' = Month End
      .sum()
      .sort_index()
)


# 2) Plot raw monthly totals + 3-month rolling statistics

# Inventory plot
inv_roll_mean3 = inv_monthly_qty.rolling(window=3).mean()
inv_roll_std3  = inv_monthly_qty.rolling(window=3).std()

plt.figure(figsize=(10, 4))
plt.plot(inv_monthly_qty.index, inv_monthly_qty, marker='o', linewidth=1, label='Raw Monthly Dispensed')
plt.plot(inv_roll_mean3.index,  inv_roll_mean3,   linestyle='--', linewidth=2, label='3-Month Rolling Mean')
plt.fill_between(
    inv_roll_mean3.index,
    inv_roll_mean3 - inv_roll_std3,
    inv_roll_mean3 + inv_roll_std3,
    color='gray', alpha=0.2, label='±1 Std Dev (3-month)'
)
plt.title("Inventory: Qty Dispensed per Month\n(with 3-Month Rolling Mean & Std Dev)")
plt.xlabel("Month")
plt.ylabel("Units Dispensed")
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()


# Restock plot
rest_roll_mean3 = rest_monthly_qty.rolling(window=3).mean()
rest_roll_std3  = rest_monthly_qty.rolling(window=3).std()

plt.figure(figsize=(10, 4))
plt.plot(rest_monthly_qty.index, rest_monthly_qty, marker='o', linewidth=1, color='C1', label='Raw Monthly Restocked')
plt.plot(rest_roll_mean3.index,  rest_roll_mean3,   linestyle='--', linewidth=2, color='C2', label='3-Month Rolling Mean')
plt.fill_between(
    rest_roll_mean3.index,
    rest_roll_mean3 - rest_roll_std3,
    rest_roll_mean3 + rest_roll_std3,
    color='lightcoral', alpha=0.2, label='±1 Std Dev (3-month)'
)
plt.title("Restock: Qty Restocked per Month\n(with 3-Month Rolling Mean & Std Dev)")
plt.xlabel("Month")
plt.ylabel("Units Restocked")
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()


# 3) Decompose each series into Trend / Seasonal / Residual

# 3A) Inventory decomposition (12-month period)
decomp_inv = seasonal_decompose(inv_monthly_qty, model='additive', period=12)

fig = decomp_inv.plot()
fig.set_size_inches(10, 8)
fig.suptitle("Inventory Qty Dispensed Decomposition (12-Month Period)", y=1.02)
plt.tight_layout()
plt.show()


# 3B) Restock decomposition (6-month period, since we have ~13 monthly points)
decomp_rest = seasonal_decompose(rest_monthly_qty, model='additive', period=6)

fig = decomp_rest.plot()
fig.set_size_inches(10, 8)
fig.suptitle("Restock Qty Restocked Decomposition (6-Month Period)", y=1.02)
plt.tight_layout()
plt.show()

"""Inventory (Qty Dispensed per Month)
The raw monthly series spikes around mid-2022 (18-20k) before dipping sharly in early 2023 (~8k) and then gradually recovers to ~12K by early 2024.


The 3-month rolling mean (orange dashed) smooths that early-2023 drop and shows a clear downward shift in trend from summer 2022 to spring 2023, followed by a mild upward recovery.

The ±1 std dev (gray shaded) is narrow in periods of low volatility (mid-2023) and widens around mid-2022 and early 2024, indicating higher month-to-month variability in those periods.

Seasonal Decomposition (12-month):

Trend component steadily declines from ~15.5K in late 2022 to ~10.3K by August 2023, then flattens around ~10.5–12K through early 2024.

Seasonal component peaks (≈ +5K) around July–August and troughs (≈ –5K) around February–March, confirming strong summer demand and winter lull.

Residuals are small except one outlier (~ +1K) in September 2022 and one negative (~ –800) in August 2023, suggesting those months deviated unusually from expected patterns.

Restock (Qty Restocked per Month)
The raw restock series rises from ~5.3K in March 2023 to ~18.5K by January 2024, then dips to ~10K by April 2024.

The 3-month rolling mean (green dashed) captures a gradual upward trend through late 2023 before declining into spring 2024.

The ±1 std dev band (pink shaded) is widest around mid-2023 (June–July) and early 2024 (Feb–Mar), indicating those months had more erratic restock volumes.

Seasonal Decomposition (6-month):

Trend component climbs from ~15.2K in June 2023 to ~17.2K by November 2023, then dips to ~16.3K by January 2024 before falling to ~10K in April 2024.

Seasonal component shows a clear mid-year high (+1.2K around July 2023 and Jan 2024) and a mid-winter/early-spring trough (–1K around October 2023), indicating restocks peak in summer and again in early winter.

Residuals are small except one large negative (~ –1.3K) in June 2023 and one large positive (~ +800) in January 2024, signaling unusual restock fluctuations those months.
"""

# 1) Compute total units dispensed per SKU, then sort descending
# done in previous cell

# 2) Plot the top 10 SKUs as a horizontal bar chart
import matplotlib.pyplot as plt

TOP_N = 10
top_sku_totals = sku_totals.head(TOP_N)

plt.figure(figsize=(8, 5))
top_sku_totals.sort_values().plot(
    kind='barh',
    color='C3',
    edgecolor='black'
)
plt.title(f"Top {TOP_N} SKUs by Total Units Dispensed")
plt.xlabel("Total Units Dispensed")
plt.ylabel("SKU")
plt.gca().invert_yaxis()   # so the highest one appears at the top
plt.tight_layout()
plt.show()


# 3) Build a “monthly_by_sku” DataFrame for those top SKUs
#    — first create a Year‐Month period column
df_inventory['year_month'] = df_inventory['dispense_date'].dt.to_period('M')

#    — filter to only keep the top N SKUs
top_skus = top_sku_totals.index.tolist()
inv_top = df_inventory[df_inventory['sku'].isin(top_skus)].copy()

#    — group by [year_month, sku], sum qty_dispensed, then unstack so that each column is one SKU
monthly_by_sku = (
    inv_top
      .groupby(['year_month', 'sku'])['qty_dispensed']
      .sum()
      .unstack(fill_value=0)
)

# Convert the index back to Timestamp (month end) for easier plotting on the x‐axis
monthly_by_sku.index = monthly_by_sku.index.to_timestamp()

print("\n=== Monthly Demand for Top SKUs (first few rows) ===")
print(monthly_by_sku.head())


# 4) Plot each top SKU’s monthly series on a single chart
plt.figure(figsize=(10, 5))
for sku in top_skus:
    plt.plot(
        monthly_by_sku.index,
        monthly_by_sku[sku],
        marker='o',
        label=sku
    )

plt.title(f"Monthly Units Dispensed for Top {TOP_N} SKUs")
plt.xlabel("Month")
plt.ylabel("Units Dispensed")
plt.legend(title="SKU", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# 5) Compute and display each top SKU’s “average by calendar‐month”
#    to highlight seasonality. This creates a 12×TOP_N table of typical January→December demand.

# Add an integer “month_of_year” column (1–12)
monthly_by_sku['month_of_year'] = monthly_by_sku.index.month

# Group by month_of_year and take the mean across all years
sku_monthly_means = (
    monthly_by_sku
      .groupby('month_of_year')
      .mean()
)

print("\n=== Average Monthly Demand (Jan→Dec) for Each Top SKU ===")
print(sku_monthly_means)

# 6) Plot“seasonal index” curves
plt.figure(figsize=(8, 5))
for sku in top_skus:
    plt.plot(
        sku_monthly_means.index,
        sku_monthly_means[sku],
        marker='o',
        label=sku
    )

plt.title("Seasonal Profile: Average Units/Month for Each Top SKU")
plt.xlabel("Month of Year")
plt.xticks(range(1, 13))   # show 1 through 12
plt.ylabel("Avg. Units Dispensed")
plt.legend(title="SKU", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()

"""Concentration of Volume in a Few SKUs
The top 10 SKUs together account for a large share of total units dispensed, with the #1 SKU moving roughly 21,845 units—about 20% more than the #2 SKU. The 10th­highest SKU is already down at ~10,800 units, confirming a classic “long tail” where a handful of SKUs dominate overall consumption.

Mid-Year Demand Spike for Most High-Volume SKUs
In the line plot of each top-10 SKU’s monthly series, nearly every SKU peaks between June and August (e.g., SKU “be61be55…” surges to ~1,560 units in July 2022, and “b1cfc8c8…” peaks around 1,415 in November 2022 but is still strong in summer). This mid-year lift suggests a pronounced summer/fall surge in demand.

Low-Demand Lull around Year-End/Start
Almost all top SKUs dip sharply in early 2023 (January–March), often to less than half of their mid-year volumes. That 2022→2023 trough appears more severe than in preceding or subsequent winters—likely reflecting a one-time event (e.g., pandemic lull, supply constraints, or seasonality shift).

Consistent Winter “Second Peak” for Some SKUs
While most SKUs bottom out in Q1, a subset (for example, “9a154810…” and “93d664dd…”) rebounded strongly around November–December 2022, forming a secondary winter spike. That pattern is not universal—some SKUs stay flat through Nov/Dec—indicating different calendar‐month sensitivities across SKUs.

Seasonal Profile (Jan→Dec) Highlights SKU-Level Differences
The “average by calendar month” chart shows that:

b1cfc8c8… (top SKU) climbs steadily from ~433 in February to ~1,193 in December. Its highest months are July–December, indicating it sees both a big summer bump and a year-end tail.

be61be55… and 9a154810… also crescendo into July/August (peaking ~1,041 and ~778 respectively) but then dip again in September before rallying into year-end.

05d98e5c2… (rank 9) is much more muted: ~412–583 units in summer, but only ~274 in February, demonstrating that even #9 has ~2× swing from low to high.

The lowest‐volume among the top 10 (e.g., “78baaa…” at ~195 in February → ~580 in December) still has a >2× seasonal swing—so every leading SKU is strongly seasonal.

Implications for Restocking Strategy

Inventory Safety Stock should be highest in June–August for nearly all top SKUs, then kept relatively low in February–March.

SKUs with a distinct winter bump (e.g., “9a154810…” and “93d664dd…”) may require a small secondary order in November/December to catch that uptick rather than waiting until spring.

During the January–March “lull,” restocking could be deprioritized for most SKUs to free up capital and warehouse space.

Overall Takeaway

A small handful of SKUs dominate volume, and they all exhibit strong seasonal cycles, with high demand in summer, a sharp Q1 trough, and—depending on the SKU—either a flat or secondary lift in late year.

Any predictive model should therefore include a 12-month seasonal dummy (or Fourier term) plus a trend-adjustment to capture the mid-year peaks and winter recovery.

Operationally, prioritizing summer restocking for these top SKUs—and scheduling a smaller holiday shipment for those that rebound in November–December—will drive the greatest ROI.
"""

# Correlation Analysis: Explore correlations between the quantity dispensed and restock frequency or cost.
# This is

# 1) Build a true “monthly quantity dispensed” series (month‐end index)
inv_monthly_qty = (
    df_inventory
      .set_index('dispense_date')             # ensure datetime index
      .resample('ME')['qty_dispensed']        # ‘ME’ = month‐end
      .sum()
      .sort_index()
)

# 2) Build a “monthly restock frequency” series (count of rows per month)
rest_monthly_freq = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']                # we’re simply counting rows, so pick any column
      .count()
      .rename('restock_frequency')
      .sort_index()
)

# 3) Build a “monthly restock cost” series (sum of total$ per month)
rest_monthly_cost = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']
      .sum()
      .rename('restock_cost')
      .sort_index()
)

# 4) Merge all three into one DataFrame (outer‐join to keep months that appear only in one series)
monthly = (
    pd.concat([inv_monthly_qty.rename('dispensed_qty'),
               rest_monthly_freq,
               rest_monthly_cost],
              axis=1)
      .fillna(0)  # if a month had zero restocks or zero dispenses, fill with 0
)

# 5) Compute the Pearson‐correlation matrix
corr_matrix = monthly[['dispensed_qty','restock_frequency','restock_cost']].corr()
print("=== Correlation Matrix ===")
print(corr_matrix)

# 6) If you want the two specific pairwise correlations, you can extract them:
print()
print(f"Correlation(dispensed_qty, restock_frequency) = "
      f"{corr_matrix.loc['dispensed_qty','restock_frequency']:.3f}")
print(f"Correlation(dispensed_qty, restock_cost)      = "
      f"{corr_matrix.loc['dispensed_qty','restock_cost']:.3f}")

"""Moderate Negative Relationship with Restocks
• Quantity dispensed and restock frequency correlate at –0.493, and with restock cost at –0.482.
• When more is dispensed, fewer restocking events (and lower cost) tend to follow that same month—and vice versa.

Restock Frequency vs. Cost (Redundant Signal)
• Restock frequency and restock cost correlate at +0.983, indicating that months with many restock events also incur higher total restock spend.
• For modeling purposes, you probably only need one of those two (frequency or cost), since they carry nearly identical information.

Implication for Demand–Supply Timing
• Negative correlation suggests a “rebound” effect: high dispensing months are typically followed by months with fewer restocks (lower restock frequency/cost), whereas low‐dispense months precede busy restocking.
• That lagged pattern could inform an ARIMAX or transfer‐function approach, where past dispensing drives future restock behavior (or vice versa).
"""

# Corrleation analysis with a 1 month lag on restock

# 1) build the three monthly series (exactly as you already have)
inv_monthly_qty   = (
    df_inventory
      .set_index('dispense_date')
      .resample('ME')['qty_dispensed']
      .sum()
      .sort_index()
)

rest_monthly_freq = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']
      .count()
      .rename('restock_frequency')
      .sort_index()
)

rest_monthly_cost = (
    df_restock
      .set_index('restock_date')
      .resample('ME')['total']
      .sum()
      .rename('restock_cost')
      .sort_index()
)

monthly = pd.concat(
    [inv_monthly_qty.rename('dispensed_qty'),
     rest_monthly_freq,
     rest_monthly_cost],
    axis=1
).fillna(0)

# 2) shift the restock series by 1 month so that “March’s dispensing”
#    lines up with “April’s restocking”
monthly['restock_frequency_lag1'] = monthly['restock_frequency'].shift(1)
monthly['restock_cost_lag1']      = monthly['restock_cost'].shift(1)

# 3) compute the new, “lead/lag” correlation matrix
corr_lagged = monthly[['dispensed_qty','restock_frequency_lag1','restock_cost_lag1']].corr()

print("=== Correlation (Dispense(t) vs Restock(t+1)) ===")
print(corr_lagged)
print()
print(f"Correlation(dispensed_qty, restock_frequency_lag1) = "
      f"{corr_lagged.loc['dispensed_qty','restock_frequency_lag1']:.3f}")
print(f"Correlation(dispensed_qty, restock_cost_lag1)      = "
      f"{corr_lagged.loc['dispensed_qty','restock_cost_lag1']:.3f}")

"""The magnitudes (|–0.67| and |–0.63|) tell us there is a very strong one‐month “lead/lag” relationship between dispensing and restocking—months with big dispense‐outs tend to be followed by big restock activity one month later.

The reason the coefficients show up as negative is simply because we aligned “dispense(t)” with “restock(t+1)” but then computed corr(dispense(t),restock_lag1). In other words, when dispense is high in March, restock_lag1 is actually capturing April’s refill, which in our DataFrame appears in an earlier row than March’s dispense.

If you flip the shift so that April’s restock sits on the same row as March’s dispense (e.g. use monthly['restock_cost_lead1'] = monthly['restock_cost'].shift(-1)), you would see a strong positive correlation (≈ +0.63) instead of –0.63. That positive value is the real “usage → next‐month refill” signal.
"""

# Seasonality and Patterns: Investigate any seasonal patterns or cyclic behaviour in dispensing and restocking activities.

import seaborn as sns

# 1) Compute “dispensed_qty” seasonality (Jan→Dec)
avg_by_month_inv = inv_monthly_qty.groupby(inv_monthly_qty.index.month).mean()
overall_mean_inv = inv_monthly_qty.mean()
seasonal_index_inv = (avg_by_month_inv / overall_mean_inv).rename('seasonal_index')

# 2) Compute “restocked_amount” seasonality (Jan→Dec)
avg_by_month_rest = rest_monthly_qty.groupby(rest_monthly_qty.index.month).mean()
overall_mean_rest = rest_monthly_qty.mean()
seasonal_index_rest = (avg_by_month_rest / overall_mean_rest).rename('seasonal_index')

# 3) Prepare DataFrames for boxplots
inv_monthly_df = inv_monthly_qty.reset_index().rename(columns={'dispense_date':'date', 'qty_dispensed':'dispensed_qty'})
inv_monthly_df['month'] = inv_monthly_df['date'].dt.month

rest_monthly_df = rest_monthly_qty.reset_index().rename(columns={'restock_date':'date', 'total':'restocked_amount'})
rest_monthly_df['month'] = rest_monthly_df['date'].dt.month

# 4) Boxplot: dispensed_qty by calendar month
sns.boxplot(data=inv_monthly_df, x='month', y='dispensed_qty', color='C0')
plt.title('Monthly Distribution of Qty Dispensed (All Years)')
plt.xlabel('Calendar Month (1=Jan … 12=Dec)')
plt.ylabel('Units Dispensed')
plt.tight_layout()
plt.show()

# 5) Line: inventory seasonal index
seasonal_index_inv.plot(marker='o', linewidth=2, color='C0')
plt.axhline(1.0, color='gray', linestyle='--', linewidth=1)
plt.title('Inventory Seasonal Index (All Years)')
plt.xlabel('Month of Year')
plt.xticks(range(1,13))
plt.ylabel('Index (month avg ÷ overall avg)')
plt.tight_layout()
plt.show()

# 6) Boxplot: restocked_amount by calendar month
df_restock['restock_date'] = pd.to_datetime(df_restock['restock_date'])
df_restock['month'] = df_restock['restock_date'].dt.month

plt.figure(figsize=(8,4))
sns.boxplot(
    data=df_restock,
    x='month',
    y='total',
    color='C1'
)
plt.title("Daily Distribution of 'total' Restocked by Month (All Years)")
plt.xlabel("Calendar Month (1=Jan … 12=Dec)")
plt.ylabel("Units Restocked (daily total)")
plt.tight_layout()
plt.show()

# 7) Line: restock seasonal index
seasonal_index_rest.plot(marker='o', linewidth=2, color='C1')
plt.axhline(1.0, color='gray', linestyle='--', linewidth=1)
plt.title('Restock Seasonal Index (All Years)')
plt.xlabel('Month of Year')
plt.xticks(range(1,13))
plt.ylabel('Index (month avg ÷ overall avg)')
plt.tight_layout()
plt.show()

"""Inventory Dispensed (monthly boxplots)
February has a noticeably lower volume than January and is the weakest month, indicating a post–holiday slowdown
Demand begins to pick up in March and continues rising through midsummer
From July through October, monthly medians stay close to or slightly above the yearly average, showing steady mid-year demand
November and December show the highest demand, with December being the strongest month overall

Inventory Seasonal Index
February’s index is about 0.52 times the annual average, confirming the deep February trough
March recovers to nearly the annual average
June through August rise above the annual average, with the index exceeding 1.10 by July
December peaks at approximately 1.26 times the annual average, marking the year-end high

Daily Restocked (daily boxplots by month)
March has very low daily restocks, often near zero, indicating minimal restocking activity
April and May rebound, with May’s daily restocks clustering around 300–350
June through September maintain a relatively stable daily restock level (around 300–350) with moderate variability
November and December show the highest daily restocks, with December having the widest. February is the weakest month and December is the strongest month

Restock Seasonal Index
March’s index is about 0.50 times the annual average, confirming the deep March trough
April rises to roughly 0.91 times the annual average
May through August hover between 1.06 and 1.14 times average, reflecting steady mid-year restocking
December peaks at approximately 1.23 times the annual average, indicating a strong year-end restock surge
"""

# Demand Variability by SKU: Investigate the variability in demand for each SKU over time to identify high-variance items that may require special attention in inventory planning.

# 1) Create “year_month” column (PeriodIndex) for df_inventory
df_inventory['year_month'] = df_inventory['dispense_date'].dt.to_period('M')

# 2) Build a “monthly_by_sku_all” DataFrame: index = year_month, columns = SKUs,
#    values = total qty_dispensed for that SKU in that month (fill missing with 0)
monthly_by_sku_all = (
    df_inventory
      .groupby(['year_month', 'sku'])['qty_dispensed']
      .sum()
      .unstack(fill_value=0)
)

# 3) Convert the index back to timestamps (month end) for convenience
monthly_by_sku_all.index = monthly_by_sku_all.index.to_timestamp()

# 4) Compute per‐SKU summary statistics over all months:
#    - mean month‐to‐month demand
#    - standard deviation of month‐to‐month demand
#    - coefficient of variation (std / mean)
sku_monthly_std  = monthly_by_sku_all.std()
sku_monthly_mean = monthly_by_sku_all.mean()
sku_monthly_cv   = sku_monthly_std / sku_monthly_mean

# 5) Combine into one DataFrame and sort descending by CV
sku_variability = pd.DataFrame({
    'std':  sku_monthly_std,
    'mean': sku_monthly_mean,
    'cv':   sku_monthly_cv
}).sort_values('cv', ascending=False)

# 6) Display the top 10 SKUs by coefficient of variation
top10_cv = sku_variability.head(10)
print("=== Top 10 SKUs by Coefficient of Variation (σ/μ) ===")
print(top10_cv)

# 7) (Optional) Plot the top 10 CV SKUs as a bar chart
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 4))
top10_cv['cv'].plot(
    kind='bar',
    color='C4',
    edgecolor='black'
)
plt.title("Top 10 SKUs by Demand Variability (Coeff of Variation)")
plt.ylabel("Coefficient of Variation (σ / μ)")
plt.xlabel("SKU")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

"""SKUs with tiny average monthly demand (mean ≈ 0.08) but nonzero std (≈ 0.40) yield a massive CV (≈ 5.0). These are essentially “one‐off” or ultra‐infrequent items—very unpredictable and likely low‐priority for tight forecasting.

The next SKU (48d1f362…) has mean ≈ 1.04 but std ≈ 2.88 (CV ≈ 2.77), indicating occasional small spikes—still quite sporadic demand. These may be niche items with irregular restocking.

Mid‐rank SKUs (e.g., 67e22bfb… and eaccfd10…) have mean demand in the 40–50 range but std ≈ 75–81 (CV ≈ 1.7–1.8). Although they move more units overall, they swing wildly month to month—these likely need more dynamic reorder rules.

Lower down, SKUs with mean ≈ 7–18 and std ≈ 8–20 (CV ≈ 1.1–1.3) still show above‐average variability, meaning that even moderate sellers are far from stable. They could be seasonal or tied to irregular usage.

In contrast, the remainder of SKUs outside this top‐CV list will have CV ≪ 1, implying steadier (“core”) demand suitable for standard reorder cadences.

Bottom line: The highest‐CV SKUs are either ultra‐low‐volume “one‐off” items or moderately popular SKUs with erratic spikes. They warrant special inventory rules (e.g., larger safety stock or conditional reorder thresholds), while the low‐CV SKUs can follow regular forecasting.
"""

# Seasonality in SKU Demand: Perform a seasonality analysis for individual SKUs to discover any cyclical demand patterns, which can inform restocking strategies.

# 1) (Re)build a monthly‐SKU pivot table if you don’t already have one.
#    We did this for the top‐10 SKUs earlier; here we’ll do it for all SKUs.

df_inventory['year_month'] = df_inventory['dispense_date'].dt.to_period('M')

monthly_all_skus = (
    df_inventory
      .groupby(['year_month', 'sku'])['qty_dispensed']
      .sum()
      .unstack(fill_value=0)
)

# Convert the index back to a Timestamp at month end for plotting convenience
monthly_all_skus.index = monthly_all_skus.index.to_timestamp()

# 2) Add a “month_of_year” column (1–12) based on that index
monthly_all_skus['month_of_year'] = monthly_all_skus.index.month

# 3) Compute each SKU’s 12‐entry “seasonal index” (mean by calendar month)
#    This gives a DataFrame whose index is 1–12 and columns = all SKUs.
seasonal_index_all = (
    monthly_all_skus
      .groupby('month_of_year')
      .mean()                # this averages across every year for each month_of_year
)

# 4) (Optional) If you only want to inspect the top‐N most important SKUs,
#    you can filter seasonal_index_all to only those columns. For example:
# top_n = 10
# top_cols = sku_totals.sort_values(ascending=False).index[:top_n]
# seasonal_index_top10 = seasonal_index_all[top_cols]

# 5) Now, plot each SKU’s index‐curve. For visual clarity you might want to
#    pick a subset at first (e.g. the top 5 or top 10 by overall volume).

import matplotlib.pyplot as plt

# Example: plot the top‐5 highest‐volume SKUs’ seasonal indices:
top_10 = sku_totals.sort_values(ascending=False).index[:10]

plt.figure(figsize=(8, 5))
for sku in top_10:
    plt.plot(
        seasonal_index_all.index,
        seasonal_index_all[sku],
        marker='o',
        label=sku
    )

plt.title("Seasonal Demand Profiles\n(Top 10 SKUs)")
plt.xlabel("Calendar Month (1=Jan ... 12=Dec)")
plt.xticks(range(1, 13))
plt.ylabel("Average Units Dispensed")
plt.legend(title="SKU", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()

# 6) If you’d like to see a “heatmap” of seasonality across *all* SKUs, you can do:

import seaborn as sns

plt.figure(figsize=(10, 12))
sns.heatmap(
    seasonal_index_all.T,      # SKUs as rows, months (1–12) as columns
    cmap="YlGnBu",
    cbar_kws={"label": "Avg Units Dispensed (Seasonal Index)"}
)
plt.title("Seasonality Heatmap: Average Monthly Demand for Every SKU")
plt.xlabel("Month of Year")
plt.ylabel("SKU")
plt.tight_layout()
plt.show()

"""For the Top 10 SKUs seasonal profiles:
• Almost every top SKU dips in February (calendar month 2), then steadily rises through mid-year.

• The strongest peak months are around July–August and again in November–December for most SKUs.

• SKU b1cfc8…deb shows a nearly monotonic climb from March through December, indicating end-of-year demand surge.

• SKU be61be5…8fa7 and 93d664d…e051e92 mirror that pattern but with slightly smaller peaks in late summer and late year.

• SKU 9a15481…4fb7e05 spikes in July and November, suggesting promotional or project-driven restocking.

• Mid-ranking SKUs (e.g. da3562c…fb66aa, ff9575e…2c2bff82) have modest seasonality: small trough in Feb and a broad plateau May–Sep.

• Lower-volume SKUs (05d98e5…4d1fc3, 78baaaf…1a7ef8d) show relatively flat demand with only a slight bump in November–December.

• Across all ten, winter months (Jan) tend to be below average, spring (Mar–May) gradually recovers, summer shows clear growth, and fall/winter finish strong.

From the full‐SKU heatmap:
• A handful of SKUs have very low year-round volume (bottom rows, light colors), meaning they never exceed ~50–100 units in any month.

• High-volume SKUs form distinct horizontal “bright bands,” with the brightest being b1cfc8…deb, 93d664d…e051e92, and bebd1078…3fcf9.

• Those bright lines confirm strong seasonality: they dip darkest (lowest) in February, then progressively lighten (higher) through mid-year, with the very brightest cells in November–December.

• Some mid-volume SKUs (e.g. 05d98e5…4d1fc3, 690b7d2f…456a943) show a smaller amplitude: lightish green May–Sep, moderate in winter.

• A few SKUs (e.g. 48d1f362…0eb40a) stay almost uniformly pale, indicating nearly constant low demand.

• Overall, most stocking activity is clustered June–December, with a clear trough in February–March across almost all SKUs.










"""

# Device Utilization Analysis
# ---------------------------
# Based on the existing “df_inventory” and “daily_inventory” from earlier steps,
# we want to compute for each device:
#   1) How many distinct days it was active (“active_days”)
#   2) The total quantity dispensed over the entire period (“total_dispensed”)
#   3) The average quantity dispensed per active day (“avg_dispensed_per_day”)
#
# Then we’ll assemble these into a DataFrame and plot three bar charts:
#   (i)   active_days per device
#   (ii)  total_dispensed per device
#   (iii) avg_dispensed_per_day per device
#
# This block assumes you have already run the code that created “daily_inventory” and “df_inventory”.
# If “daily_inventory” does not have a column named “date” (perhaps it still has “dispense_date”),
# we recreate/overwrite it here to guarantee the correct column exists.

import pandas as pd
import matplotlib.pyplot as plt

# 0) Ensure daily_inventory exists and has a “date” column
# If “daily_inventory” isn’t already defined or doesn’t have “date”, rebuild it now:
if 'daily_inventory' not in globals() or 'date' not in daily_inventory.columns:
    # Rebuild daily_inventory exactly as before:
    daily_inventory = (
        df_inventory
          .groupby(['device_id', df_inventory['dispense_date'].dt.date])
          .agg(qty_dispensed=('qty_dispensed', 'sum'))
          .reset_index()
          .rename(columns={'dispense_date':'date'})
    )
    # Convert that “date” column to datetime:
    daily_inventory['date'] = pd.to_datetime(daily_inventory['date'])

# 1) Count distinct active days per device
active_days_by_device = (
    daily_inventory
      .groupby('device_id')['date']
      .nunique()
)

# 2) Compute total quantity dispensed per device (from the raw df_inventory)
total_dispensed_by_device = (
    df_inventory
      .groupby('device_id')['qty_dispensed']
      .sum()
)

# 3) Compute average quantity dispensed per active day
#    We must align the two series by device_id index
total_dispensed_aligned = total_dispensed_by_device.reindex(active_days_by_device.index)
avg_dispensed_per_day = total_dispensed_aligned / active_days_by_device

# 4) Assemble into a single DataFrame
device_util = pd.DataFrame({
    'device_id':             active_days_by_device.index,
    'active_days':           active_days_by_device.values,
    'total_dispensed':       total_dispensed_aligned.values,
    'avg_dispensed_per_day': avg_dispensed_per_day.values
})
# Make sure the order is sorted by avg_dispensed_per_day descending
device_util = device_util.sort_values(by='avg_dispensed_per_day', ascending=False).reset_index(drop=True)

# Display the resulting DataFrame
print(device_util)


# 5) Plotting
# ------------

# (i) Active days per device
plt.figure(figsize=(8, 4))
plt.bar(device_util['device_id'], device_util['active_days'], color='C0')
plt.title('Active Days per Device')
plt.xlabel('Device ID')
plt.ylabel('Number of Active Days')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# (ii) Total quantity dispensed per device
plt.figure(figsize=(8, 4))
plt.bar(device_util['device_id'], device_util['total_dispensed'], color='C1')
plt.title('Total Quantity Dispensed per Device')
plt.xlabel('Device ID')
plt.ylabel('Total Units Dispensed')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# (iii) Average quantity dispensed per active day (per device)
plt.figure(figsize=(8, 4))
plt.bar(device_util['device_id'], device_util['avg_dispensed_per_day'], color='C2')
plt.title('Average Units Dispensed per Active Day (per Device)')
plt.xlabel('Device ID')
plt.ylabel('Avg Units / Day')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

"""All five devices have almost identical active-day counts (around 580 days each), so they’ve been online for roughly the same length of time.

Despite similar uptime, device_6726f2a054f54836aaabe8c7643286bc dispensed the most total units (70K+), while device_0749c361d8ac7047c2f98fbcb2eadd16 dispensed the least (55K).

In terms of average throughput (units per active day), device_6726f2a054f54836aaabe8c7643286bc leads at ~99 units/day, and device_0749c361d8ac7047c2f98fbcb2eadd16 is lowest at ~85 units/day.

The narrow range (≈85–99 units/day) indicates no severely underused machine—all machines are utilized at a fairly similar rate, though device_6726f2a054f54836aaabe8c7643286bc is marginally busier than the others.
"""
