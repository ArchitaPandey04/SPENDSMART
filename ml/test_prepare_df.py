import sqlite3
from ml.model_utils import prepare_df_for_user

# Path to main app database
DB_PATH = "database/spendsmart.db"

def test_prepare_df():
    conn =sqlite3.connect(DB_PATH)
    
    user_id = 1
    
    df = prepare_df_for_user(conn, user_id)
    
    print("\n=== DataFrame Preview ===")
    print(df.head())
    
    print("\n=== DataFrame Info ===")
    print(df.info())
    
    conn.close()
    
if __name__ == "__main__":
    test_prepare_df()