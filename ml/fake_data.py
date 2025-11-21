import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_fake_expenses(num_records=100):
    np.random.seed(42)

    # Define sample categories
    categories = ["Food", "Shopping", "Transport", "Bills", "Entertainment"]

    # Generate random dates within the last 6 months
    start_date = datetime.now() - timedelta(days=180)
    dates = [start_date + timedelta(days=int(np.random.randint(0, 180))) for _ in range(num_records)]

    # Generate random amounts (₹50–₹2000)
    amounts = np.random.randint(50, 2000, num_records)

    # Random categories
    cat_choices = np.random.choice(categories, num_records)

    # Create DataFrame
    df = pd.DataFrame({
        "date": dates,
        "amount": amounts,
        "category": cat_choices
    })

    # Add extra columns
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_year"] = df["date"].dt.to_period("M").astype(str)

    return df

def aggregate_monthly_expenses(df):
    if df.empty:
        return pd.DataFrame(columns=['month_year', 'amount'])
    
    monthly_df = (
        df.groupby('month_year')['amount']
        .sum()
        .reset_index()
        .sort_values('month_year')
    )
    return monthly_df



if __name__ == "__main__":
    df = generate_fake_expenses(10)
    print(df.head())
