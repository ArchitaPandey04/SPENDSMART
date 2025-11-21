import matplotlib.pyplot as plt

def plot_monthly_expenses(monthly_df):
    """
    Plot a simple monthly expenses line chart.
    """
    
    if monthly_df.empty:
        print("No data to plot.")
        return
    
    plt.figure(figsize=(8,4))
    plt.plot(monthly_df["month_year"], monthly_df["amount"])
    plt.xticks(rotation=45)
    plt.title("Monthly Spending Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Amount")
    plt.tight_layout()
    plt.show()
