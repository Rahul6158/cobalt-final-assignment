import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# File paths
app_data_path = r"D:\cobalt\application_data.csv"
prev_app_path = r"D:\cobalt\previous_application.csv"
desc_path = r"D:\cobalt\columns_description.csv"

# ------------------------
# LOAD DATA
# ------------------------

print("🔄 Loading datasets...")
app_df = pd.read_csv(app_data_path)
prev_df = pd.read_csv(prev_app_path)
desc_df = pd.read_csv(desc_path, encoding='latin1')  # fix for encoding error
print("✅ Datasets loaded.\n")

# ------------------------
# HANDLE MISSING VALUES
# ------------------------

print("🔍 Handling missing values...")

# Drop columns with > 40% missing values
missing_percent = app_df.isnull().mean().sort_values(ascending=False)
to_drop = missing_percent[missing_percent > 0.4].index.tolist()
app_df.drop(columns=to_drop, inplace=True)
print(f"Dropped columns with >40% missing values: {to_drop}\n")

# Fill EXT_SOURCE columns with median
for col in ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']:
    if col in app_df.columns:
        app_df[col].fillna(app_df[col].median(), inplace=True)

# Fill OCCUPATION_TYPE based on NAME_INCOME_TYPE
if 'OCCUPATION_TYPE' in app_df.columns and 'NAME_INCOME_TYPE' in app_df.columns:
    app_df['OCCUPATION_TYPE'] = app_df.groupby('NAME_INCOME_TYPE')['OCCUPATION_TYPE']\
        .transform(lambda x: x.fillna(x.mode().iloc[0]) if not x.mode().empty else x)

# Fill NAME_EDUCATION_TYPE based on NAME_FAMILY_STATUS
if 'NAME_EDUCATION_TYPE' in app_df.columns and 'NAME_FAMILY_STATUS' in app_df.columns:
    app_df['NAME_EDUCATION_TYPE'] = app_df.groupby('NAME_FAMILY_STATUS')['NAME_EDUCATION_TYPE']\
        .transform(lambda x: x.fillna(x.mode().iloc[0]) if not x.mode().empty else x)

print("✅ Missing values handled.\n")

# ------------------------
# REMOVE OUTLIERS USING IQR
# ------------------------

print("📊 Removing outliers from numeric columns...")

def remove_outliers(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[col] >= lower) & (df[col] <= upper)]

numeric_cols = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'CNT_CHILDREN']
for col in numeric_cols:
    if col in app_df.columns:
        before = len(app_df)
        app_df = remove_outliers(app_df, col)
        after = len(app_df)
        print(f"{col}: removed {before - after} outliers")

print("✅ Outliers removed.\n")

# ------------------------
# CONVERT DATE COLUMNS
# ------------------------

print("📆 Converting date columns...")

reference_date = pd.to_datetime("2025-08-03")

# DAYS_BIRTH conversion
app_df['BIRTH_DATE'] = reference_date + pd.to_timedelta(app_df['DAYS_BIRTH'], unit='D')

# DAYS_EMPLOYED with filtering
app_df['EMPLOYMENT_START_DATE'] = pd.NaT
valid_emp = app_df['DAYS_EMPLOYED'].between(-30000, 30000)
app_df.loc[valid_emp, 'EMPLOYMENT_START_DATE'] = reference_date + pd.to_timedelta(app_df.loc[valid_emp, 'DAYS_EMPLOYED'], unit='D')

print("✅ Date fields converted.\n")

# ------------------------
# SAVE CLEANED application_data.csv
# ------------------------

output_app_path = r"D:\cobalt\cleaned_application_data.csv"
app_df.to_csv(output_app_path, index=False)
print(f"💾 Cleaned application data saved to: {output_app_path}\n")

# ------------------------
# CLEAN previous_application.csv
# ------------------------

print("🧼 Cleaning previous_application.csv...")

# Fill numerical missing values with median
prev_df.fillna(prev_df.median(numeric_only=True), inplace=True)

# Fill categorical missing values with mode
for col in prev_df.select_dtypes(include='object'):
    prev_df[col].fillna(prev_df[col].mode()[0], inplace=True)

# Convert DAYS_* columns with overflow safety
date_cols = ['DAYS_FIRST_DRAWING', 'DAYS_FIRST_DUE', 'DAYS_LAST_DUE_1ST_VERSION',
             'DAYS_LAST_DUE', 'DAYS_TERMINATION', 'DAYS_DECISION']

for col in date_cols:
    if col in prev_df.columns:
        new_col = col + '_ACTUAL'
        prev_df[new_col] = pd.NaT
        valid_mask = prev_df[col].between(-30000, 30000)
        prev_df.loc[valid_mask, new_col] = reference_date + pd.to_timedelta(prev_df.loc[valid_mask, col], unit='D')

print("✅ previous_application.csv cleaned.\n")

# ------------------------
# SAVE CLEANED previous_application.csv
# ------------------------

output_prev_path = r"D:\cobalt\cleaned_previous_application.csv"
prev_df.to_csv(output_prev_path, index=False)
print(f"💾 Cleaned previous application data saved to: {output_prev_path}\n")

# ------------------------
# OPTIONAL: Summary Report
# ------------------------

print("📋 Final Summary:")
print(f"Cleaned application_data shape: {app_df.shape}")
print(f"Cleaned previous_application shape: {prev_df.shape}")
print("🟢 Step 1 (Data Cleaning & Preparation) complete.")


#output::::
# PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50591' '--' 'D:\Projects\qp_app\loan_data_cleaning.py' 
# 🔴 Columns removed due to >40% missing values:
# COMMONAREA_AVG                  0.699214
# COMMONAREA_MODE                 0.699214
# COMMONAREA_MEDI                 0.699214
# NONLIVINGAPARTMENTS_MEDI        0.694294
# NONLIVINGAPARTMENTS_MODE        0.694294
# NONLIVINGAPARTMENTS_AVG         0.694294
# LIVINGAPARTMENTS_AVG            0.684534
# LIVINGAPARTMENTS_MODE           0.684534
# LIVINGAPARTMENTS_MEDI           0.684534
# FONDKAPREMONT_MODE              0.683834
# FLOORSMIN_MODE                  0.677894
# FLOORSMIN_AVG                   0.677894
# FLOORSMIN_MEDI                  0.677894
# YEARS_BUILD_AVG                 0.664793
# YEARS_BUILD_MODE                0.664793
# YEARS_BUILD_MEDI                0.664793
# OWN_CAR_AGE                     0.659013
# LANDAREA_MEDI                   0.594432
# LANDAREA_AVG                    0.594432
# LANDAREA_MODE                   0.594432
# BASEMENTAREA_MODE               0.583992
# BASEMENTAREA_MEDI               0.583992
# BASEMENTAREA_AVG                0.583992
# EXT_SOURCE_1                    0.563451
# NONLIVINGAREA_MODE              0.551451
# NONLIVINGAREA_AVG               0.551451
# NONLIVINGAREA_MEDI              0.551451
# ELEVATORS_AVG                   0.533031
# ELEVATORS_MEDI                  0.533031
# ELEVATORS_MODE                  0.533031
# WALLSMATERIAL_MODE              0.509190
# APARTMENTS_AVG                  0.507710
# APARTMENTS_MEDI                 0.507710
# APARTMENTS_MODE                 0.507710
# ENTRANCES_MODE                  0.503910
# ENTRANCES_MEDI                  0.503910
# ENTRANCES_AVG                   0.503910
# LIVINGAREA_AVG                  0.502750
# LIVINGAREA_MEDI                 0.502750
# LIVINGAREA_MODE                 0.502750
# HOUSETYPE_MODE                  0.501510
# FLOORSMAX_MODE                  0.497510
# FLOORSMAX_AVG                   0.497510
# FLOORSMAX_MEDI                  0.497510
# YEARS_BEGINEXPLUATATION_MODE    0.487890
# YEARS_BEGINEXPLUATATION_MEDI    0.487890
# YEARS_BEGINEXPLUATATION_AVG     0.487890
# TOTALAREA_MODE                  0.482970
# EMERGENCYSTATE_MODE             0.473969
# dtype: float64
# D:\Projects\qp_app\loan_data_cleaning.py:34: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.

# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.


#   app_df[col].fillna(app_df[col].median(), inplace=True)
# D:\Projects\qp_app\loan_data_cleaning.py:34: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.

# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.


#   app_df[col].fillna(app_df[col].median(), inplace=True)
# ✅ Removed outliers from AMT_INCOME_TOTAL: 2295 rows dropped
# ✅ Removed outliers from AMT_CREDIT: 806 rows dropped
# ✅ Removed outliers from AMT_ANNUITY: 770 rows dropped
# ✅ Removed outliers from CNT_CHILDREN: 660 rows dropped
# Backend tkagg is interactive backend. Turning interactive mode on.
# PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50665' '--' 'D:\Projects\qp_app\loan_data_cleaning.py' 
# 🔄 Loading datasets...
# ✅ Datasets loaded.

# 🔍 Handling missing values...
# Dropped columns with >40% missing values: ['COMMONAREA_AVG', 'COMMONAREA_MODE', 'COMMONAREA_MEDI', 'NONLIVINGAPARTMENTS_MEDI', 'NONLIVINGAPARTMENTS_MODE', 'NONLIVINGAPARTMENTS_AVG', 'LIVINGAPARTMENTS_AVG', 'LIVINGAPARTMENTS_MODE', 'LIVINGAPARTMENTS_MEDI', 'FONDKAPREMONT_MODE', 'FLOORSMIN_MODE', 'FLOORSMIN_AVG', 'FLOORSMIN_MEDI', 'YEARS_BUILD_AVG', 'YEARS_BUILD_MODE', 'YEARS_BUILD_MEDI', 'OWN_CAR_AGE', 'LANDAREA_MEDI', 'LANDAREA_AVG', 'LANDAREA_MODE', 'BASEMENTAREA_MODE', 'BASEMENTAREA_MEDI', 'BASEMENTAREA_AVG', 'EXT_SOURCE_1', 'NONLIVINGAREA_MODE', 'NONLIVINGAREA_AVG', 'NONLIVINGAREA_MEDI', 'ELEVATORS_AVG', 'ELEVATORS_MEDI', 'ELEVATORS_MODE', 'WALLSMATERIAL_MODE', 'APARTMENTS_AVG', 'APARTMENTS_MEDI', 'APARTMENTS_MODE', 'ENTRANCES_MODE', 'ENTRANCES_MEDI', 'ENTRANCES_AVG', 'LIVINGAREA_AVG', 'LIVINGAREA_MEDI', 'LIVINGAREA_MODE', 'HOUSETYPE_MODE', 'FLOORSMAX_MODE', 'FLOORSMAX_AVG', 'FLOORSMAX_MEDI', 'YEARS_BEGINEXPLUATATION_MODE', 'YEARS_BEGINEXPLUATATION_MEDI', 'YEARS_BEGINEXPLUATATION_AVG', 'TOTALAREA_MODE', 'EMERGENCYSTATE_MODE']

# D:\Projects\qp_app\loan_data_cleaning.py:37: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.

# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.


#   app_df[col].fillna(app_df[col].median(), inplace=True)
# D:\Projects\qp_app\loan_data_cleaning.py:37: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.

# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.


#   app_df[col].fillna(app_df[col].median(), inplace=True)
# ✅ Missing values handled.

# 📊 Removing outliers from numeric columns...
# AMT_INCOME_TOTAL: removed 2295 outliers
# AMT_CREDIT: removed 806 outliers
# AMT_ANNUITY: removed 770 outliers
# CNT_CHILDREN: removed 660 outliers
# ✅ Outliers removed.

# 📆 Converting date columns...
# ✅ Date fields converted.

# 💾 Cleaned application data saved to: D:\cobalt\cleaned_application_data.csv

# 🧼 Cleaning previous_application.csv...
# D:\Projects\qp_app\loan_data_cleaning.py:112: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.

# For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.


#   prev_df[col].fillna(prev_df[col].mode()[0], inplace=True)
# ✅ previous_application.csv cleaned.

# 💾 Cleaned previous application data saved to: D:\cobalt\cleaned_previous_application.csv

# 📋 Final Summary:
# Cleaned application_data shape: (45468, 75)
# Cleaned previous_application shape: (49999, 43)
# 🟢 Step 1 (Data Cleaning & Preparation) complete.
# PS D:\Projects\qp_app> PS D:\Projects\qp_app>  & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50014' '--' 'D:\Projects\qp_app\loan_data_cleaning.py'
# >> 🚀 Starting loan data cleaning process...
# >>
# >> 📂 Loading datasets...
# >> Loaded 49,999 current applications
# >> Loaded 49,999 previous applications
# >>
# >> 🧹 Cleaning application data...
# >> 🧹 Cleaning previous applications...
# >> PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50451' '--' 'D:\Projects\qp_app\loan_data_cleaning.py'
# >> 🚀 Starting loan data cleaning process...
# >>
# >> 📂 Loading datasets...
# >> Loaded 49,999 current applications
# >> Loaded 49,999 previous applications
# >>
# >> 🧹 Cleaning application data...
# >> 🧹 Cleaning previous applications...
# >> PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50531' '--' 'D:\Projects\qp_app\loan_data_cleaning.py'
# >> Backend tkagg is interactive backend. Turning interactive mode on.
# >> PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50591' '--' 'D:\Projects\qp_app\loan_data_cleaning.py'
# >> 🔴 Columns removed due to >40% missing values:
# >> COMMONAREA_AVG                  0.699214
# >> COMMONAREA_MODE                 0.699214
# >> COMMONAREA_MEDI                 0.699214
# >> NONLIVINGAPARTMENTS_MEDI        0.694294
# >> NONLIVINGAPARTMENTS_MODE        0.694294
# >> NONLIVINGAPARTMENTS_AVG         0.694294
# >> LIVINGAPARTMENTS_AVG            0.684534
# >> LIVINGAPARTMENTS_MODE           0.684534
# >> LIVINGAPARTMENTS_MEDI           0.684534
# >> FONDKAPREMONT_MODE              0.683834
# >> FLOORSMIN_MODE                  0.677894
# >> FLOORSMIN_AVG                   0.677894
# >> FLOORSMIN_MEDI                  0.677894
# >> YEARS_BUILD_AVG                 0.664793
# >> YEARS_BUILD_MODE                0.664793
# >> YEARS_BUILD_MEDI                0.664793
# >> OWN_CAR_AGE                     0.659013
# >> LANDAREA_MEDI                   0.594432
# >> LANDAREA_AVG                    0.594432
# >> LANDAREA_MODE                   0.594432
# >> BASEMENTAREA_MODE               0.583992
# >> BASEMENTAREA_MEDI               0.583992
# >> BASEMENTAREA_AVG                0.583992
# >> EXT_SOURCE_1                    0.563451
# >> NONLIVINGAREA_MODE              0.551451
# >> NONLIVINGAREA_AVG               0.551451
# >> NONLIVINGAREA_MEDI              0.551451
# >> ELEVATORS_AVG                   0.533031
# >> ELEVATORS_MEDI                  0.533031
# >> ELEVATORS_MODE                  0.533031
# >> WALLSMATERIAL_MODE              0.509190
# >> APARTMENTS_AVG                  0.507710
# >> APARTMENTS_MEDI                 0.507710
# >> APARTMENTS_MODE                 0.507710
# >> ENTRANCES_MODE                  0.503910
# >> ENTRANCES_MEDI                  0.503910
# >> ENTRANCES_AVG                   0.503910
# >> LIVINGAREA_AVG                  0.502750
# >> LIVINGAREA_MEDI                 0.502750
# >> LIVINGAREA_MODE                 0.502750
# >> HOUSETYPE_MODE                  0.501510
# >> FLOORSMAX_MODE                  0.497510
# >> FLOORSMAX_AVG                   0.497510
# >> FLOORSMAX_MEDI                  0.497510
# >> YEARS_BEGINEXPLUATATION_MODE    0.487890
# >> YEARS_BEGINEXPLUATATION_MEDI    0.487890
# >> YEARS_BEGINEXPLUATATION_AVG     0.487890
# >> TOTALAREA_MODE                  0.482970
# >> EMERGENCYSTATE_MODE             0.473969
# >> dtype: float64
# >> D:\Projects\qp_app\loan_data_cleaning.py:34: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# >> The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
# >>
# >> For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
# >>
# >>
# >>   app_df[col].fillna(app_df[col].median(), inplace=True)
# >> D:\Projects\qp_app\loan_data_cleaning.py:34: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# >> The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
# >>
# >> For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
# >>
# >>
# >>   app_df[col].fillna(app_df[col].median(), inplace=True)
# >> ✅ Removed outliers from AMT_INCOME_TOTAL: 2295 rows dropped
# >> ✅ Removed outliers from AMT_CREDIT: 806 rows dropped
# >> ✅ Removed outliers from AMT_ANNUITY: 770 rows dropped
# >> ✅ Removed outliers from CNT_CHILDREN: 660 rows dropped
# >> Backend tkagg is interactive backend. Turning interactive mode on.
# >> PS D:\Projects\qp_app>  d:; cd 'd:\Projects\qp_app'; & 'c:\Users\tusha\AppData\Local\Programs\Python\Python310\python.exe' 'c:\Users\tusha\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' '50665' '--' 'D:\Projects\qp_app\loan_data_cleaning.py'
# >> 🔄 Loading datasets...
# >> ✅ Datasets loaded.
# >>
# >> 🔍 Handling missing values...
# >> Dropped columns with >40% missing values: ['COMMONAREA_AVG', 'COMMONAREA_MODE', 'COMMONAREA_MEDI', 'NONLIVINGAPARTMENTS_MEDI', 'NONLIVINGAPARTMENTS_MODE', 'NONLIVINGAPARTMENTS_AVG', 'LIVINGAPARTMENTS_AVG', 'LIVINGAPARTMENTS_MODE', 'LIVINGAPARTMENTS_MEDI', 'FONDKAPREMONT_MODE', 'FLOORSMIN_MODE', 'FLOORSMIN_AVG', 'FLOORSMIN_MEDI', 'YEARS_BUILD_AVG', 'YEARS_BUILD_MODE', 'YEARS_BUILD_MEDI', 'OWN_CAR_AGE', 'LANDAREA_MEDI', 'LANDAREA_AVG', 'LANDAREA_MODE', 'BASEMENTAREA_MODE', 'BASEMENTAREA_MEDI', 'BASEMENTAREA_AVG', 'EXT_SOURCE_1', 'NONLIVINGAREA_MODE', 'NONLIVINGAREA_AVG', 'NONLIVINGAREA_MEDI', 'ELEVATORS_AVG', 'ELEVATORS_MEDI', 'ELEVATORS_MODE', 'WALLSMATERIAL_MODE', 'APARTMENTS_AVG', 'APARTMENTS_MEDI', 'APARTMENTS_MODE', 'ENTRANCES_MODE', 'ENTRANCES_MEDI', 'ENTRANCES_AVG', 'LIVINGAREA_AVG', 'LIVINGAREA_MEDI', 'LIVINGAREA_MODE', 'HOUSETYPE_MODE', 'FLOORSMAX_MODE', 'FLOORSMAX_AVG', 'FLOORSMAX_MEDI', 'YEARS_BEGINEXPLUATATION_MODE', 'YEARS_BEGINEXPLUATATION_MEDI', 'YEARS_BEGINEXPLUATATION_AVG', 'TOTALAREA_MODE', 'EMERGENCYSTATE_MODE']
# >>
# >> D:\Projects\qp_app\loan_data_cleaning.py:37: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# >> The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
# >>
# >> For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
# >>
# >>
# >>   app_df[col].fillna(app_df[col].median(), inplace=True)
# >> D:\Projects\qp_app\loan_data_cleaning.py:37: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# >> The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
# >>
# >> For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
# >>
# >>
# >>   app_df[col].fillna(app_df[col].median(), inplace=True)
# >> ✅ Missing values handled.
# >>
# >> 📊 Removing outliers from numeric columns...
# >> AMT_INCOME_TOTAL: removed 2295 outliers
# >> AMT_CREDIT: removed 806 outliers
# >> AMT_ANNUITY: removed 770 outliers
# >> CNT_CHILDREN: removed 660 outliers
# >> ✅ Outliers removed.
# >>
# >> 📆 Converting date columns...
# >> ✅ Date fields converted.
# >>
# >> 💾 Cleaned application data saved to: D:\cobalt\cleaned_application_data.csv
# >>
# >> 🧼 Cleaning previous_application.csv...
# >> D:\Projects\qp_app\loan_data_cleaning.py:112: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
# >> The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
# >>
# >> For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
# >>
# >>
# >>   prev_df[col].fillna(prev_df[col].mode()[0], inplace=True)
# >> ✅ previous_application.csv cleaned.
# >>
# >> 💾 Cleaned previous application data saved to: D:\cobalt\cleaned_previous_application.csv
# >>
# >> 📋 Final Summary:
# >> Cleaned application_data shape: (45468, 75)
# >> Cleaned previous_application shape: (49999, 43)
# >> 🟢 Step 1 (Data Cleaning & Preparation) complete.
