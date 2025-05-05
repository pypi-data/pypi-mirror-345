print("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
data=pd.read_excel('Ecommerce+Sales+Data.xlsx')
data.head()
def extracting(file_path):
    df=pd.read_excel(file_path)
    return df

def transform(df):
    print("Transforming Data")

    df['OrderDate']=pd.to_datetime(df['OrderDate'],errors='coerce')

    if 'Quantity' in df.columns and 'UnitPrice' in df.columns:
        df['Revenue']=df['Quantity']*df['UnitPrice']
        print("Revenue Column Added")
    else:
        print("Quantity or UnitPrice column not found")

    numeric_column=df.select_dtypes(include=['float64','int64']).columns
    df[numeric_column]=df[numeric_column].fillna(df[numeric_column].mean())

    text_cols=df.select_dtypes(include=['object']).columns
    df[text_cols]=df[text_cols].fillna('Unknown')

    df['OrderMonth'] = df['OrderDate'].dt.month
    df['OrderYear'] = df['OrderDate'].dt.year

    return df

def load(df, output_file):
    print("Loading Data")
    df.to_csv(output_file,index=False)
    print(f"Data Saved to {output_file}")

def etl_process(file_path, output_file):
    df=extracting(file_path)
    df=transform(df)
    load(df, output_file)
    return output_file

transformed_data=etl_process('Ecommerce+Sales+Data.xlsx','transformed_data.csv')

def visualise(transformed_data):
    df=pd.read_csv(transformed_data)
    df.head()
    print("Visualizing data...")
    plt.figure(figsize=(10,6))
    sns.lineplot(x='OrderDate',y='Revenue',data=df)
    if 'Revenue' in df.columns:
        sales_by_month = df.groupby(['OrderYear', 'OrderMonth'])['Revenue'].sum().reset_index()

        plt.figure(figsize=(12,6))
        sns.lineplot(data=sales_by_month, x='OrderMonth', y='Revenue', hue='OrderYear', marker="o")
        plt.title('Monthly Sales Trend by Year')
        plt.xlabel('Month')
        plt.ylabel('Revenue ($)')
        plt.grid(True)
        plt.show()
visualise(transformed_data)""")

