import numpy as np
from sklearn.linear_model import LinearRegression

def predict_next_month(monthly_df):
    """
    Predict the next month's total spending.
    monthly_df must contain columns: month_index, amount
    """

    if monthly_df.empty or len(monthly_df) < 2:
        print("Not enough data to predict.")
        return None

    # Prepare the training data
    X = monthly_df["month_index"].values.reshape(-1, 1)
    y = monthly_df["amount"].values

    model = LinearRegression()
    model.fit(X, y)

    next_month_index = monthly_df["month_index"].max() + 1
    prediction = model.predict([[next_month_index]])[0]

    return round(float(prediction), 2)
