import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def generate_synthetic_data(n_samples=1000, random_seed=42):
    np.random.seed(random_seed)
    
    # Biometric
    bmi = np.random.normal(24, 6, n_samples).clip(15, 45)
    whr = np.random.normal(0.8, 0.1, n_samples).clip(0.6, 1.2)
    
    # Menstrual
    cycle_regularity = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    cycle_length = np.random.normal(28, 5, n_samples).astype(int).clip(21, 90)
    
    # Biochemical
    fsh = np.random.normal(5, 2, n_samples).clip(1, 20)
    # LH is often higher in PCOS
    lh = np.random.normal(5, 3, n_samples).clip(1, 30)
    amh = np.random.normal(3, 2, n_samples).clip(0.1, 15)
    testosterone = np.random.normal(30, 15, n_samples).clip(5, 120)
    
    # Clinical signs
    hirsutism_score = np.random.poisson(4, n_samples).clip(0, 36)
    acne_severity = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.5, 0.3, 0.15, 0.05])
    acanthosis = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    
    df = pd.DataFrame({
        'BMI': bmi,
        'Waist_Hip_Ratio': whr,
        'Cycle_Regularity': cycle_regularity,
        'Cycle_Length_Days': cycle_length,
        'LH_mIUmL': lh,
        'FSH_mIUmL': fsh,
        'AMH_ngmL': amh,
        'Testosterone_ngdL': testosterone,
        'Hirsutism_Score': hirsutism_score,
        'Acne_Severity': acne_severity,
        'Acanthosis_Nigricans': acanthosis
    })
    
    # Logic for target variable (PCOS_Status)
    # Rotterdam Criteria roughly: 
    # 1. Oligo/Anovulation (Cycle Irregularity)
    # 2. Hyperandrogenism (Testosterone or Hirsutism or Acne)
    # 3. Polycystic Ovaries (often correlated with AMH > 3.5-4.0)
    
    score = (
        (df['Cycle_Regularity'] * 2.0) +
        (df['AMH_ngmL'] > 3.8).astype(int) * 1.5 +
        (df['LH_mIUmL'] / df['FSH_mIUmL'] > 2.0).astype(int) * 1.2 +
        (df['Testosterone_ngdL'] > 50).astype(int) * 1.0 +
        (df['Hirsutism_Score'] > 8).astype(int) * 0.8 +
        (df['BMI'] > 28).astype(int) * 0.5
    )
    
    # Add some noise
    score += np.random.normal(0, 0.5, n_samples)
    
    # Probability conversion
    prob = 1 / (1 + np.exp(-(score - 3)))
    df['PCOS_Status'] = (prob > 0.5).astype(int)
    
    return df

if __name__ == "__main__":
    data = generate_synthetic_data()
    data.to_csv('e:/projects/AURA/pcos_data.csv', index=False)
    print(f"Generated data with {data['PCOS_Status'].sum()} positive cases out of {len(data)}.")
