from ml.fake_data import generate_fake_expenses
from ml.model_utils import aggregate_monthly_expenses

df = generate_fake_expenses(50)
print("=== Raw Data ===")
print(df.head())

print("\n=== Monthly Aggregation ===")
print(aggregate_monthly_expenses(df))
