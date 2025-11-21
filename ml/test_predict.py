from ml.fake_data import generate_fake_expenses
from ml.model_utils import aggregate_monthly_expenses
from ml.predictor import predict_next_month

def test_prediction():
    df = generate_fake_expenses(80)
    monthly = aggregate_monthly_expenses(df)
    
    print("=== Monthly Data ===")
    print(monthly)
    
    pred = predict_next_month(monthly)
    print("\nPredicted next month's speding:", pred)
    
if __name__ == "__main__":
    test_prediction()
