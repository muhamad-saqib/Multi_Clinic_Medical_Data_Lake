import hashlib
import pandas as pd

def hash_id(raw_id: str) -> str:
    """Patient ID ko secure hash mein convert karein"""
    return hashlib.sha256(raw_id.encode()).hexdigest()[:16]

def remove_pii(df):
    """Personal Information hataein aur patient hash banayein"""
    df = df.copy()
    
    # Personal information ke columns hataein
    pii_columns = ['name', 'address', 'phone', 'email']
    for col in pii_columns:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    
    # Patient ID ko hash mein convert karein
    if 'patient_id' in df.columns:
        df['patient_hash'] = df['patient_id'].astype(str).apply(hash_id)
        df.drop(columns=['patient_id'], inplace=True)
    
    return df

# Test function
if __name__ == "__main__":
    # Test data
    test_data = {
        'patient_id': ['P001', 'P002'],
        'name': ['Ali Khan', 'Sara Ahmed'],
        'age': [25, 30],
        'diagnosis': ['FLU', 'COLD']
    }
    
    df = pd.DataFrame(test_data)
    print("Original Data:")
    print(df)
    
    cleaned_df = remove_pii(df)
    print("\nAfter Anonymization:")
    print(cleaned_df)