import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from imblearn.over_sampling import SMOTE
from sklearn.metrics import recall_score, f1_score, classification_report
import joblib
import os

def preprocess_and_train():
    # Load data
    data_path = 'e:/projects/AURA/data/PCOS_infertility.csv'
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return
    
    # Read the data
    df = pd.read_csv(data_path)
    
    # 1. Cleaning Column Names
    df.columns = [c.strip() for c in df.columns]
    
    # 2. Data Cleaning for 'AMH(ng/mL)'
    # Found that AMH contains 'a' as a value, which is likely a data entry error. 
    # Let's convert to numeric and handle errors as NaNs (to be imputed later).
    df['AMH(ng/mL)'] = pd.to_numeric(df['AMH(ng/mL)'], errors='coerce')
    
    # 3. Define Features and Target
    target_col = 'PCOS (Y/N)'
    drop_cols = ['Sl. No', 'Patient File No.', target_col]
    
    X = df.drop(drop_cols, axis=1)
    y = df[target_col]
    
    print(f"Features used: {X.columns.tolist()}")

    # 4. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 5. Imputation (using KNN since AMH now has NaNs)
    imputer = KNNImputer(n_neighbors=3, weights='distance')
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)
    
    # 6. Sampling Strategy (SMOTE) - Balancing the classes
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train_imputed, y_train)
    
    # 7. Model Training (XGBoost)
    params = {
        'n_estimators': 200,
        'max_depth': 4,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'random_state': 42
    }
    
    model = xgb.XGBClassifier(**params)
    model.fit(X_train_res, y_train_res)
    
    # 8. Evaluation
    y_pred = model.predict(X_test_imputed)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\nModel Evaluation Metrics:")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save artifacts
    os.makedirs('e:/projects/AURA/artifacts', exist_ok=True)
    joblib.dump(model, 'e:/projects/AURA/artifacts/model.pkl')
    joblib.dump(imputer, 'e:/projects/AURA/artifacts/imputer.pkl')
    joblib.dump(X.columns.tolist(), 'e:/projects/AURA/artifacts/features.pkl')
    
    return model, imputer

if __name__ == "__main__":
    preprocess_and_train()
