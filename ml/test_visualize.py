from ml.fake_data import generate_fake_expenses
from ml.model_utils import aggregate_monthly_expenses
from ml.visualizer import plot_monthly_expenses

def test_visualize():
    df = generate_fake_expenses(50)
    monthly = aggregate_monthly_expenses(df)
    plot_monthly_expenses(monthly)

if __name__ == "__main__":
    test_visualize()

