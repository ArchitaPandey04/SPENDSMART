import pandas as pd
import matplotlib.pyplot as plt


def prepare_df_for_user(conn, user_id):
    """
    Fetch expenses for a specific user from the database and return a cleaned DataFrame.
    
    Parameters:
    - conn: sqlite3 connection object 
    - user_id: integer, the ID of the user
    
    Returns:
    -df: pandas DataFrame with columns:
     'date', 'amount', 'category', 'year', 'month', 'month_year'   
    """
    
    # Fetch relevant columns from teh expense table
    df = pd.read_sql_query(
    "SELECT date, amount, category FROM expenses WHERE user_id = ?",
    conn,
    params=(user_id,)
)
    
    # If user has no expenses, return empty DataFrame
    if df.empty:
        return df
    
    # Converting 'date' column to adtetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract year,month, and combined month-year for analysis
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    
    # Ensure 'amount' column is numeric and fill any missing values with 0
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    
    return df

def aggregate_monthly_expenses(df):
    """
    Aggregate total expenses per month.
    """
    if df.empty:
        return pd.DataFrame(columns=['month_year', 'amount'])
    
    monthly_df = (
        df.groupby('month_year')['amount']
        .sum()
        .reset_index()
        .sort_values('month_year')
    )
    
    monthly_df["month_index"] = range(len(monthly_df))

    return monthly_df

def plot_monthly_exepnses(monthly_df):
    """
    Display a bar chart showing total expenses per month.
    """
    
    if monthly_df.empty:
        print("No data available to plot.")
        return
    
    plt.figure(figsize=(8, 5))
    plt.bar(monthly_df["month_year"], monthly_df["amount"])
    plt.xlabel("Month")
    plt.ylabel("Total Expenses (₹)")
    plt.title("Monthly Expenses Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()