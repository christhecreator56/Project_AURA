from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import shap
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AURA API (PCOS Infertility)", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTIFACTS_DIR = 'e:/projects/AURA/artifacts'
model = None
imputer = None
feature_names = None
explainer = None

class PatientInfertilityData(BaseModel):
    beta_HCG_I: float = Field(..., alias="I   beta-HCG(mIU/mL)")
    beta_HCG_II: float = Field(..., alias="II    beta-HCG(mIU/mL)")
    AMH: float = Field(..., alias="AMH(ng/mL)")
    
    class Config:
        allow_population_by_field_name = True

@app.on_event("startup")
async def startup_event():
    global model, imputer, feature_names, explainer
    try:
        model = joblib.load(os.path.join(ARTIFACTS_DIR, 'model.pkl'))
        imputer = joblib.load(os.path.join(ARTIFACTS_DIR, 'imputer.pkl'))
        feature_names = joblib.load(os.path.join(ARTIFACTS_DIR, 'features.pkl'))
        explainer = shap.TreeExplainer(model)
        print("Model and artifacts loaded successfully.")
    except Exception as e:
        print(f"Error loading artifacts: {e}")

@app.get("/")
def read_root():
    return {"message": "AURA Infertility API is running", "status": "Ready" if model else "Loading"}

@app.post("/predict")
async def predict(data: PatientInfertilityData):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # 1. Convert to DataFrame
    # Note: We use the aliases to match the training feature names
    input_dict = {
        "I   beta-HCG(mIU/mL)": data.beta_HCG_I,
        "II    beta-HCG(mIU/mL)": data.beta_HCG_II,
        "AMH(ng/mL)": data.AMH
    }
    input_df = pd.DataFrame([input_dict])
    
    # 2. Match training columns order
    input_df = input_df[feature_names]
    
    # 3. Impute
    input_array = imputer.transform(input_df)
    
    # 4. Predict
    prob = float(model.predict_proba(input_array)[0][1])
    
    # 5. Risk Tier
    risk_tier = "low"
    if prob > 0.7:
        risk_tier = "high"
    elif prob > 0.3:
        risk_tier = "moderate"
    
    # 6. SHAP Explanation
    shap_values = explainer.shap_values(input_array)
    if isinstance(shap_values, list):
        shap_values = shap_values[1] # positive class
    
    explanations = {feature_names[i]: float(shap_values[0][i]) for i in range(len(feature_names))}
    
    return {
        "probability": prob,
        "risk_tier": risk_tier,
        "explanations": explanations,
        "model_type": "PCOS Infertility Analysis"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
