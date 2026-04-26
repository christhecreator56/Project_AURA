# AURA - PCOS Infertility Risk API

AURA is a machine learning project for predicting infertility risk in the context of PCOS using clinical biomarkers.  
It includes scripts for data acquisition, model training, and a FastAPI inference service with SHAP-based feature explanations.

## Project Structure

- `download_data.py` - downloads the PCOS dataset from Kaggle into `data/`
- `train_model.py` - preprocesses data, trains XGBoost, evaluates, and saves artifacts
- `main.py` - FastAPI app that loads artifacts and serves prediction endpoints
- `generate_data.py` - generates synthetic sample data (optional utility)
- `artifacts/` - saved model, imputer, and feature metadata
- `data/` - local dataset storage

## Requirements

- Python 3.9+ recommended
- Kaggle access configured for `kagglehub` (for dataset download)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1) Download dataset

```bash
python download_data.py
```

This fetches the PCOS dataset and copies files into `data/`.

### 2) Train model

```bash
python train_model.py
```

This creates:

- `artifacts/model.pkl`
- `artifacts/imputer.pkl`
- `artifacts/features.pkl`

### 3) Run API

```bash
python main.py
```

The API runs on `http://0.0.0.0:8000`.

## API Endpoints

- `GET /` - health/status check
- `POST /predict` - returns probability, risk tier, and SHAP explanations

Example request body for `POST /predict`:

```json
{
  "I   beta-HCG(mIU/mL)": 45.2,
  "II    beta-HCG(mIU/mL)": 58.7,
  "AMH(ng/mL)": 6.1
}
```

## Notes

- Paths in current scripts are configured for this workspace (`e:/projects/AURA/...`).
- CORS is currently open to all origins in `main.py`.
- If artifacts are missing, `/predict` returns `503 Model not loaded`.